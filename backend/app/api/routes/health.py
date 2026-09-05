from fastapi import APIRouter, HTTPException, status
from backend.app.core.database import neo4j_conn

router = APIRouter()

@router.get("")
def health_check():
    from backend.app.core.data import data_store
    
    dataset_status = "missing"
    if data_store.accounts_df is not None and data_store.detection_df is not None:
        dataset_status = "initialized"
        
    return {
        "status": "healthy",
        "service": "mule-matrix",
        "dataset": dataset_status
    }

@router.get("/neo4j")
def neo4j_health_check():
    try:
        # Perform a simple query to check connection
        neo4j_conn.query("RETURN 1 AS num")
        return {
            "status": "healthy",
            "neo4j": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Neo4j unavailable: {str(e)}"
        )
