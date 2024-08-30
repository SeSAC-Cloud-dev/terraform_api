import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GUACAMOLE_URL = os.environ.get("GUACAMOLE_URL")
GUACAMOLE_ID = os.environ.get("GUACAMOLE_ID")
GUACAMOLE_PW = os.environ.get("GUACAMOLE_PW")
GUACAMOLE_DATASOURCE = os.environ.get("GUACAMOLE_DATASOURCE")
GUACAMOLE_TOKEN = None


async def get_guacamole_token(url: str, id: str, pw: str, datasource: str) -> str:
    global GUACAMOLE_TOKEN

    data = {"username": id, "password": pw}

    # Token 미발급 상태라면 Generate
    if GUACAMOLE_TOKEN == None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{url}/api/tokens", data=data)
                r = response.raise_for_status().json()
                token = r.get("authToken")
                print(f"############ None -> Token Generate ############")
        except httpx.HTTPStatusError as exc:
            print(f"HTTP Status Error: {exc.response.status_code}")
            print(f"Error Message: {exc.response.text}")
            # 추가적인 디버깅 정보를 위한 예외 내용 출력
            print(f"Request URL: {exc.request.url}")
            print(f"Request Method: {exc.request.method}")
            print(f"Request Headers: {exc.request.headers}")
            print(f"Request Body: {exc.request.content}")
            raise

    params = {"token": token}

    # 현재 토큰 값이 유효 토큰인지 검증 후 유효하지 않다면 재발급
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{url}/api/session/data/{datasource}/connections/",
                params=params,
                data=data,
            )
            if response.status_code == 403:
                async with httpx.AsyncClient() as client:
                    response = await client.post(f"{url}/api/tokens", data=data)
                r = response.raise_for_status.json()
                token = response.get("authToken")
                print(f"############ Permission Denied -> Token Generate ############")
        return token
    except httpx.HTTPStatusError as exc:
        print(f"HTTP Status Error: {exc.response.status_code}")
        print(f"Error Message: {exc.response.text}")
        # 추가적인 디버깅 정보를 위한 예외 내용 출력
        print(f"Request URL: {exc.request.url}")
        print(f"Request Method: {exc.request.method}")
        print(f"Request Headers: {exc.request.headers}")
        print(f"Request Body: {exc.request.content}")
        raise


async def create_guacamole_connection(
    instance_tag: str,
    password: str,
    ip: str,
    username: str = "Administrator",
):
    global GUACAMOLE_URL
    global GUACAMOLE_ID
    global GUACAMOLE_PW
    global GUACAMOLE_DATASOURCE

    token = await get_guacamole_token(
        GUACAMOLE_URL, GUACAMOLE_ID, GUACAMOLE_PW, GUACAMOLE_DATASOURCE
    )

    headers = {"Content-Type": "application/json"}
    params = {"token": token}
    data = {
        "parentIdentifier": "ROOT",
        "name": instance_tag,
        "protocol": "rdp",
        "parameters": {
            "port": "3389",
            "read-only": "",
            "swap-red-blue": "",
            "cursor": "",
            "color-depth": "",
            "clipboard-encoding": "",
            "disable-copy": "",
            "disable-paste": "",
            "dest-port": "",
            "recording-exclude-output": "",
            "recording-exclude-mouse": "",
            "recording-include-keys": "",
            "create-recording-path": "",
            "enable-sftp": "",
            "sftp-port": "",
            "sftp-server-alive-interval": "",
            "enable-audio": "",
            "security": "",
            "disable-auth": "",
            "ignore-cert": "true",
            "gateway-port": "",
            "server-layout": "",
            "timezone": "",
            "console": "",
            "width": "",
            "height": "",
            "dpi": "",
            "resize-method": "",
            "console-audio": "",
            "disable-audio": "",
            "enable-audio-input": "",
            "enable-printing": "",
            "enable-drive": "",
            "create-drive-path": "",
            "enable-wallpaper": "",
            "enable-theming": "",
            "enable-font-smoothing": "",
            "enable-full-window-drag": "",
            "enable-desktop-composition": "",
            "enable-menu-animations": "",
            "disable-bitmap-caching": "",
            "disable-offscreen-caching": "",
            "disable-glyph-caching": "",
            "preconnection-id": "",
            "hostname": ip,
            "username": username,
            "password": password,
            "domain": "",
            "gateway-hostname": "",
            "gateway-username": "",
            "gateway-password": "",
            "gateway-domain": "",
            "initial-program": "",
            "client-name": "",
            "printer-name": "",
            "drive-name": "",
            "drive-path": "",
            "static-channels": "",
            "remote-app": "",
            "remote-app-dir": "",
            "remote-app-args": "",
            "preconnection-blob": "",
            "load-balance-info": "",
            "recording-path": "",
            "recording-name": "",
            "sftp-hostname": "",
            "sftp-host-key": "",
            "sftp-username": "",
            "sftp-password": "",
            "sftp-private-key": "",
            "sftp-passphrase": "",
            "sftp-root-directory": "",
            "sftp-directory": "",
        },
        "attributes": {
            "max-connections": "",
            "max-connections-per-user": "",
            "weight": "",
            "failover-only": "",
            "guacd-port": "",
            "guacd-encryption": "",
            "guacd-hostname": "",
        },
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GUACAMOLE_URL}/api/session/data/{GUACAMOLE_DATASOURCE}/connections",
                headers=headers,
                params=params,
                json=data,
            )
            r = response.raise_for_status().json()
        return r
    except httpx.HTTPStatusError as exc:
        print(f"HTTP Status Error: {exc.response.status_code}")
        print(f"Error Message: {exc.response.text}")
        # 추가적인 디버깅 정보를 위한 예외 내용 출력
        print(f"Request URL: {exc.request.url}")
        print(f"Request Method: {exc.request.method}")
        print(f"Request Headers: {exc.request.headers}")
        print(f"Request Body: {exc.request.content}")
        raise


async def delete_guacamole_connection(connection_name: str):
    global GUACAMOLE_URL
    global GUACAMOLE_ID
    global GUACAMOLE_PW
    global GUACAMOLE_DATASOURCE

    # Token 유효성 체크 및 생성
    token = await get_guacamole_token(
        GUACAMOLE_URL, GUACAMOLE_ID, GUACAMOLE_PW, GUACAMOLE_DATASOURCE
    )
    headers = {"Content-Type": "application/json"}
    params = {"token": token}

    # Connection_list 모두 불러오기
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GUACAMOLE_URL}/api/session/data/{GUACAMOLE_DATASOURCE}/connections/",
                headers=headers,
                params=params,
            )
            r = response.raise_for_status().json()
    except httpx.HTTPStatusError as exc:
        print(f"HTTP Status Error: {exc.response.status_code}")
        print(f"Error Message: {exc.response.text}")
        # 추가적인 디버깅 정보를 위한 예외 내용 출력
        print(f"Request URL: {exc.request.url}")
        print(f"Request Method: {exc.request.method}")
        print(f"Request Headers: {exc.request.headers}")
        print(f"Request Body: {exc.request.content}")
        raise

    # Connection_list에서 Connection_num찾기
    connection_num = None

    for key, value in r.items():
        if value.get("name") == connection_name:
            connection_num = key

    if connection_num == None:
        raise ValueError("존재하지 않는 Connection 번호입니다.")

    # Connection_num을 이용해 Connection 삭제
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{GUACAMOLE_URL}/api/session/data/{GUACAMOLE_DATASOURCE}/connections/{connection_num}",
                headers=headers,
                params=params,
            )
            r = response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print(f"HTTP Status Error: {exc.response.status_code}")
        print(f"Error Message: {exc.response.text}")
        # 추가적인 디버깅 정보를 위한 예외 내용 출력
        print(f"Request URL: {exc.request.url}")
        print(f"Request Method: {exc.request.method}")
        print(f"Request Headers: {exc.request.headers}")
        print(f"Request Body: {exc.request.content}")
        raise
