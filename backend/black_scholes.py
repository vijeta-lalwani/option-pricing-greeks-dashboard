"""
Black-Scholes formulas for a European call option.

This module keeps the finance logic separate from the API code so the
application is easier to test, explain, and extend later.
"""

from math import erf, exp, log, pi, sqrt


def normal_cdf(x: float) -> float:
    """Return the standard normal cumulative distribution function."""
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def normal_pdf(x: float) -> float:
    """Return the standard normal probability density function."""
    return (1.0 / sqrt(2.0 * pi)) * exp(-0.5 * x * x)


def compute_d1(stock_price: float, strike_price: float, time_to_maturity: float, rate: float, volatility: float) -> float:
    """Compute d1 from the Black-Scholes formula."""
    return (
        log(stock_price / strike_price)
        + (rate + 0.5 * volatility * volatility) * time_to_maturity
    ) / (volatility * sqrt(time_to_maturity))


def compute_d2(d1: float, time_to_maturity: float, volatility: float) -> float:
    """Compute d2 from d1."""
    return d1 - volatility * sqrt(time_to_maturity)


def call_price(stock_price: float, strike_price: float, time_to_maturity: float, rate: float, volatility: float) -> float:
    """Return the Black-Scholes price of a European call option."""
    d1 = compute_d1(stock_price, strike_price, time_to_maturity, rate, volatility)
    d2 = compute_d2(d1, time_to_maturity, volatility)
    return stock_price * normal_cdf(d1) - strike_price * exp(-rate * time_to_maturity) * normal_cdf(d2)


def call_delta(stock_price: float, strike_price: float, time_to_maturity: float, rate: float, volatility: float) -> float:
    """Return the delta of a European call option."""
    d1 = compute_d1(stock_price, strike_price, time_to_maturity, rate, volatility)
    return normal_cdf(d1)


def call_vega(stock_price: float, strike_price: float, time_to_maturity: float, rate: float, volatility: float) -> float:
    """Return the vega of a European call option."""
    d1 = compute_d1(stock_price, strike_price, time_to_maturity, rate, volatility)
    return stock_price * normal_pdf(d1) * sqrt(time_to_maturity)
