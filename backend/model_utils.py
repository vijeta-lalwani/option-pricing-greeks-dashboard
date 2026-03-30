"""
Training and inference utilities for the neural surrogate model.

The goal is to keep the ML-specific code separate from the API routes and the
analytical formulas.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
import torch.nn as nn


MODEL_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = MODEL_DIR / "option_model.pt"


class OptionPricingNetwork(nn.Module):
    """Simple feedforward model for price, delta, and vega."""

    def __init__(self, input_dim: int = 5, hidden_dim: int = 64, output_dim: int = 3):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.network(inputs)


def save_artifacts(
    model: OptionPricingNetwork,
    feature_mean: np.ndarray,
    feature_std: np.ndarray,
    target_mean: np.ndarray,
    target_std: np.ndarray,
) -> None:
    """Save the trained model and scaling values to disk."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "feature_mean": feature_mean,
            "feature_std": feature_std,
            "target_mean": target_mean,
            "target_std": target_std,
        },
        MODEL_PATH,
    )


def load_artifacts() -> dict | None:
    """Load the trained model and scaling values if they exist."""
    if not MODEL_PATH.exists():
        return None

    checkpoint = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
    model = OptionPricingNetwork()
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    return {
        "model": model,
        "feature_mean": checkpoint["feature_mean"],
        "feature_std": checkpoint["feature_std"],
        "target_mean": checkpoint["target_mean"],
        "target_std": checkpoint["target_std"],
    }


def scale_features(features: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    """Standardize feature values using saved statistics."""
    return (features - mean) / std


def unscale_targets(targets: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    """Convert standardized model outputs back to the original scale."""
    return targets * std + mean
