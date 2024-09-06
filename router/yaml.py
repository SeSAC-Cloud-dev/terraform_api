from fastapi import APIRouter
from function.yaml import update_yaml


router = APIRouter(prefix="/yaml", tags=["Version control"])


@router.put("/")
async def yaml_result(tag_name: str):
    result = await update_yaml(tag_name)
    return {"message": result}
