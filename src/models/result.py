from pydantic import BaseModel, Field


class FXOptionResult(BaseModel):
    id: str
    pv: float = Field(description="Present value of the option")
    delta: float = Field(description="Sensitivity to the underlying asset price")
    vega: float = Field(
        description="Sensitivity to the volatility of the underlying asset"
    )


class PortfolioSummary(BaseModel):
    total_pv: float = Field(description="Total Present value of the option")
    total_delta: float = Field(
        description="Total Sensitivity to the underlying asset price"
    )
    total_vega: float = Field(
        description="Total Sensitivity to the volatility of the underlying asset"
    )
    num_of_trades: int
