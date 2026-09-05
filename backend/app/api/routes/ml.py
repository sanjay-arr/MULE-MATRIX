from fastapi import APIRouter, HTTPException
import io
import sys
import os
import threading
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))
from ml.train import train_model
from ml.evaluate import evaluate_model
import traceback

router = APIRouter()

def run_ml_background():
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../ml/run_output.txt"))
    with open(output_path, "w") as f:
        old_stdout = sys.stdout
        sys.stdout = f
        
        try:
            f.write("Starting training...\n")
            train_model()
            f.write("Starting evaluation...\n")
            evaluate_model()
            f.write("Done!\n")
        except Exception as e:
            f.write(f"Error: {e}\n")
            f.write(traceback.format_exc())
        finally:
            sys.stdout = old_stdout

@router.get("/run_all_async")
def run_all_async():
    threading.Thread(target=run_ml_background).start()
    return {"status": "started"}

@router.get("/find_trail")
def api_find_trail():
    from backend.app.core.database import neo4j_conn
    query = """
    MATCH path = (victim:Account)-[t1:TRANSFER]->(m1:Account)-[t2:TRANSFER]->(m2:Account)-[t3:TRANSFER]->(offramp:Account {account_type: 'OFF_RAMP'})
    WHERE m1.bank_id <> m2.bank_id
    RETURN [n in nodes(path) | n.account_id] AS path_accounts,
           [n in nodes(path) | n.bank_id] AS banks
    LIMIT 1
    """
    results = neo4j_conn.query(query)
    return results

@router.get("/metrics")
def api_get_metrics():
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../ml/models"))
    metrics_path = os.path.join(models_dir, "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            return json.load(f)
    else:
        raise HTTPException(status_code=404, detail="Metrics not found. Model might not be trained yet.")

@router.get("/check_gnn")
def check_gnn():
    import sys
    res = {"python_version": sys.version}
    try:
        import torch
        res["torch_version"] = torch.__version__
        res["cuda_available"] = torch.cuda.is_available()
    except ImportError:
        res["torch_installed"] = False
        
    try:
        import torch_geometric
        res["torch_geometric_version"] = torch_geometric.__version__
    except ImportError:
        res["torch_geometric_installed"] = False
        
    return res
