"""Request and response models for the option pricing API."""

from typing import Optional

from pydantic import BaseModel, Field


class OptionInput(BaseModel):
    stock_price: float = Field(..., gt=0, description="Current stock price (S)")
    strike_price: float = Field(..., gt=0, description="Strike price (K)")
    time_to_maturity: float = Field(..., gt=0, description="Time to maturity in years (T)")
    rate: float = Field(..., description="Risk-free interest rate (r)")
    volatility: float = Field(..., gt=0, description="Volatility (sigma)")


class OptionMetrics(BaseModel):
    price: float
    delta: float
    vega: float


class ErrorMetrics(BaseModel):
    price_abs_error: float
    delta_abs_error: float
    vega_abs_error: float


class AnalyzeResponse(BaseModel):
    exact: OptionMetrics
    predicted: Optional[OptionMetrics] = None
    error: Optional[ErrorMetrics] = None
    model_loaded: bool


class SensitivityPoint(BaseModel):
    stock_price: float
    exact_price: float
    exact_delta: float
    exact_vega: float
    predicted_price: Optional[float] = None
    predicted_delta: Optional[float] = None
    predicted_vega: Optional[float] = None


class SensitivityResponse(BaseModel):
    points: list[SensitivityPoint]
    model_loaded: bool


class RuntimeMetrics(BaseModel):
    exact_runtime_ms: float
    predicted_runtime_ms: Optional[float] = None
    model_loaded: bool
