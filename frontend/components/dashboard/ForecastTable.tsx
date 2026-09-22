import { TARGET_LABELS } from "@/data/defaults";
import { riskTone } from "@/lib/risk";
import type { ForecastResponse, TargetName } from "@/types/mosaic";

const targets: TargetName[] = ["onset", "break", "revival", "heavy_rain"];

export function ForecastTable({
  forecast,
}: {
  forecast: ForecastResponse | null;
}) {
  if (!forecast) {
    return (
      <div className="px-5 py-12 text-center text-xs text-slate-500">
        Run the model to see the week-by-week probability matrix.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[680px] border-collapse text-left">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50/70 text-[10px] font-bold uppercase tracking-[0.08em] text-slate-500">
            <th className="px-5 py-3">Signal</th>
            {forecast.weeks.map((week) => (
              <th key={week.lead_week} className="px-4 py-3">
                Week {week.lead_week}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {targets.map((target) => (
            <tr key={target} className="border-b border-slate-100 last:border-b-0">
              <td className="px-5 py-4 text-xs font-bold text-slate-700">
                {TARGET_LABELS[target]}
              </td>
              {forecast.weeks.map((week) => {
                const result = week.probabilities[target];
                return (
                  <td key={week.lead_week} className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-extrabold text-slate-800">
                        {result.percent.toFixed(1)}%
                      </span>
                      <span
                        className={`rounded-full border px-2 py-0.5 text-[9px] font-bold uppercase tracking-[0.06em] ${riskTone(
                          result.level
                        )}`}
                      >
                        {result.level}
                      </span>
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
