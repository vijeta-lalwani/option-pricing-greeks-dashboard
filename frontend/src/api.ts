import type {
  AnalyzeResponse,
  OptionInput,
  RuntimeMetrics,
  SensitivityResponse
} from "./types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function analyzeOption(input: OptionInput): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(input)
  });

  if (!response.ok) {
    throw new Error("Unable to fetch option metrics from the API.");
  }

  return response.json();
}

export async function fetchSensitivity(input: OptionInput): Promise<SensitivityResponse> {
  const response = await fetch(`${API_BASE_URL}/sensitivity`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(input)
  });

  if (!response.ok) {
    throw new Error("Unable to fetch the sensitivity curve from the API.");
  }

  return response.json();
}

export async function fetchRuntimeMetrics(input: OptionInput): Promise<RuntimeMetrics> {
  const response = await fetch(`${API_BASE_URL}/benchmark`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(input)
  });

  if (!response.ok) {
    throw new Error("Unable to fetch runtime metrics from the API.");
  }

  return response.json();
}
