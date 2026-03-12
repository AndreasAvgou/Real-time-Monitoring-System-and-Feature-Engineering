from sqlalchemy import Column, Integer, String, Float
from datetime import datetime, timezone
from .database import Base


def get_iso_timestamp():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

class TransactionalData(Base):
    __tablename__ = "transactional_data"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    loan_date = Column(String)
    amount = Column(Float)
    fee = Column(Float)
    term = Column(String)
    loan_status = Column(Integer)
    annual_income = Column(Float)

class FeatureData(Base):
    __tablename__ = "feature_data"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    total_amount = Column(Float)
    income_ratio = Column(Float)
    created_at = Column(String, default=get_iso_timestamp)

class MetricLog(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String)
    latency = Column(Float)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    zero_value_count = Column(Integer)
    status_code = Column(Integer, index=True) 
    timestamp = Column(String, default=get_iso_timestamp, index=True)