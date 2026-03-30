import { useState, type FormEvent } from "react";

import { analyzeOption, fetchRuntimeMetrics, fetchSensitivity } from "./api";
import { InputField } from "./components/InputField";
import { MetricCard } from "./components/MetricCard";
import { SensitivityChart } from "./components/SensitivityChart";
import type {
  AnalyzeResponse,
  OptionInput,
  RuntimeMetrics,
  SensitivityResponse
} from "./types";

const initialInput: OptionInput = {
  stock_price: 100,
  strike_price: 100,
  time_to_maturity: 1,
  rate: 0.05,
  volatility: 0.2
};

export default function App() {
  const [formValues, setFormValues] = useState<OptionInput>(initialInput);
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [sensitivity, setSensitivity] = useState<SensitivityResponse | null>(null);
  const [runtimeMetrics, setRuntimeMetrics] = useState<RuntimeMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  function handleInputChange(name: string, value: number) {
    setFormValues((currentValues) => ({
      ...currentValues,
      [name]: value
    }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setErrorMessage("");

    try {
      const [analysisResult, sensitivityResult, runtimeResult] = await Promise.all([
        analyzeOption(formValues),
        fetchSensitivity(formValues),
        fetchRuntimeMetrics(formValues)
      ]);
      setAnalysis(analysisResult);
      setSensitivity(sensitivityResult);
      setRuntimeMetrics(runtimeResult);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="hero">
        <p className="eyebrow">Option Pricing + Greeks Dashboard</p>
        <h1>Explore Black-Scholes outputs with a simple interactive interface.</h1>
        <p className="hero-copy">
          This version computes the exact call option price, delta, and vega, and it is
          already structured to compare those outputs against a neural surrogate model.
        </p>
      </section>

      <div className="dashboard-grid">
        <section className="panel">
          <h2>Option Inputs</h2>
          <form onSubmit={handleSubmit} className="form-grid">
            <InputField
              label="Stock Price (S)"
              name="stock_price"
              value={formValues.stock_price}
              onChange={handleInputChange}
            />
            <InputField
              label="Strike Price (K)"
              name="strike_price"
              value={formValues.strike_price}
              onChange={handleInputChange}
            />
            <InputField
              label="Time to Maturity (T)"
              name="time_to_maturity"
              value={formValues.time_to_maturity}
              onChange={handleInputChange}
            />
            <InputField
              label="Risk-Free Rate (r)"
              name="rate"
              value={formValues.rate}
              onChange={handleInputChange}
            />
            <InputField
              label="Volatility (sigma)"
              name="volatility"
              value={formValues.volatility}
              onChange={handleInputChange}
            />

            <button type="submit" className="submit-button" disabled={loading}>
              {loading ? "Calculating..." : "Calculate Metrics"}
            </button>
          </form>
        </section>

        <section className="panel">
          <h2>Exact Black-Scholes Outputs</h2>
          {errorMessage ? <p className="error-message">{errorMessage}</p> : null}

          {analysis ? (
            <div className="metrics-grid">
              <MetricCard label="Call Price" value={analysis.exact.price} />
              <MetricCard label="Delta" value={analysis.exact.delta} />
              <MetricCard label="Vega" value={analysis.exact.vega} />
            </div>
          ) : (
            <p className="empty-state">
              Enter option parameters and calculate the metrics to see results here.
            </p>
          )}
        </section>
      </div>

      <div className="dashboard-grid lower-grid">
        <section className="panel">
          <h2>Neural Approximation</h2>
          {analysis?.model_loaded && analysis.predicted ? (
            <div className="metrics-grid">
              <MetricCard label="Predicted Price" value={analysis.predicted.price} accent="gold" />
              <MetricCard label="Predicted Delta" value={analysis.predicted.delta} accent="gold" />
              <MetricCard label="Predicted Vega" value={analysis.predicted.vega} accent="gold" />
            </div>
          ) : (
            <p className="empty-state">
              Train the model in the backend to unlock predicted price, delta, and vega.
            </p>
          )}
        </section>

        <section className="panel">
          <h2>Error Comparison</h2>
          {analysis?.model_loaded && analysis.error ? (
            <div className="metrics-grid">
              <MetricCard label="Price Error" value={analysis.error.price_abs_error} />
              <MetricCard label="Delta Error" value={analysis.error.delta_abs_error} />
              <MetricCard label="Vega Error" value={analysis.error.vega_abs_error} />
            </div>
          ) : (
            <p className="empty-state">
              Once the neural model is trained, this panel will show how close the predicted
              values are to the exact Black-Scholes outputs.
            </p>
          )}
        </section>
      </div>

      <section className="panel chart-panel">
        <h2>Price Sensitivity Chart</h2>
        {sensitivity ? (
          <>
            <p className="chart-copy">
              This chart varies the stock price while keeping the other parameters fixed,
              which makes it easy to compare the exact pricing curve with the neural approximation.
            </p>
            <SensitivityChart
              points={sensitivity.points}
              showPredicted={sensitivity.model_loaded}
            />
          </>
        ) : (
          <p className="empty-state">
            Calculate the metrics first to generate a stock-price sensitivity curve.
          </p>
        )}
      </section>

      <section className="panel chart-panel">
        <h2>Runtime Comparison</h2>
        {runtimeMetrics ? (
          <>
            <p className="chart-copy">
              This compares the time needed to compute the exact Black-Scholes metrics
              against the neural surrogate inference for the same input.
            </p>
            <div className="metrics-grid runtime-grid">
              <MetricCard label="Exact Runtime (ms)" value={runtimeMetrics.exact_runtime_ms} />
              {runtimeMetrics.model_loaded && runtimeMetrics.predicted_runtime_ms !== null ? (
                <MetricCard
                  label="Predicted Runtime (ms)"
                  value={runtimeMetrics.predicted_runtime_ms}
                  accent="gold"
                />
              ) : (
                <p className="empty-state runtime-note">
                  Train the model to compare exact runtime against surrogate inference time.
                </p>
              )}
            </div>
          </>
        ) : (
          <p className="empty-state">
            Calculate the metrics first to see the runtime comparison.
          </p>
        )}
      </section>
    </main>
  );
}
