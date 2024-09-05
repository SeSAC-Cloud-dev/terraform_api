from fastapi import APIRouter
from fastapi.responses import JSONResponse
from function.yaml import update_yaml


router = APIRouter(prefix="/yaml", tags=["Version control"])


@router.put("/")
async def update_yaml(tag_name: str):
    result = update_yaml(tag_name)
    return JSONResponse(content={"message": result}, status_code=200)
