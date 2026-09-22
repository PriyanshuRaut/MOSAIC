"use client";

import { BarChart3, Database, FlaskConical, ShieldCheck } from "lucide-react";

import { useMosaic } from "@/components/providers/MosaicProvider";
import { PageTitle } from "@/components/ui/PageTitle";
import { SectionHeader } from "@/components/ui/SectionHeader";

const targetNames = ["onset", "break", "revival", "heavy_rain"] as const;

function readMetric(
  evaluation: Record<string, unknown> | undefined,
  target: string,
  key: string
): number | null {
  if (!evaluation) return null;

  const targetNode =
    (evaluation[target] as Record<string, unknown> | undefined) ??
    ((evaluation.targets as Record<string, unknown> | undefined)?.[
      target
    ] as Record<string, unknown> | undefined);

  if (!targetNode) return null;

  const direct = targetNode[key];
  if (typeof direct === "number") return direct;

  const overall = targetNode.overall as Record<string, unknown> | undefined;
  const nested = overall?.[key];
  return typeof nested === "number" ? nested : null;
}

function formatMetric(value: number | null, digits = 3) {
  return value === null ? "—" : value.toFixed(digits);
}

export default function AnalyticsPage() {
  const { modelInfo } = useMosaic();
  const evaluation = modelInfo?.evaluation;

  return (
    <>
      <PageTitle
        eyebrow="Validation"
        title="Historical model analytics"
        description="Review the backend's evaluation metadata rather than hard-coding performance claims into the interface."
      />

      <div className="mb-5 grid gap-3 md:grid-cols-3">
        {[
          {
            icon: Database,
            label: "Historical window",
            value: "2001–2025",
            detail: "Public historical climate and weather baseline",
          },
          {
            icon: FlaskConical,
            label: "Held-out test",
            value: "2023–2025",
            detail: "Later years excluded from model fitting",
          },
          {
            icon: ShieldCheck,
            label: "Model family",
            value: "4 classifiers",
            detail: "Onset, break, revival and heavy rain",
          },
        ].map(({ icon: Icon, label, value, detail }) => (
          <div key={label} className="mosaic-card p-5">
            <div className="flex items-center gap-2 text-slate-500">
              <Icon size={16} />
              <span className="mosaic-label">{label}</span>
            </div>
            <div className="mt-3 text-2xl font-extrabold tracking-tight text-[#17303d]">
              {value}
            </div>
            <div className="mt-1 text-xs text-slate-500">{detail}</div>
          </div>
        ))}
      </div>

      <div className="mosaic-card overflow-hidden">
        <SectionHeader
          title="Evaluation metrics from backend"
          description="Values are read from ml/models/evaluation.json through /api/model-info. A dash means the current JSON structure did not expose that metric at the expected key."
          right={<BarChart3 size={17} className="text-slate-500" />}
        />

        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-left text-[10px] font-bold uppercase tracking-[0.08em] text-slate-500">
                <th className="px-5 py-3">Target</th>
                <th className="px-4 py-3">ROC-AUC</th>
                <th className="px-4 py-3">Average precision</th>
                <th className="px-4 py-3">Brier score</th>
                <th className="px-4 py-3">Brier skill</th>
                <th className="px-4 py-3">F1</th>
              </tr>
            </thead>
            <tbody>
              {targetNames.map((target) => (
                <tr
                  key={target}
                  className="border-b border-slate-100 text-sm last:border-b-0"
                >
                  <td className="px-5 py-4 font-bold capitalize text-slate-700">
                    {target.replace("_", " ")}
                  </td>
                  <td className="px-4 py-4 font-mono text-xs text-slate-700">
                    {formatMetric(readMetric(evaluation, target, "roc_auc"))}
                  </td>
                  <td className="px-4 py-4 font-mono text-xs text-slate-700">
                    {formatMetric(
                      readMetric(evaluation, target, "average_precision")
                    )}
                  </td>
                  <td className="px-4 py-4 font-mono text-xs text-slate-700">
                    {formatMetric(
                      readMetric(evaluation, target, "brier_score"),
                      4
                    )}
                  </td>
                  <td className="px-4 py-4 font-mono text-xs text-slate-700">
                    {formatMetric(
                      readMetric(
                        evaluation,
                        target,
                        "brier_skill_score_vs_climatology"
                      ),
                      4
                    )}
                  </td>
                  <td className="px-4 py-4 font-mono text-xs text-slate-700">
                    {formatMetric(readMetric(evaluation, target, "f1"))}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {modelInfo?.limitations?.length ? (
        <div className="mosaic-card mt-5 overflow-hidden">
          <SectionHeader
            title="Current limitations"
            description="These are exposed directly by the backend."
          />
          <div className="grid gap-3 p-5 md:grid-cols-2">
            {modelInfo.limitations.map((item) => (
              <div
                key={item}
                className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs leading-5 text-slate-600"
              >
                {item}
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </>
  );
}
