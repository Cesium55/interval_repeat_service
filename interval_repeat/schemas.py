from pydantic import BaseModel


class GroupGet(BaseModel):
    id: int
    entity_id: int


class GroupFind(BaseModel):
    id: int
    entity_type: str


class EntityByName(BaseModel):
    entity_type: str


class RepeatInstance(BaseModel):
    entity_type: str
    instance_id: int


class RepeatInstanceWithStatus(BaseModel):
    entity_type: str
    instance_id: int
    remembered_status: bool
