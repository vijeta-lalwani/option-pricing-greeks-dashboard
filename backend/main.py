"""
FastAPI app for exact Black-Scholes option pricing and Greeks.

This is the first backend milestone for the dashboard project.
"""

from typing import Optional

from time import perf_counter

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

from black_scholes import call_delta, call_price, call_vega
from model_utils import load_artifacts, scale_features, unscale_targets
from schemas import (
    AnalyzeResponse,
    ErrorMetrics,
    OptionInput,
    OptionMetrics,
    RuntimeMetrics,
    SensitivityPoint,
    SensitivityResponse,
)


app = FastAPI(
    title="Option Pricing Greeks API",
    description="Compute Black-Scholes call price, delta, and vega.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def predict_metrics(option_input: OptionInput) -> Optional[OptionMetrics]:
    """
    Return surrogate model predictions if trained artifacts are available.
    """
    artifacts = load_artifacts()
    if artifacts is None:
        return None

    features = [
        option_input.stock_price,
        option_input.strike_price,
        option_input.time_to_maturity,
        option_input.rate,
        option_input.volatility,
    ]

    import torch

    feature_array = np.array([features], dtype=np.float32)
    scaled_features = scale_features(
        feature_array,
        artifacts["feature_mean"],
        artifacts["feature_std"],
    )

    with torch.no_grad():
        raw_prediction = artifacts["model"](torch.tensor(scaled_features, dtype=torch.float32))

    prediction = unscale_targets(
        raw_prediction.numpy(),
        artifacts["target_mean"],
        artifacts["target_std"],
    )[0]

    return OptionMetrics(
        price=float(prediction[0]),
        delta=float(prediction[1]),
        vega=float(prediction[2]),
    )


@app.get("/")
def read_root() -> dict:
    """Basic health check route."""
    return {"message": "Option Pricing Greeks API is running."}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_option(option_input: OptionInput) -> AnalyzeResponse:
    """
    Compute exact Black-Scholes outputs and, when available, surrogate predictions.
    """
    price = call_price(
        option_input.stock_price,
        option_input.strike_price,
        option_input.time_to_maturity,
        option_input.rate,
        option_input.volatility,
    )
    delta = call_delta(
        option_input.stock_price,
        option_input.strike_price,
        option_input.time_to_maturity,
        option_input.rate,
        option_input.volatility,
    )
    vega = call_vega(
        option_input.stock_price,
        option_input.strike_price,
        option_input.time_to_maturity,
        option_input.rate,
        option_input.volatility,
    )

    exact_metrics = OptionMetrics(price=price, delta=delta, vega=vega)
    predicted_metrics = predict_metrics(option_input)

    if predicted_metrics is None:
        return AnalyzeResponse(exact=exact_metrics, predicted=None, error=None, model_loaded=False)

    error_metrics = ErrorMetrics(
        price_abs_error=abs(exact_metrics.price - predicted_metrics.price),
        delta_abs_error=abs(exact_metrics.delta - predicted_metrics.delta),
        vega_abs_error=abs(exact_metrics.vega - predicted_metrics.vega),
    )

    return AnalyzeResponse(
        exact=exact_metrics,
        predicted=predicted_metrics,
        error=error_metrics,
        model_loaded=True,
    )


@app.post("/sensitivity", response_model=SensitivityResponse)
def sensitivity_curve(option_input: OptionInput) -> SensitivityResponse:
    """
    Return a simple price sensitivity curve by varying stock price.
    """
    stock_prices = np.linspace(
        option_input.stock_price * 0.7,
        option_input.stock_price * 1.3,
        25,
        dtype=np.float32,
    )
    points = []
    model_loaded = load_artifacts() is not None

    for stock_price in stock_prices:
        scenario_input = OptionInput(
            stock_price=float(stock_price),
            strike_price=option_input.strike_price,
            time_to_maturity=option_input.time_to_maturity,
            rate=option_input.rate,
            volatility=option_input.volatility,
        )

        exact_price = call_price(
            scenario_input.stock_price,
            scenario_input.strike_price,
            scenario_input.time_to_maturity,
            scenario_input.rate,
            scenario_input.volatility,
        )
        exact_delta = call_delta(
            scenario_input.stock_price,
            scenario_input.strike_price,
            scenario_input.time_to_maturity,
            scenario_input.rate,
            scenario_input.volatility,
        )
        exact_vega = call_vega(
            scenario_input.stock_price,
            scenario_input.strike_price,
            scenario_input.time_to_maturity,
            scenario_input.rate,
            scenario_input.volatility,
        )
        predicted_metrics = predict_metrics(scenario_input)

        points.append(
            SensitivityPoint(
                stock_price=scenario_input.stock_price,
                exact_price=exact_price,
                exact_delta=exact_delta,
                exact_vega=exact_vega,
                predicted_price=predicted_metrics.price if predicted_metrics else None,
                predicted_delta=predicted_metrics.delta if predicted_metrics else None,
                predicted_vega=predicted_metrics.vega if predicted_metrics else None,
            )
        )

    return SensitivityResponse(points=points, model_loaded=model_loaded)


@app.post("/benchmark", response_model=RuntimeMetrics)
def benchmark_runtime(option_input: OptionInput) -> RuntimeMetrics:
    """
    Compare exact Black-Scholes runtime against surrogate model inference runtime.
    """
    exact_start = perf_counter()
    _ = call_price(
        option_input.stock_price,
        option_input.strike_price,
        option_input.time_to_maturity,
        option_input.rate,
        option_input.volatility,
    )
    _ = call_delta(
        option_input.stock_price,
        option_input.strike_price,
        option_input.time_to_maturity,
        option_input.rate,
        option_input.volatility,
    )
    _ = call_vega(
        option_input.stock_price,
        option_input.strike_price,
        option_input.time_to_maturity,
        option_input.rate,
        option_input.volatility,
    )
    exact_runtime_ms = (perf_counter() - exact_start) * 1000

    if load_artifacts() is None:
        return RuntimeMetrics(
            exact_runtime_ms=exact_runtime_ms,
            predicted_runtime_ms=None,
            model_loaded=False,
        )

    predicted_start = perf_counter()
    _ = predict_metrics(option_input)
    predicted_runtime_ms = (perf_counter() - predicted_start) * 1000

    return RuntimeMetrics(
        exact_runtime_ms=exact_runtime_ms,
        predicted_runtime_ms=predicted_runtime_ms,
        model_loaded=True,
    )
