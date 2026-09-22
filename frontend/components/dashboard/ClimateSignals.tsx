"use client";

import { RadioTower } from "lucide-react";

import { useMosaic } from "@/components/providers/MosaicProvider";

function Signal({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="border-b border-slate-100 px-5 py-3.5 last:border-b-0">
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="text-xs font-bold text-slate-700">{label}</div>
          <div className="mt-1 text-[11px] text-slate-500">{detail}</div>
        </div>
        <div className="font-mono text-sm font-bold text-[#244957]">{value}</div>
      </div>
    </div>
  );
}

export function ClimateSignals() {
  const { input } = useMosaic();

  return (
    <div className="mosaic-card overflow-hidden">
      <div className="mosaic-card-header flex items-center gap-2 px-5 py-4">
        <RadioTower size={16} className="text-[#0f766e]" />
        <div>
          <h2 className="text-sm font-bold text-slate-800">
            Climate signal snapshot
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            Inputs supplied to the current inference request
          </p>
        </div>
      </div>

      <Signal
        label="ENSO"
        value={input.enso.toFixed(2)}
        detail="Niño 3.4 anomaly input"
      />
      <Signal
        label="IOD"
        value={input.iod.toFixed(2)}
        detail="Indian Ocean Dipole index"
      />
      <Signal
        label="MJO"
        value={`P${input.mjo_phase} / ${input.mjo_amplitude.toFixed(2)}`}
        detail="Phase / amplitude"
      />
      <Signal
        label="7-day rainfall"
        value={`${input.rainfall_7d.toFixed(1)} mm`}
        detail={`${input.rainy_days_7d} rainy days in the previous week`}
      />
      <Signal
        label="Soil moisture"
        value={input.soil_moisture.toFixed(2)}
        detail="Current root-zone proxy input"
      />
    </div>
  );
}
