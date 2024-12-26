from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.service import create_map

router = APIRouter(tags=["root"])


@router.get("/", response_class=HTMLResponse)
async def root() -> HTMLResponse:
    map_object = create_map()
    map_object.save("map.html")

    with open("map.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    return HTMLResponse(content=html_content)
