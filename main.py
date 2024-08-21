from fastapi import FastAPI
from router import hcl_maker

app = FastAPI()
app.include_router(hcl_maker.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/ping")
async def ping():
    return {"message": "PONG"}
