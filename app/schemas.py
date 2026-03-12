from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List

class LoanRecord(BaseModel):
    loan_date: str
    amount: float = Field(..., ge=100, le=1000)
    fee: float = Field(..., ge=10, le=50)
    term: str
    loan_status: int = Field(..., ge=0, le=1)
    annual_income: float = Field(..., ge=100, le=10000000)

    @field_validator('term')
    def validate_term(cls, v):
        if v not in ['short', 'long']:
            raise ValueError('term must be "short" or "long"')
        return v

    @model_validator(mode='after')
    def validate_income_tiers(self) -> 'LoanRecord':
        total = self.amount + self.fee
        inc = self.annual_income
        if 100 <= inc <= 1000 and total > 110: raise ValueError("Total amount > 110 for this income")
        if 1000 < inc <= 10000 and total > 220: raise ValueError("Total amount > 220 for this income")
        if 10000 < inc <= 100000 and total > 550: raise ValueError("Total amount > 550 for this income")
        if 100000 < inc <= 10000000 and total > 1050: raise ValueError("Total amount > 1050 for this income")
        return self

class CustomerData(BaseModel):
    customer_ID: str = Field(..., min_length=10, max_length=20)
    loans: List[LoanRecord]

    @field_validator('customer_ID')
    def validate_ascii(cls, v):
        if not v.isascii(): raise ValueError("customer_ID must be ASCII only")
        return v

class FeatureRequest(BaseModel):
    data: List[CustomerData]