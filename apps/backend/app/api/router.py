from fastapi import APIRouter

from app.api import admin, analytics, companies, saved_companies

api_router = APIRouter()
api_router.include_router(companies.router)
api_router.include_router(analytics.router)
api_router.include_router(saved_companies.router)
api_router.include_router(admin.router)
