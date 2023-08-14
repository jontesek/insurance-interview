import datetime
from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, NonNegativeInt, PositiveInt, conint

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class Car(BaseModel):
    id: int
    additional_model_name: Optional[str]
    airbags: Optional[NonNegativeInt]
    air_conditioning_name: Optional[str]
    air_conditioning_value: Optional[NonNegativeInt]
    capacity: Optional[conint(ge=1, le=100)]
    category_id: NonNegativeInt
    category_name: str
    color_name: Optional[str]
    color_value: Optional[NonNegativeInt]
    condition_name: str
    condition_value: NonNegativeInt
    country_of_origin_name: str
    country_of_origin_value: NonNegativeInt
    create_date: datetime.datetime
    doors: Optional[conint(ge=1, le=10)]
    edit_date: datetime.datetime
    engine_power: conint(ge=1, le=2_000)
    engine_volume: conint(ge=1, le=20_000)
    first_owner: Optional[bool]
    fuel_name: str
    fuel_value: NonNegativeInt
    gearbox_name: str
    gearbox_value: NonNegativeInt
    gearbox_levels: Optional[conint(ge=1, le=20)]
    in_operation_date: Optional[datetime.date]
    locality_district_name: str
    manufacturer_name: str
    manufacturer_value: NonNegativeInt
    manufacturing_date: Optional[datetime.date]
    car_model_name: str
    car_model_value: NonNegativeInt
    name: str
    premise_name: Optional[str]
    premise_id: Optional[NonNegativeInt]
    price: conint(ge=1, le=50_000_000)
    status: str
    tachometer: conint(ge=0, le=1_000_000)
    vehicle_body_name: Optional[str]
    vehicle_body_value: Optional[NonNegativeInt]
