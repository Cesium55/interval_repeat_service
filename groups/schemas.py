from pydantic import BaseModel, Field
from typing import List


class GroupsPOST(BaseModel):
    class GroupPOST(BaseModel):
        name: str = Field(min_length=2, max_length=1000)

    data: List[GroupPOST]


class GroupCreate(BaseModel):
    name: str
    id: int
    entity_id: int
    owner_id: int = -1


class BrokerGroupCreate(BaseModel):
    name: str
    id: int
    entity_name: str
    owner_id: int = -1


class GroupsCreate(BaseModel):
    data: List[GroupCreate]


class GroupsModel(BaseModel):
    id: int
    name: str
    owner_id: int


class GroupDelete(BaseModel):
    id: int


class GroupRead(BaseModel):
    id: int
    name: str
    owner_id: int
