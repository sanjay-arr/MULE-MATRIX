class InvestigationService:
    def __init__(self, network_service):
        self.network_service = network_service

    def build_investigation_report(self, account_id):
        network = self.network_service.reconstruct_network(account_id)
        if not network:
            return {"error": "No network found or graph connection failed"}
            
        threat_level = "LOW"
        if network['average_risk_score'] > 80:
            threat_level = "CRITICAL"
        elif network['average_risk_score'] > 60:
            threat_level = "HIGH"
        elif network['average_risk_score'] > 40:
            threat_level = "MEDIUM"

        return {
            "network_id": network['network_id'],
            "threat_level": threat_level,
            "accounts_involved": network['total_accounts'],
            "banks_involved": network['number_of_banks'],
            "suspicious_amount": network['total_amount'],
            "cross_bank_transactions": network['cross_bank_transactions'],
            "max_hops": network['max_hops'],
            "highest_risk_account": network['highest_risk_account'],
            "off_ramps_found": network['off_ramp_connections'],
            "off_ramps": network['off_ramps'],
            "money_trail": [] # This would be populated by the money_trail cypher query in a full flow
        }
