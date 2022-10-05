import asyncio

import uvicorn
from fastapi import Depends, FastAPI

from microservice.consumer import consume
from microservice.jwt_auth import has_access
from microservice.routes.page_statistics_routes import router
from microservice.services.page_service import create_table

app = FastAPI()
app.include_router(router, tags=["pages"], prefix="", dependencies=[Depends(has_access)])


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(consume(loop))
    await create_table()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
