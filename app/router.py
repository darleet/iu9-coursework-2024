import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.schemas import JSONResponseSchema, RouteRequestSchema, RouteResponseSchema
from app.service import check_route

logger = logging.getLogger(__name__)
router = APIRouter(tags=["root"])


@router.post("/route", response_class=JSONResponse)
async def root(route: RouteRequestSchema) -> dict:
    try:
        ice_probabilities, visibility_scores = await check_route(route.coordinates)
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error"
        ) from e

    json_data = JSONResponseSchema(
        data=RouteResponseSchema(
            ice_probabilities=ice_probabilities, visibility_scores=visibility_scores
        )
    )
    return json_data.dict()
