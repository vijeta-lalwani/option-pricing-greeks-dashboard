export type OptionInput = {
  stock_price: number;
  strike_price: number;
  time_to_maturity: number;
  rate: number;
  volatility: number;
};

export type OptionMetrics = {
  price: number;
  delta: number;
  vega: number;
};

export type ErrorMetrics = {
  price_abs_error: number;
  delta_abs_error: number;
  vega_abs_error: number;
};

export type AnalyzeResponse = {
  exact: OptionMetrics;
  predicted: OptionMetrics | null;
  error: ErrorMetrics | null;
  model_loaded: boolean;
};

export type SensitivityPoint = {
  stock_price: number;
  exact_price: number;
  predicted_price: number | null;
};

export type SensitivityResponse = {
  points: SensitivityPoint[];
  model_loaded: boolean;
};

export type RuntimeMetrics = {
  exact_runtime_ms: number;
  predicted_runtime_ms: number | null;
  model_loaded: boolean;
};
