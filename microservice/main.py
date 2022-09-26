import uvicorn
from fastapi import Depends, FastAPI

from microservice.jwt_auth import has_access
from microservice.routes.page_statistics_routes import router

app = FastAPI()
app.include_router(router, tags=["pages"], prefix="", dependencies=[Depends(has_access)])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
