from fastapi import APIRouter, Depends
from database import get_async_session, AsyncSession
from managers.AuthManager.AuthManager import user_required
from .manager import IntervalRepeatManager
from pydantic import BaseModel
from . import schemas

ir_manager = IntervalRepeatManager()


class BaseDeps:
    def __init__(
        self,
        user: dict = Depends(user_required),
        session: AsyncSession = Depends(get_async_session),
    ):
        self.user = user
        self.session = session


router = APIRouter(prefix="/ir")


@router.get("/groups")
async def get_groups_info(deps: BaseDeps = Depends()):
    result = await ir_manager.get_user_subscribed_groups(
        deps.session, deps.user.get("id")
    )

    return {"data": result}


@router.post("/groups/subscribe")
async def subscribe_group(group: schemas.GroupFind, deps: BaseDeps = Depends()):
    result = await ir_manager.subscribe(deps.session, deps.user.get("id"), group)
    return result


@router.delete("/groups/subscribe")
async def unsubscribe_group(group: schemas.GroupFind, deps: BaseDeps = Depends()):
    result = await ir_manager.unsubscribe(deps.session, deps.user.get("id"), group)
    return result


@router.get("/instances-to-learn/{entity_type}")
async def get_new_instances(
    entity_type: str,
    deps: BaseDeps = Depends(),
):
    data = await ir_manager.get_instances_to_learn(
        deps.session, deps.user.get("id"), entity_type
    )
    return {"data": data}


@router.get("/instances-to-repeat/{entity_type}")
async def get_repeat_instances(entity_type: str, deps: BaseDeps = Depends()):
    result = await ir_manager.get_instances_to_repeat(
        deps.session, deps.user.get("id"), entity_type
    )
    return {"data": result}


@router.post("/already-know")
async def already_know(instance: schemas.RepeatInstance, deps: BaseDeps = Depends()):
    data = await ir_manager.mark_as_known(
        deps.session, deps.user.get("id"), instance.entity_type, instance.instance_id
    )
    return {"data": data}


@router.post("/learn")
async def start_learning(instance: schemas.RepeatInstance, deps: BaseDeps = Depends()):
    result = await ir_manager.start_learning(
        deps.session, deps.user.get("id"), instance.entity_type, instance.instance_id
    )
    return {"data": result}


@router.put("/repeat")
async def repeat(
    instance: schemas.RepeatInstanceWithStatus, deps: BaseDeps = Depends()
):
    if instance.remembered_status:
        data = await ir_manager.repeat(
            deps.session,
            deps.user.get("id"),
            instance.entity_type,
            instance.instance_id,
        )
    else:
        data = await ir_manager.forget(
            deps.session,
            deps.user.get("id"),
            instance.entity_type,
            instance.instance_id,
        )
    return {"data": data}


@router.get("/instances")
async def get_all_repeat_instances(): ...


@router.get("/instances/repeating_good")
async def get_all_repeat_instances_currently_in_repeat_and_not_problem(): ...


@router.get("/instances/repeating")
async def get_all_repeat_instances_currently_in_repeat(): ...


@router.get("/instances/problem")
async def get_all_repeat_instances_forgotten_last_time(): ...


@router.get("/instances/learned")
async def get_all_repeat_instances_learned(): ...


@router.get("/instances/known")
async def get_all_repeat_instances_known(): ...


@router.get("/instances/by-ids")
async def get_repeat_instances_by_ids(): ...


@router.get("/stats")
async def get_stats(deps: BaseDeps = Depends()):
    data = await ir_manager.get_stats(deps.session, deps.user.get("id"))
    return {"data": data}


@router.get("/get-next-repeat-relation/{entity_type}")
async def get_stats(entity_type: str, deps: BaseDeps = Depends()):
    data = await ir_manager.get_next_repeat_relation(
        deps.session, deps.user.get("id"), entity_type
    )
    return {"data": data}
