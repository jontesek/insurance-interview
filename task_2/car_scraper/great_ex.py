import great_expectations as gx
import yaml

from .cars_checker import load_motors
from .expectations.expect_engine_power_for_car_model import ExpectEnginePowerForCarModel


def process_file(file_path: str):
    context = gx.get_context()
    validator = context.sources.pandas_default.read_json(file_path, lines=True)

    # These data must be filled
    NOT_NULL_COLUMNS = (
        "id",
        "condition_name",
        "country_of_origin_name",
        "create_date",
        "edit_date",
        "gearbox_name",
        "manufacturer_name",
        "car_model_name",
        "name",
    )
    for x in NOT_NULL_COLUMNS:
        validator.expect_column_values_to_not_be_null(x)

    # Check for numbers
    validator.expect_column_values_to_be_between("capacity", 1, 10)
    validator.expect_column_values_to_be_between("doors", 2, 5)
    validator.expect_column_values_to_be_between("engine_power", 20, 1000)
    validator.expect_column_values_to_be_between("engine_volume", 500, 10_000)
    validator.expect_column_values_to_be_between("price", 1_000, 5_000_000)
    validator.expect_column_values_to_be_between("tachometer", 0, 1_000_000)

    # Check for enums
    FUEL_NAMES = [
        "Benzín",
        "Nafta",
        "CNG + benzín",
        "LPG + benzín",
        "Elektro",
        "Hybridní",
        "Ethanol",
    ]
    validator.expect_column_values_to_be_in_set("fuel_name", FUEL_NAMES)

    # Create a custom expectation about engine power
    motors_config = load_motors()
    column_list = ["manufacturer_name", "fuel_name", "car_model_name", "engine_power"]
    validator.expect_engine_power_for_car_model(
        column_list=column_list, motors_config=motors_config
    )

    # Save expectations
    validator.save_expectation_suite()
    # Validate data
    checkpoint = context.add_or_update_checkpoint(
        name="my_quickstart_checkpoint",
        validator=validator,
    )
    checkpoint_result = checkpoint.run()
    # Show result in browser
    context.view_validation_result(checkpoint_result)
