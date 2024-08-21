import os
from fastapi import APIRouter
from function.hcl import create_hcl, terraform_apply, terraform_destroy

router = APIRouter(prefix="/hcl", tags=["hcl"])


@router.post("/apply", status_code=201)
async def create_vd(
    user_id: str,
    seq: str,
    ami_id: str,
    instance_type: str,
    subnet_id: str,
    tag_name: str,
) -> dict:
    user_config = {
        "user_id": user_id,
        "seq": seq,
        "ami_id": ami_id,
        "instance_type": instance_type,
        "subnet_id": subnet_id,
        "tag_name": tag_name,
    }

    output_path = create_hcl(user_config)  # hcl 생성
    output_message = terraform_apply(output_path)

    return {"message": output_message}


@router.delete("/destroy")
async def destroy_vd(
    user_id: str,
    seq: str,
) -> dict:
    work_dir = os.path.join(os.getcwd(), user_id, seq)
    output_message = terraform_destroy(work_dir)
    return {"message": output_message}
