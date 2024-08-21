import re
import os
import subprocess


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
        profile = "default" 
        region = "ap-northeast-2"
    }}

    # EC2 설정 
    resource "aws_instance" "EC2" {{
        ami = "{user_config["ami_id"]}"
        instance_type = "{user_config["instance_type"]}"
        subnet_id = "{user_config["subnet_id"]}"
        tags = {{
            Name = "{user_config["tag_name"]}"
        }}
    }}

    output "instance_public_ip" {{
        value = jsonencode({{public_ip = aws_instance.EC2.public_ip}})
    }}
    """

    output_path = os.path.join(os.getcwd(), user_config["user_id"], user_config["seq"])
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file_path = os.path.join(
        output_path, f"{user_config["user_id"]}_{user_config["seq"]}.tf"
    )
    with open(file_path, "w") as file:
        file.write(terraform_config)
    return output_path


def terraform_apply(output_path: str) -> str:
    init_process = subprocess.run(
        ["terraform", f"-chdir={output_path}", "init"], capture_output=True, text=True
    )
    if init_process.returncode != 0:
        raise Exception(f"Terraform init failed: {init_process.stderr}")

    apply_process = subprocess.run(
        ["terraform", f"-chdir={output_path}", "apply", "--auto-approve"],
        capture_output=True,
        text=True,
    )
    if apply_process.returncode != 0:
        raise Exception(f"Terraform apply failed: {apply_process.stderr}")

    result = remove_ansi_escape_sequences(apply_process.stdout)
    
    match = re.search(r'public_ip\\":\\"(.*?)\\"', result)
    
    if match:
        public_ip = match.group(1)
    else:
        print("Public IP 정보를 찾을 수 없습니다.")
        
    return {"message": result, "public_ip" : public_ip}


def terraform_destroy(work_dir: str) -> str:
    destroy_process = subprocess.run(
        ["terraform", f"-chdir={work_dir}", "destroy", "--auto-approve"],
        capture_output=True,
        text=True,
    )

    if destroy_process.returncode != 0:
        raise Exception(f"Terraform apply failed: {destroy_process.stderr}")

    result = remove_ansi_escape_sequences(destroy_process.stdout)
    return result
