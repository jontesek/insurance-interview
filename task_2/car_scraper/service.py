import datetime
import os

from request_session import RequestSession

from .logs import get_logger
from .cars_provider import CarsProvider
from .cars_saver import FileSaver, DbSaver


class Service:
    def __init__(self, is_debug: bool) -> None:
        self._logger = get_logger(is_debug, "cars_service")
        self._http_client = RequestSession(
            raise_for_status=True,
            max_retries=2,
            request_category="general",
            logger=self._logger,
        )

    def get_cars_provider(self) -> CarsProvider:
        return CarsProvider(self._http_client, self._logger)

    def save_cars_to_file(
        self, manufacturer: str, search_until_datetime: datetime, dir_path: str, file_name: str = None
    ) -> None:
        file_name = file_name or f"cars_{manufacturer}_{str(search_until_datetime)}.jsonl"
        file_path = os.path.join(dir_path, file_name)
        self._logger.info("save_cars_to_file.start", file_path=file_path)
        saver = FileSaver(self._logger, file_path)
        provider = self.get_cars_provider()
        provider.save_all_cars(
            manufacturer=manufacturer,
            search_until_datetime=search_until_datetime,
            cars_saver=saver,
        )

    def save_cars_to_db(
        self,
        manufacturer: str,
        search_until_datetime: datetime,
        db_connection_string: str,
    ) -> None:
        saver = DbSaver(self._logger, db_connection_string)
        provider = self.get_cars_provider()
        provider.save_all_cars(
            manufacturer=manufacturer,
            search_until_datetime=search_until_datetime,
            cars_saver=saver,
        )
