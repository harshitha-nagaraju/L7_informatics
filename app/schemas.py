from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class ExpenseCreate(BaseModel):
amount: float = Field(..., gt=0)
category: str
note: Optional[str] = None
created_at: Optional[datetime] = None
user: Optional[str] = "default_user"
share_id: Optional[str] = None


class ExpenseOut(ExpenseCreate):
id: int
created_at: datetime


class Config:
orm_mode = True


class BudgetCreate(BaseModel):
category: str
year: int
month: int
amount: float = Field(..., gt=0)
user: Optional[str] = "default_user"
alert_threshold: Optional[float] = None


class BudgetOut(BudgetCreate):
id: int


class Config:
orm_mode = True


class ReportItem(BaseModel):
category: str
spent: float
budget: Optional[float]
percent_used: Optional[float]
