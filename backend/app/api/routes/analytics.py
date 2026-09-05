from fastapi import APIRouter, HTTPException
from backend.app.services.analytics_service import analytics_service

router = APIRouter()

@router.get("/overview")
def get_analytics_overview():
    try:
        return analytics_service.get_overview_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk-distribution")
def get_risk_distribution():
    try:
        return analytics_service.get_risk_distribution()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bank-risk")
def get_bank_risk():
    try:
        return analytics_service.get_bank_risk()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
