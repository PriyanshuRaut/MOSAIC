"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { DEFAULT_FORECAST_REQUEST } from "@/data/defaults";
import { mosaicApi } from "@/lib/api";
import type {
  AdvisoryRequest,
  AdvisoryResponse,
  ForecastRequest,
  ForecastResponse,
  HealthResponse,
  HistoricalLocation,
  ModelInfo,
} from "@/types/mosaic";

interface MosaicContextValue {
  input: ForecastRequest;
  setInput: React.Dispatch<React.SetStateAction<ForecastRequest>>;
  forecast: ForecastResponse | null;
  advisory: AdvisoryResponse | null;
  health: HealthResponse | null;
  modelInfo: ModelInfo | null;
  locations: HistoricalLocation[];
  loading: boolean;
  advisoryLoading: boolean;
  error: string | null;
  runForecast: () => Promise<void>;
  runAdvisory: (
    values: Omit<AdvisoryRequest, "forecast">
  ) => Promise<void>;
  resetInput: () => void;
}

const MosaicContext = createContext<MosaicContextValue | undefined>(undefined);

export function MosaicProvider({ children }: { children: React.ReactNode }) {
  const [input, setInput] = useState<ForecastRequest>(
    DEFAULT_FORECAST_REQUEST
  );
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [advisory, setAdvisory] = useState<AdvisoryResponse | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [locations, setLocations] = useState<HistoricalLocation[]>([]);
  const [loading, setLoading] = useState(false);
  const [advisoryLoading, setAdvisoryLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void Promise.allSettled([
      mosaicApi.health().then(setHealth),
      mosaicApi.modelInfo().then(setModelInfo),
      mosaicApi.locations().then((response) => setLocations(response.locations)),
    ]);
  }, []);

  const runForecast = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await mosaicApi.predict(input);
      setForecast(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Forecast request failed.");
    } finally {
      setLoading(false);
    }
  }, [input]);

  const runAdvisory = useCallback(
    async (values: Omit<AdvisoryRequest, "forecast">) => {
      setAdvisoryLoading(true);
      setError(null);
      try {
        const response = await mosaicApi.advisory({
          ...values,
          forecast: input,
        });
        setAdvisory(response);
        setForecast(response.forecast);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Advisory request failed.");
      } finally {
        setAdvisoryLoading(false);
      }
    },
    [input]
  );

  const resetInput = useCallback(() => {
    setInput(DEFAULT_FORECAST_REQUEST);
    setForecast(null);
    setAdvisory(null);
    setError(null);
  }, []);

  const value = useMemo<MosaicContextValue>(
    () => ({
      input,
      setInput,
      forecast,
      advisory,
      health,
      modelInfo,
      locations,
      loading,
      advisoryLoading,
      error,
      runForecast,
      runAdvisory,
      resetInput,
    }),
    [
      input,
      forecast,
      advisory,
      health,
      modelInfo,
      locations,
      loading,
      advisoryLoading,
      error,
      runForecast,
      runAdvisory,
      resetInput,
    ]
  );

  return (
    <MosaicContext.Provider value={value}>{children}</MosaicContext.Provider>
  );
}

export function useMosaic() {
  const value = useContext(MosaicContext);
  if (!value) {
    throw new Error("useMosaic must be used inside MosaicProvider.");
  }
  return value;
}
