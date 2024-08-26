import re
import os
import asyncio
from typing import List


def remove_ansi_escape_sequences(text: str) -> str:
    # ANSI escape sequences 패턴
    ansi_escape_pattern = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
    text = ansi_escape_pattern.sub("", text)
    # 개행 문자 제거
    text = text.replace("\n", " ")
    # 필요시 중복된 공백 제거
    plain_text = re.sub(" +", " ", text).strip()
    return plain_text


def create_hcl(user_config: dict) -> str:
    terraform_config = f"""
    terraform {{
        required_providers {{
            aws = {{
                source  = "hashicorp/aws"
                version = "~> 5.0"
            }}
        }}
    }}

    provider "aws" {{
        region = "ap-northeast-2"
    }}

    # EC2 설정 
    resource "aws_instance" "EC2" {{
        launch_template {{
            id      = "{user_config['template_id']}"  # 사용하려는 Launch Template ID
            version = "$Latest"  # 최신 버전 사용, 특정 버전을 사용하려면 버전 번호를 지정
        }}
        tags = {{
            Name = "{user_config['user_id']+'_'+user_config['seq']}"
        }}
    }}

    output "instance_private_ip" {{
        value = jsonencode({{private_ip = aws_instance.EC2.private_ip}})
    }}
    """

    output_path = os.path.join(os.getcwd(), user_config["user_id"], user_config["seq"])
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file_path = os.path.join(
        output_path, f"{user_config['user_id']}_{user_config['seq']}.tf"
    )
    with open(file_path, "w") as file:
        file.write(terraform_config)
    return output_path


async def run_command(command: List[str]):
    process = await asyncio.create_subprocess_exec(
        *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(f"Command failed: {stderr.decode()}")
    return stdout.decode()


async def terraform_apply(output_path: str) -> str:
    init_command = ["terraform", f"-chdir={output_path}", "init"]
    await run_command(init_command)

    apply_command = ["terraform", f"-chdir={output_path}", "apply", "--auto-approve"]
    apply_process = await run_command(apply_command)

    result = remove_ansi_escape_sequences(apply_process)

    match = re.search(r'private_ip\\":\\"(.*?)\\"', result)

    if match:
        private_ip = match.group(1)
    else:
        print("Public IP 정보를 찾을 수 없습니다.")

    return {"message": result, "private_ip": private_ip}


async def terraform_destroy(work_dir: str) -> str:
    destroy_command = ["terraform", f"-chdir={work_dir}", "destroy", "--auto-approve"]
    destroy_process = await run_command(destroy_command)
    result = remove_ansi_escape_sequences(destroy_process)
    return result
