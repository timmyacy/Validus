from pydantic import BaseModel, Field


class FXOptionResult(BaseModel):
    id: str
    pv: float = Field(description="Present value of the option")
    delta: float = Field(description="Sensitivity to the underlying asset price")
    vega: float = Field (description="Sensitivity to the volatility of the underlying asset")

class PortfolioSummary(BaseModel):
    total_pv: float
    total_delta: float
    total_vega: float
    num_of_trades: int
