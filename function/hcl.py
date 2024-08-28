import re
import os
import json
import asyncio
from typing import List
from ast import literal_eval

# Secret
KEY_PATH = "./key.pem"
    
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
        get_password_data = true
    }}

    output "instance_id" {{
      value = aws_instance.EC2.id
    }}

    output "instance_private_ip" {{
        value = aws_instance.EC2.private_ip
    }}
    """

    output_path = os.path.join(os.getcwd(), "user_tf", user_config["user_id"], user_config["seq"])
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file_path = os.path.join(
        output_path, f"{user_config['user_id']}_{user_config['seq']}.tf"
    )
    with open(file_path, "w") as file:
        file.write(terraform_config)
    return output_path

async def decrypt_password(instance_id, key_path):
    decrypt_command = ["aws", "ec2", "get-password-data", "--instance-id", f"{instance_id}", "--priv-launch-key", f"{key_path}"]
    decrypt_process = await run_command(decrypt_command)
    return decrypt_process

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
    await run_command(apply_command)
    
    # Terraform 결과 추출
    terraform_result_path = os.path.join(output_path, "terraform.tfstate")
    with open(terraform_result_path, 'r') as file:
        result_data = json.load(file)
        
    instance_id = result_data['outputs']['instance_id']['value']
    instance_private_ip = result_data['outputs']['instance_private_ip']['value']
    
    # Password 복호화
    pass_data = await decrypt_password(instance_id, KEY_PATH)
    password = literal_eval(pass_data)['PasswordData']
    
    # Guacamole VD 연결 API
    return {"instance_id" : instance_id, "private_ip" : instance_private_ip, "password_data" : password}


async def terraform_destroy(work_dir: str) -> str:
    destroy_command = ["terraform", f"-chdir={work_dir}", "destroy", "--auto-approve"]
    destroy_process = await run_command(destroy_command)
    result = remove_ansi_escape_sequences(destroy_process)
    return {"message" : result}
