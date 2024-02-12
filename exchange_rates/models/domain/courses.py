from exchange_rates.core.models import OrmBaseModel


class CoursesDTO(OrmBaseModel):
    exchanger: str
    direction: str
    value: float
