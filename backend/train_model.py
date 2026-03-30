"""
Train a neural network to approximate Black-Scholes price, delta, and vega.
"""

from __future__ import annotations

import random

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from black_scholes import call_delta, call_price, call_vega
from model_utils import OptionPricingNetwork, save_artifacts


RANDOM_SEED = 42
N_SAMPLES = 25000
BATCH_SIZE = 256
EPOCHS = 120
LEARNING_RATE = 1e-3


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def generate_dataset(n_samples: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Create synthetic Black-Scholes inputs and targets.

    Inputs: S, K, T, r, sigma
    Targets: price, delta, vega
    """
    stock_price = np.random.uniform(50, 150, n_samples)
    strike_price = np.random.uniform(50, 150, n_samples)
    time_to_maturity = np.random.uniform(0.1, 2.0, n_samples)
    rate = np.random.uniform(0.0, 0.1, n_samples)
    volatility = np.random.uniform(0.1, 0.6, n_samples)

    features = np.column_stack(
        [stock_price, strike_price, time_to_maturity, rate, volatility]
    ).astype(np.float32)

    price = np.array(
        [
            call_price(s, k, t, r, sigma)
            for s, k, t, r, sigma in features
        ],
        dtype=np.float32,
    )
    delta = np.array(
        [
            call_delta(s, k, t, r, sigma)
            for s, k, t, r, sigma in features
        ],
        dtype=np.float32,
    )
    vega = np.array(
        [
            call_vega(s, k, t, r, sigma)
            for s, k, t, r, sigma in features
        ],
        dtype=np.float32,
    )

    targets = np.column_stack([price, delta, vega]).astype(np.float32)
    return features, targets


def compute_scaling(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Compute mean and standard deviation with a small floor for stability."""
    mean = values.mean(axis=0)
    std = values.std(axis=0)
    std = np.where(std < 1e-8, 1.0, std)
    return mean, std


def main() -> None:
    set_seed(RANDOM_SEED)

    print("Generating synthetic training data...")
    features, targets = generate_dataset(N_SAMPLES)

    feature_mean, feature_std = compute_scaling(features)
    target_mean, target_std = compute_scaling(targets)

    features_scaled = (features - feature_mean) / feature_std
    targets_scaled = (targets - target_mean) / target_std

    dataset = TensorDataset(
        torch.tensor(features_scaled, dtype=torch.float32),
        torch.tensor(targets_scaled, dtype=torch.float32),
    )
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    model = OptionPricingNetwork()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    loss_function = nn.MSELoss()

    print("Training neural surrogate model...")
    for epoch in range(EPOCHS):
        total_loss = 0.0

        for batch_inputs, batch_targets in loader:
            optimizer.zero_grad()
            predictions = model(batch_inputs)
            loss = loss_function(predictions, batch_targets)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * batch_inputs.size(0)

        average_loss = total_loss / len(loader.dataset)
        if (epoch + 1) % 20 == 0 or epoch == 0:
            print(f"Epoch {epoch + 1:3d}/{EPOCHS} - Loss: {average_loss:.6f}")

    save_artifacts(model, feature_mean, feature_std, target_mean, target_std)
    print("Saved trained model artifacts to backend/artifacts/option_model.pt")


if __name__ == "__main__":
    main()
