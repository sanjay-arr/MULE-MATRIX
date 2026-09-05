from fastapi import APIRouter

from backend.app.api.routes import health, accounts, transactions, networks, investigations, analytics, alerts, ml, demo

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(networks.router, prefix="/networks", tags=["networks"])
api_router.include_router(investigations.router, prefix="/investigations", tags=["investigations"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(ml.router, prefix="/ml", tags=["ml"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
