import random

from datetime import datetime, timedelta

def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )

def generate_account_id(prefix="ACC"):
    hex_str = ''.join(random.choices('0123456789ABCDEF', k=8))
    return f"{prefix}_{hex_str}"

def generate_device_id():
    hex_str = ''.join(random.choices('0123456789ABCDEF', k=12))
    return f"DEV_{hex_str}"

def generate_location():
    cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad"]
    return random.choice(cities)

def create_mule_network_pass_through(banks, start_time, network_id):
    accounts = []
    transactions = []
    
    # 1 Victim, 2 Mules, 1 Off-ramp
    victim = {"account_id": generate_account_id("VIC"), "bank_id": random.choice(banks), "account_type": "CUSTOMER", "is_mule": False, "network_id": "NORMAL"}
    mule1 = {"account_id": generate_account_id("MUL"), "bank_id": random.choice(banks), "account_type": "MULE", "is_mule": True, "network_id": network_id}
    mule2 = {"account_id": generate_account_id("MUL"), "bank_id": random.choice(banks), "account_type": "MULE", "is_mule": True, "network_id": network_id}
    off_ramp = {"account_id": generate_account_id("OFF"), "bank_id": random.choice(banks), "account_type": "OFF_RAMP", "is_mule": True, "network_id": network_id}
    
    accounts.extend([victim, mule1, mule2, off_ramp])
    for a in accounts:
        a.update({
            "account_age_days": random.randint(1, 1000),
            "created_at": (start_time - timedelta(days=random.randint(1, 1000))).isoformat(),
            "device_id": generate_device_id(),
            "location": generate_location()
        })
    
    amount = random.randint(10000, 100000)
    
    t1_time = start_time
    transactions.append({
        "transaction_id": f"TXN_{''.join(random.choices('0123456789ABCDEF', k=10))}",
        "timestamp": t1_time.isoformat(),
        "sender_account": victim["account_id"],
        "receiver_account": mule1["account_id"],
        "sender_bank": victim["bank_id"],
        "receiver_bank": mule1["bank_id"],
        "amount": amount,
        "transaction_type": "TRANSFER",
        "device_id": victim["device_id"],
        "location": victim["location"],
        "is_suspicious": True,
        "network_id": network_id
    })
    
    amount = int(amount * 0.98) # Keep a cut
    t2_time = t1_time + timedelta(minutes=random.randint(2, 30))
    transactions.append({
        "transaction_id": f"TXN_{''.join(random.choices('0123456789ABCDEF', k=10))}",
        "timestamp": t2_time.isoformat(),
        "sender_account": mule1["account_id"],
        "receiver_account": mule2["account_id"],
        "sender_bank": mule1["bank_id"],
        "receiver_bank": mule2["bank_id"],
        "amount": amount,
        "transaction_type": "TRANSFER",
        "device_id": mule1["device_id"],
        "location": mule1["location"],
        "is_suspicious": True,
        "network_id": network_id
    })
    
    amount = int(amount * 0.99)
    t3_time = t2_time + timedelta(minutes=random.randint(2, 30))
    transactions.append({
        "transaction_id": f"TXN_{''.join(random.choices('0123456789ABCDEF', k=10))}",
        "timestamp": t3_time.isoformat(),
        "sender_account": mule2["account_id"],
        "receiver_account": off_ramp["account_id"],
        "sender_bank": mule2["bank_id"],
        "receiver_bank": off_ramp["bank_id"],
        "amount": amount,
        "transaction_type": "OFF_RAMP",
        "device_id": mule2["device_id"],
        "location": mule2["location"],
        "is_suspicious": True,
        "network_id": network_id
    })
    
    return accounts, transactions

def create_mule_network_fan_out(banks, start_time, network_id):
    accounts = []
    transactions = []
    
    source = {"account_id": generate_account_id("MUL_SRC"), "bank_id": random.choice(banks), "account_type": "MULE", "is_mule": True, "network_id": network_id}
    accounts.append(source)
    
    num_mules = random.randint(3, 6)
    mules = []
    for i in range(num_mules):
        m = {"account_id": generate_account_id(f"MUL_DEST_{i}"), "bank_id": random.choice(banks), "account_type": "MULE", "is_mule": True, "network_id": network_id}
        accounts.append(m)
        mules.append(m)
        
    for a in accounts:
        a.update({
            "account_age_days": random.randint(1, 100),
            "created_at": (start_time - timedelta(days=random.randint(1, 100))).isoformat(),
            "device_id": generate_device_id(),
            "location": generate_location()
        })
        
    base_amount = random.randint(50000, 200000)
    current_time = start_time
    
    for m in mules:
        split_amount = int(base_amount / num_mules)
        current_time += timedelta(minutes=random.randint(1, 15))
        transactions.append({
            "transaction_id": f"TXN_{''.join(random.choices('0123456789ABCDEF', k=10))}",
            "timestamp": current_time.isoformat(),
            "sender_account": source["account_id"],
            "receiver_account": m["account_id"],
            "sender_bank": source["bank_id"],
            "receiver_bank": m["bank_id"],
            "amount": split_amount,
            "transaction_type": "UPI_SIMULATED",
            "device_id": source["device_id"],
            "location": source["location"],
            "is_suspicious": True,
            "network_id": network_id
        })
        
    return accounts, transactions

def create_mule_network_fan_in(banks, start_time, network_id):
    accounts = []
    transactions = []
    
    dest = {"account_id": generate_account_id("MUL_DEST"), "bank_id": random.choice(banks), "account_type": "MULE", "is_mule": True, "network_id": network_id}
    accounts.append(dest)
    
    num_mules = random.randint(3, 6)
    mules = []
    for i in range(num_mules):
        m = {"account_id": generate_account_id(f"MUL_SRC_{i}"), "bank_id": random.choice(banks), "account_type": "MULE", "is_mule": True, "network_id": network_id}
        accounts.append(m)
        mules.append(m)
        
    for a in accounts:
        a.update({
            "account_age_days": random.randint(1, 100),
            "created_at": (start_time - timedelta(days=random.randint(1, 100))).isoformat(),
            "device_id": generate_device_id(),
            "location": generate_location()
        })
        
    current_time = start_time
    
    for m in mules:
        amount = random.randint(10000, 50000)
        current_time += timedelta(minutes=random.randint(1, 15))
        transactions.append({
            "transaction_id": f"TXN_{''.join(random.choices('0123456789ABCDEF', k=10))}",
            "timestamp": current_time.isoformat(),
            "sender_account": m["account_id"],
            "receiver_account": dest["account_id"],
            "sender_bank": m["bank_id"],
            "receiver_bank": dest["bank_id"],
            "amount": amount,
            "transaction_type": "TRANSFER",
            "device_id": m["device_id"],
            "location": m["location"],
            "is_suspicious": True,
            "network_id": network_id
        })
        
    return accounts, transactions

def create_cross_bank_mule_network(banks, start_time, network_id):
    accounts = []
    transactions = []
    
    # Needs to cross at least 3 distinct banks
    selected_banks = random.sample(banks, min(4, len(banks)))
    
    victim = {"account_id": generate_account_id("VIC"), "bank_id": selected_banks[0], "account_type": "CUSTOMER", "is_mule": False, "network_id": "NORMAL"}
    mule1 = {"account_id": generate_account_id("MUL_A"), "bank_id": selected_banks[1], "account_type": "MULE", "is_mule": True, "network_id": network_id}
    mule2 = {"account_id": generate_account_id("MUL_B"), "bank_id": selected_banks[2], "account_type": "MULE", "is_mule": True, "network_id": network_id}
    off_ramp = {"account_id": generate_account_id("OFF"), "bank_id": selected_banks[3] if len(selected_banks) > 3 else selected_banks[0], "account_type": "OFF_RAMP", "is_mule": True, "network_id": network_id}
    
    accounts.extend([victim, mule1, mule2, off_ramp])
    for a in accounts:
        a.update({
            "account_age_days": random.randint(1, 300),
            "created_at": (start_time - timedelta(days=random.randint(1, 300))).isoformat(),
            "device_id": generate_device_id(),
            "location": generate_location()
        })
        
    amount = random.randint(50000, 200000)
    current_time = start_time
    
    chain = [(victim, mule1), (mule1, mule2), (mule2, off_ramp)]
    
    for sender, receiver in chain:
        current_time += timedelta(minutes=random.randint(1, 20))
        tx_type = "TRANSFER" if receiver["account_type"] != "OFF_RAMP" else "OFF_RAMP"
        transactions.append({
            "transaction_id": f"TXN_{''.join(random.choices('0123456789ABCDEF', k=10))}",
            "timestamp": current_time.isoformat(),
            "sender_account": sender["account_id"],
            "receiver_account": receiver["account_id"],
            "sender_bank": sender["bank_id"],
            "receiver_bank": receiver["bank_id"],
            "amount": amount,
            "transaction_type": tx_type,
            "device_id": sender["device_id"],
            "location": sender["location"],
            "is_suspicious": True,
            "network_id": network_id
        })
        amount = int(amount * random.uniform(0.95, 0.99)) # Drop a bit each hop
        
    return accounts, transactions

def generate_fraud_scenarios(banks, count, start_date, end_date):
    accounts = []
    transactions = []
    networks_meta = {}
    
    scenario_funcs = [
        create_mule_network_pass_through,
        create_mule_network_fan_out,
        create_mule_network_fan_in,
        create_cross_bank_mule_network
    ]
    
    for i in range(count):
        network_id = f"NETWORK_{i:03d}"
        func = random.choice(scenario_funcs)
        scenario_start = random_date(start_date, end_date - timedelta(days=1))
        accs, txns = func(banks, scenario_start, network_id)
        
        accounts.extend(accs)
        transactions.extend(txns)
        
        networks_meta[network_id] = {
            "type": func.__name__,
            "accounts_involved": [a["account_id"] for a in accs],
            "transaction_count": len(txns)
        }
        
    return accounts, transactions, networks_meta
