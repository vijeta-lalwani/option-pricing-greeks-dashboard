# Option Pricing Greeks Dashboard

This project is a small full-stack app for exploring option pricing and risk
sensitivities.

The app is being built in stages:

- exact Black-Scholes call price, delta, and vega
- a React dashboard for interactive input and output display
- a neural network that will approximate the same metrics
- a stock-price sensitivity chart for exact vs predicted price curves
- a runtime comparison panel for exact formulas vs surrogate inference
- delta and vega sensitivity charts for richer risk analysis
- preset example scenarios for faster exploration and demos

## Project Structure

```text
option-pricing-greeks-dashboard/
  backend/
    artifacts/
    black_scholes.py
    main.py
    model_utils.py
    requirements.txt
    schemas.py
    train_model.py
  frontend/
    src/
      App.tsx
      api.ts
      styles.css
      types.ts
```

## Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Test the API

Visit:

- `http://127.0.0.1:8000/docs`

Example request body for `POST /analyze`:

```json
{
  "stock_price": 100,
  "strike_price": 100,
  "time_to_maturity": 1.0,
  "rate": 0.05,
  "volatility": 0.2
}
```

If the neural model has not been trained yet, the API will still return the
exact Black-Scholes outputs and mark `model_loaded` as `false`.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Then open:

- `http://127.0.0.1:5173`

## Train the Neural Model

Once the backend environment is active, run:

```bash
python train_model.py
```

This will save the trained model to:

- `backend/artifacts/option_model.pt`
