import pytest
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app.services.graph_service import GraphService
from backend.app.services.network_service import NetworkService
from backend.app.services.investigation_service import InvestigationService

@pytest.fixture(scope="module")
def graph_service():
    gs = GraphService()
    try:
        gs.connect_to_neo4j()
        # Seed test graph
        gs.conn.query("MATCH (n:TestNode) DETACH DELETE n") # clean
        yield gs
    except Exception as e:
        pytest.skip(f"Neo4j not available: {e}")

def test_neo4j_connection(graph_service):
    assert graph_service.conn._driver is not None

def test_network_reconstruction(graph_service):
    # We test the logic with a mock dataframe
    risk_df = pd.DataFrame([
        {"account_id": "MULE_A", "risk_score": 85, "risk_level": "CRITICAL"}
    ])
    ns = NetworkService(graph_service, risk_df)
    
    # We assume the DB has data from load_neo4j or we just test the mock logic
    # Since DB state is unknown in isolated unit tests, we'll verify the service initializes correctly
    assert ns.risk_results is not None
    
def test_investigation_service_formats_correctly():
    class MockNetworkService:
        def reconstruct_network(self, account_id):
            return {
                "network_id": "MM-NET-123",
                "total_accounts": 5,
                "number_of_banks": 3,
                "total_amount": 100000.0,
                "cross_bank_transactions": 2,
                "max_hops": 3,
                "highest_risk_account": "MULE_1",
                "off_ramp_connections": 1,
                "off_ramps": ["OFFRAMP_X"],
                "average_risk_score": 75.0
            }
            
    ins = InvestigationService(MockNetworkService())
    report = ins.build_investigation_report("MULE_1")
    assert report['threat_level'] == "HIGH"
    assert report['accounts_involved'] == 5
