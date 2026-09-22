import type {
  AdvisoryRequest,
  AdvisoryResponse,
  ForecastRequest,
  ForecastResponse,
  HealthResponse,
  LocationsResponse,
  ModelInfo,
} from "@/types/mosaic";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_MOSAIC_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;

    try {
      const body = await response.json();
      message = body.detail ?? JSON.stringify(body);
    } catch {
      // Keep the HTTP status text.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export const mosaicApi = {
  health: () => request<HealthResponse>("/api/health"),
  modelInfo: () => request<ModelInfo>("/api/model-info"),
  locations: () => request<LocationsResponse>("/api/locations"),

  predict: (payload: ForecastRequest) =>
    request<ForecastResponse>("/api/predict", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  advisory: (payload: AdvisoryRequest) =>
    request<AdvisoryResponse>("/api/advisory", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
