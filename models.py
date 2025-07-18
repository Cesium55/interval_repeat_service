from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Table,
    Date,
    CheckConstraint,
    TIMESTAMP,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LearnStatus(Base):
    """
    0 - REPEATING
    1 - REPEATING BUT FORGOT LAST TIME
    3 - LEARNED
    4 - KNOWN
    """

    __tablename__ = "learn_statuses"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String, unique=True)


class RepeatEntity(Base):
    """class for different entities (words, videos etc)"""

    __tablename__ = "repeat_entities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)


class RepeatEntityInstance(Base):
    """class for storing existing entities"""

    __tablename__ = "repeat_entity_instances"

    entity_type = Column(Integer, ForeignKey("repeat_entities.id"), primary_key=True)
    instance_id = Column(Integer, primary_key=True)


class Group(Base):

    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey("repeat_entities.id"), primary_key=True)
    name = Column(String(1000))
    owner_id = Column(Integer, nullable=True, default=-1)


class GroupInstanceRelation(Base):

    __tablename__ = "group_instance_relations"

    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)
    entity_id = Column(Integer, ForeignKey("repeat_entities.id"), primary_key=True)
    instance_id = Column(Integer, primary_key=True)


class RepeatRelation(Base):
    __tablename__ = "repeat_relations"

    user_id = Column(Integer, primary_key=True)
    entity_type = Column(Integer, ForeignKey("repeat_entities.id"), primary_key=True)
    entity_id = Column(Integer, primary_key=True)

    current_iteration = Column(Integer, default=0)
    last_repeated = Column(TIMESTAMP)
    forgot_times = Column(Integer, default=0)
    learn_status = Column(Integer, default=0)


class UserGroupRelation(Base):
    __tablename__ = "user_group_relations"
    user_id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)
    is_active = Column(Boolean, default=True)
