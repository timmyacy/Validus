from pydantic import BaseModel


class FXOptionResult(BaseModel):
    id: str
    pv: float
    delta: float
    vega: float

class PortfolioSummary(BaseModel):
    total_pv: float
    total_delta: float
    total_vega: float
    num_of_trades: int
