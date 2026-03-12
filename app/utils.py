import psutil
import time

def get_system_metrics():
    return {
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent
    }

def perform_feature_engineering(data):
    # Count of features with zero values
    zero_count = 0
    for customer in data.get("data", []):
        for loan in customer.get("loans", []):
            for value in loan.values():
                if value == 0 or value == "0":
                    zero_count += 1
    return zero_count