import datetime
import time
import pathlib

import structlog
from request_session import RequestSession

from .logs import get_logger
from .models import Car, DATE_FORMAT, DATETIME_FORMAT
from .errors import TooHighOffsetError, SearchCarsApiError, SearchUntilDatetimeEnd
from .cars_saver import FileSaver, CarsSaver


SEARCH_LIMIT = 20
SEARCH_URL = "https://www.sauto.cz/api/v1/items/search?limit={limit}&offset={offset}&manufacturer_model_seo={manufacturer}&condition_seo=nove,ojete,predvadeci&category_id=838&operating_lease=false&timestamp_to={timestamp_to}"
CAR_URL = "https://www.sauto.cz/api/v1/items/{item_id}"
WAIT_TIME = 1


class CarsProvider:

    def __init__(self, http_client: RequestSession, logger: structlog.stdlib.BoundLogger) -> None:
        self._http_client = http_client
        self.log = logger.bind(logger_name="cars_provider")

    def save_all_cars(self, manufacturer: str, search_until_datetime: datetime.datetime, cars_saver: CarsSaver):
        self.log = self.log.bind(manufacturer=manufacturer, search_until_datetime=str(search_until_datetime))
        self.log.info("save_all_cars.start")
        _start_ts = int(time.time()) 
        search_result = self.search_cars_by_offset(limit=SEARCH_LIMIT, offset=0, manufacturer=manufacturer, timestamp_to=_start_ts, search_until_datetime=search_until_datetime)
        self.log.info("save_all_cars.first_searc_done", total=search_result["total"], new_offset=search_result["new_offset"])
        search_count = int(search_result["total"] / SEARCH_LIMIT) + 1
        for i in range(1, search_count+1):
            try:
                self.log.info("save_all_cars.next_search", search_number=i, total=search_result["total"], offset=search_result["new_offset"])
                search_result = self.search_cars_by_offset(limit=SEARCH_LIMIT, offset=search_result["new_offset"], manufacturer=manufacturer, timestamp_to=_start_ts, search_until_datetime=search_until_datetime)   
                cars_saver.save_cars(search_result["cars"])
                time.sleep(WAIT_TIME)
            except (TooHighOffsetError, SearchUntilDatetimeEnd) as e:
                self.log.warning("save_all_cars.end", exception=str(e))
                break
        cars_saver.on_end()

    def search_cars_by_offset(self, limit: int, offset: int, manufacturer: str, timestamp_to: int, search_until_datetime: datetime.datetime) -> dict:
        url = SEARCH_URL.format(limit=limit, offset=offset, manufacturer=manufacturer, timestamp_to=timestamp_to)
        response = self._http_client.get(url)
        response = response.json()
        # Check response
        if (status_code := response["status_code"]) != 200:
            if status_code == 422:  
                raise TooHighOffset
            raise SearchCarsApiError(response["status_message"])
        # Process results
        cars = []
        for item in response["results"]:
            try:
                car = self.get_car(item["id"])
                self.log.info("search_cars_by_offset.got_car", car_id=item["id"], edit_date=str(car.edit_date))
                if car.edit_date <= search_until_datetime:
                    self.log.warning("search_cars_by_offset.end_by_date",search_until_datetime=search_until_datetime)
                    raise SearchUntilDatetimeEnd
                cars.append(car)
            except ValueError:
                self.log.exception(f"Problem with getting car {item['id']}")
        # Prepare result
        pagination = response["pagination"]
        return {
            "new_offset": pagination["offset"] + pagination["limit"],
            "total": response["pagination"]["total"],
            "cars": cars,
        }

    def get_car(self, car_id: int) -> Car:
        self.log.info("get_car.start", car_id=car_id)
        url = CAR_URL.format(item_id=car_id)
        response = self._http_client.get(url)
        response = response.json()
        if response["status_code"] != 200:
            raise ValueError(response["status_message"])
        result = response["result"]
        result = self._validate_car_result(result)
        return self._create_car_obj(result)

    @staticmethod
    def _validate_car_result(result: dict) -> dict:
        # Need to know how old the car is
        if not result.get("manufacturing_date") and not result.get("in_operation_date"):
            raise ValueError("Missing car date")
        # Need to know whether car is sedan or combi
        if not result.get("doors") and not result.get("vehicle_body_cb"):
            raise ValueError("Missing car body type")
        # Don't save info about doors if there is zero
        if "doors" in result and result["doors"] == 0:
            result["doors"] = None
        # Need to know these fields
        mandatory_fields = ("gearbox_cb", "engine_power", "engine_volume")
        for field in mandatory_fields:
            if not result.get(field):
                raise ValueError(f"Missing field: {field}")

        return result
    
    @staticmethod
    def _create_car_obj(result: dict) -> Car:
        # Handle optional nested parameters
        air_cond = result.get("aircondition_cb")
        color = result.get("color_cb")
        premise = result.get("premise")
        vehicle_body = result.get("vehicle_body_cb")
        # Handle dates
        create_date = datetime.datetime.strptime(result["create_date"], DATETIME_FORMAT)
        edit_date = datetime.datetime.strptime(result["edit_date"], DATETIME_FORMAT)
        in_operation_date = datetime.datetime.strptime(result["in_operation_date"], DATE_FORMAT) if result.get("in_operation_date") else None
        manufacturing_date = datetime.datetime.strptime(result["manufacturing_date"], DATE_FORMAT) if result.get("manufacturing_date") else None
        # Create object
        return Car(
            id=result["id"],
            additional_model_name=result.get("additional_model_name"),
            airbags=result.get("airbags"),
            air_conditioning_name=air_cond["name"] if air_cond else None,
            air_conditioning_value=air_cond["value"] if air_cond else None,
            capacity=result.get("capacity"),
            category_id=result["category"]["id"],
            category_name=result["category"]["name"], 
            color_name=color["name"] if color else None,
            color_value=color["value"] if color else None,
            condition_name=result["condition_cb"]["name"],
            condition_value=result["condition_cb"]["value"],
            country_of_origin_name=result["country_of_origin_cb"]["name"],
            country_of_origin_value=result["country_of_origin_cb"]["value"],
            create_date=create_date,
            doors=result.get("doors"),
            edit_date=edit_date,
            engine_power=result["engine_power"],
            engine_volume=result["engine_volume"],
            first_owner=result.get("first_owner"),
            fuel_name=result["fuel_cb"]["name"],
            fuel_value=result["fuel_cb"]["value"],
            gearbox_name=result["gearbox_cb"]["name"],
            gearbox_value=result["gearbox_cb"]["value"],
            gearbox_levels=result["gearbox_levels_cb"]["value"] if result.get("gearbox_levels_cb") else None,
            in_operation_date=in_operation_date,
            locality_district_name=result["locality"]["district"],
            manufacturer_name=result["manufacturer_cb"]["name"],
            manufacturer_value=result["manufacturer_cb"]["value"],
            manufacturing_date=manufacturing_date,
            car_model_name=result["model_cb"]["name"],
            car_model_value=result["model_cb"]["value"],
            name=result["name"],
            premise_id=premise["id"] if premise else None,
            premise_name=premise["name"] if premise else None,
            price=result["price"],
            status=result["status"],
            tachometer=result["tachometer"],
            vehicle_body_name=vehicle_body["name"] if vehicle_body else None,
            vehicle_body_value=vehicle_body["value"] if vehicle_body else None,
        )


if __name__ == "__main__":
    example_search_url = "https://www.sauto.cz/api/v1/items/search?limit=20&offset=0&manufacturer_model_seo=skoda&condition_seo=nove,ojete,predvadeci&category_id=838&operating_lease=false&timestamp_to=1691754272"
    example_item_url = "https://www.sauto.cz/api/v1/items/195001372"

    logger = get_logger(True, "cars_provider")
    http_client = RequestSession(
        raise_for_status=True,
        max_retries=2,
        request_category="general",
        logger=logger,
    )

    # http_client.get("http://httpbin.org/status/500")
    # exit()

    provider = CarsProvider(http_client, logger)

    car = provider.get_car(195001372)
    print(car)
    # search_until = datetime.datetime(2023,8,12,12,4,0)
    # timestamp_to = 1691838653
    # result = provider.search_cars_by_offset(limit=20, offset=20, manufacturer="skoda", timestamp_to=timestamp_to, search_until_datetime=search_until)
    # for r in result["cars"]:
    #     print("====")
    #     print(r.model_dump_json())

    # saving
    cars_file_path = pathlib.Path(__file__).resolve().parent / "../data/cars.jsonl"
    saver = FileSaver(logger, cars_file_path)
    search_until = datetime.datetime(2023,8,13,12,4,0)
    provider.save_all_cars(manufacturer="skoda", search_until_datetime=search_until, cars_saver=saver)
