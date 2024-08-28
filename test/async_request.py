import asyncio
import aiohttp


async def fetch(session, url, payload):
    async with session.post(url, json=payload) as response:
        if response.headers["Content-Type"] == "application/json":
            return await response.json()
        else:
            return await response.text()


async def main():
    url = "http://localhost:8000/ec2_instance/"
    payloads = [
        {"user_id": "hyukjin", "seq": "1", "template_id": "lt-09c10d50d9f38ae5a"},
        {"user_id": "seondo", "seq": "1", "template_id": "lt-09c10d50d9f38ae5a"},
        {"user_id": "insik", "seq": "1", "template_id": "lt-09c10d50d9f38ae5a"},
    ]

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url, payload) for payload in payloads]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            print(response)


# 이벤트 루프 실행
asyncio.run(main())
