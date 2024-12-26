from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas import (
    JSONErrorSchema,
    JSONResponseSchema,
    RouteRequestSchema,
    RouteResponseSchema,
)
from app.service import check_route

router = APIRouter(tags=["root"])


@router.post("/route", response_class=JSONResponse)
async def root(route: RouteRequestSchema) -> dict:
    try:
        ice_probabilities, visibility_scores = await check_route(route.coordinates)
    except Exception as e:
        return JSONErrorSchema(status="internal_server_error", reason=str(e)).dict()

    json_data = JSONResponseSchema(
        data=RouteResponseSchema(
            ice_probabilities=ice_probabilities, visibility_scores=visibility_scores
        )
    )
    return json_data.dict()
