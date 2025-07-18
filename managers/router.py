from fastapi import APIRouter
from managers.service import BaseServiceSchema
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List


class BaseModelAPIRouter(APIRouter):

    schemas: BaseServiceSchema

    def __init__(
        self,
        schemas: BaseServiceSchema,
        *,
        prefix="",
        tags=None,
        dependencies=None,
        default_response_class=...,
        responses=None,
        callbacks=None,
        routes=None,
        redirect_slashes=True,
        default=None,
        dependency_overrides_provider=None,
        route_class=...,
        on_startup=None,
        on_shutdown=None,
        lifespan=None,
        deprecated=None,
        include_in_schema=True,
        generate_unique_id_function=...,
    ):
        super().__init__(
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default,
            dependency_overrides_provider=dependency_overrides_provider,
            route_class=route_class,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            lifespan=lifespan,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            generate_unique_id_function=generate_unique_id_function,
        )

        self.schemas = schemas
