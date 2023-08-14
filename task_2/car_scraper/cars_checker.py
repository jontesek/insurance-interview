from typing import Optional
import pathlib
import json

import yaml


# Load data
def load_cars(file_path):
    models = set()
    with open(file_path) as f:
        cars = []
        for line in f:
            obj = json.loads(line)
            if (model := obj["car_model_name"]) not in models:
                models.add(model)
            cars.append(obj)
    return cars


# Load motors config
def load_motors():
    file_name = "config/car_motors.yaml"
    file_path = pathlib.Path(__file__).resolve().parent / file_name

    with open(file_path) as f:
        return yaml.safe_load(f)


# Check engine power by car model
def check_car_engine(
    motors_config: dict,
    manufacturer: str,
    model: str,
    fuel: str,
    engine_power: int,
    car_id=None,
) -> Optional[bool]:
    motor = motors_config["manufacturers"][manufacturer]
    if not model in motor["models"]:
        # print(f"missing model {model} in motor config")
        return False
    motor = motor["models"][model]
    if fuel not in motor:
        # print("missing fuel name: ", fuel_name)
        return False
    motor = motor[fuel]
    if engine_power < motor["lowest_kw"] or engine_power > motor["highest_kw"]:
        print(model, motor)
        print("car power is not in range: ", car_id, engine_power)
        return False
    return True


# Run something
if __name__ == "__main__":
    file_name = "../data/cars_skoda_2000.jsonl"
    file_path = pathlib.Path(__file__).resolve().parent / file_name

    cars = load_cars(file_path)
    motors_config = load_motors()

    for car in cars:
        result = check_car_engine(
            motors_config=motors_config,
            car_id=car["id"],
            manufacturer=car["manufacturer_name"],
            model=car["car_model_name"],
            fuel=car["fuel_name"],
            engine_power=car["engine_power"],
        )
