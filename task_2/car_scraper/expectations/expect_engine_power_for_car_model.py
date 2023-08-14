"""
This is a template for creating custom MulticolumnMapExpectations.
For detailed instructions on how to use it, please see:
    https://docs.greatexpectations.io/docs/guides/expectations/creating_custom_expectations/how_to_create_custom_multicolumn_map_expectations
"""

from typing import Optional

from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.exceptions import InvalidExpectationConfigurationError
from great_expectations.execution_engine import (
    PandasExecutionEngine,
    SparkDFExecutionEngine,
    SqlAlchemyExecutionEngine,
)
from great_expectations.expectations.expectation import MulticolumnMapExpectation
from great_expectations.expectations.metrics.map_metric_provider import (
    MulticolumnMapMetricProvider,
    multicolumn_condition_partial,
)

from ..cars_checker import check_car_engine


# This class defines a Metric to support your Expectation.
# For most MulticolumnMapExpectations, the main business logic for calculation will live in this class.
class MulticolumnValuesEnginePower(MulticolumnMapMetricProvider):
    # This is the id string that will be used to reference your metric.
    condition_metric_name = "multicolumn_values.engine_power"
    # These point your metric at the provided keys to facilitate calculation
    condition_domain_keys = (
        "batch_id",
        "table",
        "column_list",
        "row_condition",
        "condition_parser",
        "ignore_row_if",
    )
    condition_value_keys = ("motors_config",)

    # This method implements the core logic for the PandasExecutionEngine
    @multicolumn_condition_partial(engine=PandasExecutionEngine)
    def _pandas(cls, column_list, motors_config, **kwargs):
        res = column_list.apply(
            axis=1,
            func=lambda car: check_car_engine(
                motors_config=motors_config,
                manufacturer=car["manufacturer_name"],
                model=car["car_model_name"],
                fuel=car["fuel_name"],
                engine_power=car["engine_power"],
            ),
        )
        return res

    # This method defines the business logic for evaluating your metric when using a SqlAlchemyExecutionEngine
    # @multicolumn_condition_partial(engine=SqlAlchemyExecutionEngine)
    # def _sqlalchemy(cls, column_list, **kwargs):
    #     raise NotImplementedError

    # This method defines the business logic for evaluating your metric when using a SparkDFExecutionEngine
    # @multicolumn_condition_partial(engine=SparkDFExecutionEngine)
    # def _spark(cls, column_list, **kwargs):
    #     raise NotImplementedError


# This class defines the Expectation itself
class ExpectEnginePowerForCarModel(MulticolumnMapExpectation):
    """Expect engine power to be realistic based on motors available for a given car model."""

    # These examples will be shown in the public gallery.
    # They will also be executed as unit tests for your Expectation.
    examples = []

    # This is the id string of the Metric used by this Expectation.
    # For most Expectations, it will be the same as the `condition_metric_name` defined in your Metric class above.
    map_metric = "multicolumn_values.engine_power"

    # This is a list of parameter names that can affect whether the Expectation evaluates to True or False
    success_keys = (
        "column_list",
        "mostly",
        "motors_config",
    )

    # This dictionary contains default values for any parameters that should have default values
    default_kwarg_values = {}

    def validate_configuration(
        self, configuration: Optional[ExpectationConfiguration] = None
    ) -> None:
        """
        Validates that a configuration has been set, and sets a configuration if it has yet to be set. Ensures that
        necessary configuration arguments have been provided for the validation of the expectation.

        Args:
            configuration (OPTIONAL[ExpectationConfiguration]): \
                An optional Expectation Configuration entry that will be used to configure the expectation
        Returns:
            None. Raises InvalidExpectationConfigurationError if the config is not validated successfully
        """

        super().validate_configuration(configuration)
        configuration = configuration or self.configuration

    # This object contains metadata for display in the public Gallery
    library_metadata = {
        "tags": [],  # Tags for this Expectation in the Gallery
        "contributors": [  # Github handles for all contributors to this Expectation.
            "@your_name_here",  # Don't forget to add your github handle here!
        ],
    }


if __name__ == "__main__":
    ExpectEnginePowerForCarModel().print_diagnostic_checklist()
