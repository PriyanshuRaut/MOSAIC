"use client";

import { RotateCcw, Sparkles } from "lucide-react";

import { useMosaic } from "@/components/providers/MosaicProvider";
import type { ForecastRequest } from "@/types/mosaic";

function Field({
  label,
  value,
  onChange,
  type = "number",
  step = "any",
}: {
  label: string;
  value: string | number;
  onChange: (value: string) => void;
  type?: "number" | "text" | "date";
  step?: string;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-[11px] font-bold text-slate-600">
        {label}
      </span>
      <input
        className="mosaic-input text-sm"
        type={type}
        step={type === "number" ? step : undefined}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

export function ForecastInputForm({ compact = false }: { compact?: boolean }) {
  const {
    input,
    setInput,
    loading,
    runForecast,
    resetInput,
    error,
  } = useMosaic();

  const updateText = (
    key: keyof ForecastRequest,
    value: string
  ) => {
    setInput((current) => ({ ...current, [key]: value }));
  };

  const updateNumber = (
    key: keyof ForecastRequest,
    value: string
  ) => {
    setInput((current) => ({
      ...current,
      [key]: value === "" ? 0 : Number(value),
    }));
  };

  return (
    <div className="mosaic-card overflow-hidden">
      <div className="mosaic-card-header flex items-center justify-between gap-4 px-5 py-4">
        <div>
          <h2 className="text-sm font-bold text-slate-800">
            Forecast configuration
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            Current prototype uses manually supplied observed-state features.
          </p>
        </div>
        <span className="rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.08em] text-amber-800">
          Sample input loaded
        </span>
      </div>

      <div className="p-5">
        <div className={`grid gap-3 ${compact ? "md:grid-cols-2" : "md:grid-cols-4"}`}>
          <Field
            label="State"
            type="text"
            value={input.state}
            onChange={(value) => updateText("state", value)}
          />
          <Field
            label="District"
            type="text"
            value={input.district}
            onChange={(value) => updateText("district", value)}
          />
          <Field
            label="Block"
            type="text"
            value={input.block}
            onChange={(value) => updateText("block", value)}
          />
          <Field
            label="Panchayat / pilot"
            type="text"
            value={input.panchayat}
            onChange={(value) => updateText("panchayat", value)}
          />
          <Field
            label="Latitude"
            value={input.latitude}
            onChange={(value) => updateNumber("latitude", value)}
          />
          <Field
            label="Longitude"
            value={input.longitude}
            onChange={(value) => updateNumber("longitude", value)}
          />
          <Field
            label="Issue date"
            type="date"
            value={input.date}
            onChange={(value) => updateText("date", value)}
          />
          <Field
            label="Rainfall anomaly %"
            value={input.rainfall_anomaly_pct}
            onChange={(value) => updateNumber("rainfall_anomaly_pct", value)}
          />
        </div>

        <details className="mt-4 rounded-xl border border-slate-200 bg-slate-50/60">
          <summary className="cursor-pointer select-none px-4 py-3 text-xs font-bold text-slate-700">
            Advanced weather, soil and teleconnection inputs
          </summary>
          <div className="grid gap-3 border-t border-slate-200 p-4 md:grid-cols-3 xl:grid-cols-4">
            {[
              ["Rainfall 1d (mm)", "rainfall_1d"],
              ["Rainfall 3d (mm)", "rainfall_3d"],
              ["Rainfall 7d (mm)", "rainfall_7d"],
              ["Rainfall 14d (mm)", "rainfall_14d"],
              ["Rainfall 30d (mm)", "rainfall_30d"],
              ["Rainy days, 7d", "rainy_days_7d"],
              ["Dry days, 7d", "dry_days_7d"],
              ["Soil moisture", "soil_moisture"],
              ["Soil moisture 7d", "soil_moisture_7d_mean"],
              ["Humidity %", "humidity"],
              ["Humidity 7d %", "humidity_7d_mean"],
              ["Temperature °C", "temperature_c"],
              ["Temperature 7d °C", "temperature_7d_mean"],
              ["Wind m/s", "wind_speed_ms"],
              ["Wind 7d m/s", "wind_7d_mean"],
              ["ENSO", "enso"],
              ["IOD", "iod"],
              ["MJO phase", "mjo_phase"],
              ["MJO amplitude", "mjo_amplitude"],
              ["RMM1", "rmm1"],
              ["RMM2", "rmm2"],
            ].map(([label, key]) => (
              <Field
                key={key}
                label={label}
                value={input[key as keyof ForecastRequest] as number}
                onChange={(value) =>
                  updateNumber(key as keyof ForecastRequest, value)
                }
              />
            ))}
          </div>
        </details>

        {error ? (
          <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-xs font-medium text-red-700">
            {error}
          </div>
        ) : null}

        <div className="mt-5 flex flex-wrap gap-2.5">
          <button
            type="button"
            className="mosaic-btn-primary inline-flex items-center gap-2 text-sm"
            onClick={() => void runForecast()}
            disabled={loading}
          >
            <Sparkles size={16} />
            {loading ? "Running models..." : "Run 4-week forecast"}
          </button>

          <button
            type="button"
            className="mosaic-btn-secondary inline-flex items-center gap-2 text-sm"
            onClick={resetInput}
          >
            <RotateCcw size={15} />
            Reset sample
          </button>
        </div>
      </div>
    </div>
  );
}
