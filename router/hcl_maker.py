import os
from pydantic import BaseModel
from fastapi import APIRouter
from function.hcl import create_hcl, terraform_apply, terraform_destroy

router = APIRouter(prefix="/ec2_instance", tags=["EC2"])


class User(BaseModel):
    user_id: str
    seq: str
    templete_id: str


class DeleteUser(BaseModel):
    user_id: str
    seq: str


@router.post("/", status_code=201)
async def create_ec2_instance(user_config: User) -> dict:
    user_config_dict = user_config.dict()
    output_path = create_hcl(user_config_dict)  # hcl 생성
    output_message = await terraform_apply(output_path)

    return {"message": output_message}


@router.delete("/")
async def destroy_ec2_instance(delete_user_config: DeleteUser) -> dict:
    user_info = delete_user_config.dict()
    work_dir = os.path.join(os.getcwd(), user_info["user_id"], user_info["seq"])
    output_message = await terraform_destroy(work_dir)
    return {"message": output_message}
