import os
import yaml
from fastapi import APIRouter, HTTPException
from github import Github

router = APIRouter(prefix="/yaml", tags=["Version control"])

GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
REPO_NAME = "SeSAC-Cloud-dev/k8s"
FILE_PATH = "mattermost/mattermost/mattermost-deployment.yaml"
BRANCH_NAME = "main"


@router.put("/")
async def update_yaml(new_value: str):
    try:
        # GitHub 인스턴스 생성
        g = Github(GITHUB_ACCESS_TOKEN)
        repo = g.get_repo(REPO_NAME)

        # 파일 내용 가져오기
        file = repo.get_contents(FILE_PATH, ref=BRANCH_NAME)
        content = file.decoded_content.decode()
        print(f"content : {content}")
        print(f"Before File SHA: {file.sha}")
        yaml_content = yaml.safe_load(content)
        print(f"yaml_content : {yaml_content}")
        yaml_content["spec"]["template"]["spec"]["containers"][0][
            "image"
        ] = f"214346124741.dkr.ecr.ap-northeast-2.amazonaws.com/cloudnexus/mattermost:{new_value}"
        updated_content = yaml.safe_dump(
            yaml_content, indent=2, sort_keys=False, default_flow_style=False
        )
        
        print(f"updated_content : {updated_content}")


        # 변경사항 커밋
        repo.update_file(
            FILE_PATH, f"Update to tag {new_value}", updated_content, file.sha
        )

        return {"message": "Configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
