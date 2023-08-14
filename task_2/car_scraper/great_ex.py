import great_expectations as gx
import yaml

from .cars_checker import load_motors
from .expectations.expect_engine_power_for_car_model import ExpectEnginePowerForCarModel


def process_file(file_path: str):
    context = gx.get_context()
    validator = context.sources.pandas_default.read_json(file_path, lines=True)

    # Create basic expectations
    validator.expect_column_values_to_not_be_null("create_date")
    validator.expect_column_values_to_be_between("capacity", auto=True)

    # Create a custom expectation about engine power
    motors_config = load_motors()
    column_list = ["manufacturer_name", "fuel_name", "car_model_name", "engine_power"]
    validator.expect_engine_power_for_car_model(column_list=column_list, motors_config=motors_config)

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
