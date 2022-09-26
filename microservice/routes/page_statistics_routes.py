from fastapi import APIRouter, Depends

from microservice.jwt_auth import has_access
from microservice.models.page_statistics import error_response_model, response_model
from microservice.services.page_service import retrieve_pages_statistics

router = APIRouter()


@router.get("/pages/statistics/", response_description="Pages statistics retrieved")
async def get_pages_statistics_data(user_id: int = Depends(has_access)):
    pages_statistics, error_status = await retrieve_pages_statistics(user_id)
    if pages_statistics:
        return response_model(pages_statistics, "Pages statistics data retrieved successfully")
    return response_model(pages_statistics, "Empty list returned")


@router.get(
    "/pages/statistics/{page_id}/",
    response_description="Page statistics data retrieved",
)
async def get_page_statistics_data(page_id: int, user_id: int = Depends(has_access)):
    page_statistics = await retrieve_pages_statistics(user_id, page_id)
    if page_statistics != 404:
        return response_model(page_statistics, "Page statistics data retrieved successfully")
    return error_response_model("An error occurred.", 404, "Page statistics doesn't exist.")
