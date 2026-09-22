import {
  CloudLightning,
  CloudRainWind,
  Droplets,
  Sunrise,
} from "lucide-react";

import { riskTone, targetCopy } from "@/lib/risk";
import type { ProbabilityResult, TargetName } from "@/types/mosaic";

const icons = {
  onset: Sunrise,
  break: CloudRainWind,
  revival: Droplets,
  heavy_rain: CloudLightning,
};

export function ProbabilityCard({
  target,
  result,
}: {
  target: TargetName;
  result?: ProbabilityResult;
}) {
  const Icon = icons[target];
  const copy = targetCopy[target];

  return (
    <div className="mosaic-card p-4.5">
      <div className="flex items-start justify-between gap-3">
        <div className="grid h-9 w-9 place-items-center rounded-lg border border-slate-200 bg-slate-50 text-[#315b6b]">
          <Icon size={18} />
        </div>
        {result ? (
          <span
            className={`rounded-full border px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.08em] ${riskTone(
              result.level
            )}`}
          >
            {result.level}
          </span>
        ) : (
          <span className="rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.08em] text-slate-500">
            Awaiting run
          </span>
        )}
      </div>

      <div className="mt-4">
        <div className="text-[13px] font-bold text-slate-700">{copy.title}</div>
        <div className="mt-1 flex items-end gap-1">
          <span className="text-[31px] font-extrabold tracking-tight text-[#17303d]">
            {result ? result.percent.toFixed(1) : "—"}
          </span>
          {result ? (
            <span className="mb-1.5 text-sm font-bold text-slate-500">%</span>
          ) : null}
        </div>
        <p className="mt-1 min-h-10 text-[11px] leading-5 text-slate-500">
          {copy.subtitle}
        </p>
      </div>
    </div>
  );
}
