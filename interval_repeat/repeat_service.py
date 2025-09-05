from sqlalchemy import and_, select, insert, update, delete, not_, exists, func
from sqlalchemy.ext.asyncio import AsyncSession
from models import (
    Group,
    RepeatEntity,
    UserGroupRelation,
    RepeatEntityInstance,
    GroupInstanceRelation,
    RepeatRelation,
)
from . import schemas
from repeat_entities.manager import RepeatEntityManager
from datetime import datetime, timedelta

re_manager = RepeatEntityManager()


LEARN_STATUSES = {
    "REPEATING": 0,
    "FORGOT_LAST_TIME": 1,
    "LEARNED": 3,
    "KNOWN": 4,
}

REPEAT_INTERVALS = {
    0: timedelta(minutes=30),
    1: timedelta(hours=2),
    2: timedelta(hours=12),
    3: timedelta(days=3),
    4: timedelta(weeks=2),
    5: timedelta(days=45),
}


class RepeatService:

    def __init__(self):
        self.statuses = LEARN_STATUSES
        self.intervals = REPEAT_INTERVALS

    async def get_entities_to_learn_by_entity_name(
        self, session: AsyncSession, user_id: int, entity_type: str
    ):
        entity_id = (await re_manager.get_mapping(session)).get(entity_type)
        return await self.get_entities_to_learn(session, user_id, entity_id)

    async def get_entities_to_learn(
        self, session: AsyncSession, user_id: int, entity_id: int, limit=10
    ):
        rei = RepeatEntityInstance
        gir = GroupInstanceRelation
        ugr = UserGroupRelation
        rr = RepeatRelation

        # Подзапрос: выбрать instance_id из групп, на которые подписан пользователь
        group_instances_subq = (
            select(gir.instance_id)
            .join(
                ugr,
                and_(
                    ugr.group_id == gir.group_id,
                    ugr.entity_id == gir.entity_id,
                    ugr.user_id == user_id,
                ),
            )
            .where(gir.entity_id == entity_id)
            .subquery()
        )

        # EXISTS подзапрос: проверить, что сущность не изучалась
        repeat_exists_subq = select(rr.instance_id).where(
            and_(
                rr.user_id == user_id,
                rr.entity_type == entity_id,
                rr.instance_id == rei.instance_id,
            )
        )

        # Основной запрос
        stmt = (
            select(rei)
            .where(
                rei.entity_type == entity_id,
                rei.instance_id.in_(select(group_instances_subq.c.instance_id)),
                not_(exists(repeat_exists_subq)),
            )
            .order_by(func.random())
            .limit(limit)
        )

        result = await session.execute(stmt)
        return result.scalars().all()

    def get_next_repeat_time(self, iteration: int) -> datetime:
        """Рассчитать next_repeat_time по iteration (ограничено макс. ключом словаря)"""
        now = datetime.utcnow()
        interval = self.intervals.get(min(iteration, max(self.intervals)), timedelta())
        return now + interval

    async def start_learning(
        self, session: AsyncSession, user_id: int, entity_id: int, instance_id: int
    ):
        """Создание новой записи для изучения"""
        now = datetime.utcnow()
        next_repeat_time = self.get_next_repeat_time(0)

        stmt = insert(RepeatRelation).values(
            user_id=user_id,
            entity_type=entity_id,
            instance_id=instance_id,
            current_iteration=0,
            last_repeated=now,
            next_repeat_time=next_repeat_time,
            forgot_times=0,
            learn_status=self.statuses["REPEATING"],
        )

        result = await session.execute(stmt)
        return result

    async def repeat(
        self, session: AsyncSession, user_id: int, entity_id: int, instance_id: int
    ):
        """Повторение слова: увеличить счётчик, обновить статус и время"""
        stmt = select(RepeatRelation).where(
            RepeatRelation.user_id == user_id,
            RepeatRelation.entity_type == entity_id,
            RepeatRelation.instance_id == instance_id,
        )

        result = await session.execute(stmt)
        relation = result.scalar_one_or_none()

        if not relation:
            return  # нет записи — нечего повторять

        new_iteration = min(relation.current_iteration + 1, 6)
        now = datetime.utcnow()

        new_status = (
            self.statuses["LEARNED"]
            if new_iteration == 6
            else self.statuses["REPEATING"]
        )
        next_repeat_time = (
            now
            if new_status == self.statuses["LEARNED"]
            else self.get_next_repeat_time(new_iteration)
        )

        stmt = (
            update(RepeatRelation)
            .where(
                RepeatRelation.user_id == user_id,
                RepeatRelation.entity_type == entity_id,
                RepeatRelation.instance_id == instance_id,
            )
            .values(
                current_iteration=new_iteration,
                learn_status=new_status,
                last_repeated=now,
                next_repeat_time=next_repeat_time,
            )
        ).returning(RepeatRelation)

        result = await session.execute(stmt)
        return result.scalar_one()

    async def mark_as_known(
        self, session: AsyncSession, user_id: int, entity_id: int, instance_id: int
    ):
        """Отметить слово как уже известное"""
        now = datetime.utcnow()

        stmt = (
            insert(RepeatRelation)
            .values(
                user_id=user_id,
                entity_type=entity_id,
                instance_id=instance_id,
                current_iteration=6,
                last_repeated=now,
                next_repeat_time=now,
                forgot_times=0,
                learn_status=self.statuses["KNOWN"],
            )
            .returning(RepeatRelation)
        )
        # .on_conflict_do_update(
        #     index_elements=["user_id", "entity_type", "instance_id"],
        #     set_={
        #         "current_iteration": 6,
        #         "last_repeated": now,
        #         "next_repeat_time": now,
        #         "learn_status": self.statuses["KNOWN"]
        #     }
        # )

        result = (await session.execute(stmt)).scalar_one()

        return result

    async def forget(
        self, session: AsyncSession, user_id: int, entity_id: int, instance_id: int
    ):
        """Забывание слова: откатить прогресс, увеличить счётчик забываний"""
        stmt = select(RepeatRelation).where(
            RepeatRelation.user_id == user_id,
            RepeatRelation.entity_type == entity_id,
            RepeatRelation.instance_id == instance_id,
        )

        result = await session.execute(stmt)
        relation = result.scalar_one_or_none()

        if not relation:
            return  # нечего забывать

        old_iteration = relation.current_iteration
        new_iteration = max(old_iteration - 1, 0) if old_iteration <= 3 else 3
        now = datetime.utcnow()

        stmt = (
            update(RepeatRelation)
            .where(
                RepeatRelation.user_id == user_id,
                RepeatRelation.entity_type == entity_id,
                RepeatRelation.instance_id == instance_id,
            )
            .values(
                current_iteration=new_iteration,
                learn_status=self.statuses["FORGOT_LAST_TIME"],
                forgot_times=relation.forgot_times + 1,
                last_repeated=now,
                next_repeat_time=self.get_next_repeat_time(new_iteration),
            )
        )

        result = await session.execute(stmt)
        return result

    async def get_all_in_progress(
        self, session: AsyncSession, user_id: int, entity_id: int
    ):
        """1) Все сущности со статусами REPEATING и FORGOT_LAST_TIME"""
        stmt = select(RepeatRelation).where(
            RepeatRelation.user_id == user_id,
            RepeatRelation.entity_type == entity_id,
            RepeatRelation.learn_status.in_(
                [LEARN_STATUSES["REPEATING"], LEARN_STATUSES["FORGOT_LAST_TIME"]]
            ),
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_repeating_only(
        self, session: AsyncSession, user_id: int, entity_id: int
    ):
        """2) Только REPEATING"""
        stmt = select(RepeatRelation).where(
            RepeatRelation.user_id == user_id,
            RepeatRelation.entity_type == entity_id,
            RepeatRelation.learn_status == LEARN_STATUSES["REPEATING"],
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_forgot_only(
        self, session: AsyncSession, user_id: int, entity_id: int
    ):
        """3) Только FORGOT_LAST_TIME"""
        stmt = select(RepeatRelation).where(
            RepeatRelation.user_id == user_id,
            RepeatRelation.entity_type == entity_id,
            RepeatRelation.learn_status == LEARN_STATUSES["FORGOT_LAST_TIME"],
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_learned(self, session: AsyncSession, user_id: int, entity_id: int):
        """4) Сущности со статусом LEARNED"""
        stmt = select(RepeatRelation).where(
            RepeatRelation.user_id == user_id,
            RepeatRelation.entity_type == entity_id,
            RepeatRelation.learn_status == LEARN_STATUSES["LEARNED"],
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_known(self, session: AsyncSession, user_id: int, entity_id: int):
        """5) Уже известные сущности (KNOWN)"""
        stmt = select(RepeatRelation).where(
            RepeatRelation.user_id == user_id,
            RepeatRelation.entity_type == entity_id,
            RepeatRelation.learn_status == LEARN_STATUSES["KNOWN"],
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_due_for_repeat(
        self, session: AsyncSession, user_id: int, entity_id: int
    ):
        """6) REPEATING или FORGOT_LAST_TIME и next_repeat_time < now"""
        now = datetime.utcnow()
        stmt = (
            select(RepeatRelation)
            .where(
                and_(
                    RepeatRelation.user_id == user_id,
                    RepeatRelation.entity_type == entity_id,
                    RepeatRelation.learn_status.in_(
                        [
                            LEARN_STATUSES["REPEATING"],
                            LEARN_STATUSES["FORGOT_LAST_TIME"],
                        ]
                    ),
                    RepeatRelation.next_repeat_time <= now,
                )
            )
            .order_by(func.random())
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_stats(self, session: AsyncSession, user_id: int):
        query = select(RepeatRelation)
        db_result = await session.execute(query)
        return db_result.scalars().all()

    async def get_next_repeat_relation(
        self, session: AsyncSession, user_id: int, entity_id: int
    ):
        now = datetime.utcnow()
        stmt = (
            select(RepeatRelation)
            .where(
                and_(
                    RepeatRelation.user_id == user_id,
                    RepeatRelation.entity_type == entity_id,
                    RepeatRelation.learn_status.in_(
                        (
                            LEARN_STATUSES["REPEATING"],
                            LEARN_STATUSES["FORGOT_LAST_TIME"],
                        )
                    ),
                )
            )
            .order_by(RepeatRelation.next_repeat_time)
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_repeat_relation_or_none(
        self, session: AsyncSession, user_id: int, entity_id: int, instance_id: int
    ):
        query = select(RepeatRelation).where(
            and_(
                RepeatRelation.user_id == user_id,
                RepeatRelation.entity_type == entity_id,
                RepeatRelation.instance_id == instance_id,
            )
        )
        db_response = await session.execute(query)
        return db_response.scalar_one_or_none()
