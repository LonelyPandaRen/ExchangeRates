from pydantic import BaseModel, ConfigDict


class CoreBaseModel(BaseModel):
    pass


class CoreOrmBaseModel(CoreBaseModel):
    model_config = ConfigDict(from_attributes=True)


class OrmBaseModel(CoreOrmBaseModel):
    pass


class SchemaBaseModel(CoreBaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
