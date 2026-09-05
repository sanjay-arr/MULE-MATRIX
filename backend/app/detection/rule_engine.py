class RuleEngine:
    def __init__(self):
        self.rules = [
            self.rule_rapid_fund_movement,
            self.rule_high_pass_through,
            self.rule_many_counterparties,
            self.rule_cross_bank_movement,
            self.rule_fan_in,
            self.rule_fan_out,
            self.rule_fund_splitting,
            self.rule_off_ramp_connection,
            self.rule_burst_activity
        ]

    def evaluate(self, features):
        results = []
        for rule in self.rules:
            res = rule(features)
            if res:
                results.append(res)
        return results

    def rule_rapid_fund_movement(self, f):
        threshold = 0.5
        val = f.get('rapid_transfer_ratio', 0)
        if val >= threshold:
            return {
                "rule": "RAPID_FUND_MOVEMENT",
                "triggered": True,
                "feature": "rapid_transfer_ratio",
                "observed_value": val,
                "threshold": threshold,
                "contribution": 15,
                "explanation": f"Rapid movement of funds detected: {val*100:.0f}% of outgoing transfers occurred shortly after receiving funds."
            }
        return None

    def rule_high_pass_through(self, f):
        threshold = 0.85
        val = f.get('pass_through_ratio', 0)
        # We only care if they actually received something substantial to avoid noise
        if val >= threshold and f.get('total_received', 0) > 1000:
            return {
                "rule": "HIGH_PASS_THROUGH",
                "triggered": True,
                "feature": "pass_through_ratio",
                "observed_value": val,
                "threshold": threshold,
                "contribution": 20,
                "explanation": f"High pass-through behaviour: {val*100:.0f}% of incoming funds were transferred out."
            }
        return None

    def rule_many_counterparties(self, f):
        threshold = 10
        val = f.get('unique_counterparties', 0)
        if val >= threshold:
            return {
                "rule": "MANY_COUNTERPARTIES",
                "triggered": True,
                "feature": "unique_counterparties",
                "observed_value": val,
                "threshold": threshold,
                "contribution": 10,
                "explanation": f"{val} unique counterparties detected."
            }
        return None

    def rule_cross_bank_movement(self, f):
        threshold = 3
        val = f.get('unique_banks_involved', 0)
        if val >= threshold:
            return {
                "rule": "CROSS_BANK_MOVEMENT",
                "triggered": True,
                "feature": "unique_banks_involved",
                "observed_value": val,
                "threshold": threshold,
                "contribution": 15,
                "explanation": f"Transactions crossed {val} distinct banks."
            }
        return None

    def rule_fan_in(self, f):
        threshold = 3
        val = f.get('fan_in_count', 0)
        if val >= threshold and f.get('incoming_transaction_count', 0) > 0:
            return {
                "rule": "FAN_IN",
                "triggered": True,
                "feature": "fan_in_count",
                "observed_value": val,
                "threshold": threshold,
                "contribution": 10,
                "explanation": f"Fan-in pattern detected: received funds from {val} distinct sources."
            }
        return None

    def rule_fan_out(self, f):
        threshold = 3
        val = f.get('fan_out_count', 0)
        if val >= threshold and f.get('outgoing_transaction_count', 0) > 0:
            return {
                "rule": "FAN_OUT",
                "triggered": True,
                "feature": "fan_out_count",
                "observed_value": val,
                "threshold": threshold,
                "contribution": 10,
                "explanation": f"Fan-out pattern detected: sent funds to {val} distinct destinations."
            }
        return None

    def rule_fund_splitting(self, f):
        # Splitting is often characterized by 1 large incoming, multiple outgoing
        threshold = 2.0
        val = f.get('outgoing_transaction_count', 0) / max(f.get('incoming_transaction_count', 1), 1)
        if val >= threshold and f.get('total_received', 0) > 5000 and f.get('pass_through_ratio', 0) > 0.8:
            return {
                "rule": "FUND_SPLITTING",
                "triggered": True,
                "feature": "out_to_in_ratio",
                "observed_value": val,
                "threshold": threshold,
                "contribution": 10,
                "explanation": f"Fund splitting detected: High ratio of outgoing to incoming transactions ({val:.1f}x) while passing through funds."
            }
        return None

    def rule_off_ramp_connection(self, f):
        threshold = 1
        val = f.get('off_ramp_connection_count', 0)
        if val >= threshold:
            return {
                "rule": "OFF_RAMP_CONNECTION",
                "triggered": True,
                "feature": "off_ramp_connection_count",
                "observed_value": val,
                "threshold": threshold,
                "contribution": 10,
                "explanation": f"Account is connected to an off-ramp."
            }
        return None

    def rule_burst_activity(self, f):
        threshold = 2
        val = f.get('burst_count', 0)
        if val >= threshold:
            return {
                "rule": "BURST_ACTIVITY",
                "triggered": True,
                "feature": "burst_count",
                "observed_value": val,
                "threshold": threshold,
                "contribution": 10,
                "explanation": f"Burst activity detected: Multiple transactions occurred within short time windows ({val} bursts)."
            }
        return None
