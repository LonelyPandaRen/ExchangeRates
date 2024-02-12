from exchange_rates.core.models import SchemaBaseModel


class CoursesSchema(SchemaBaseModel):
    exchanger: str
    direction: str
    value: float
