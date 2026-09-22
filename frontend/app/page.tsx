"use client";

import {
  ArrowRight,
  CheckCircle2,
  Cpu,
  MapPin,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";

import { ClimateSignals } from "@/components/dashboard/ClimateSignals";
import { ForecastInputForm } from "@/components/dashboard/ForecastInputForm";
import { ForecastTable } from "@/components/dashboard/ForecastTable";
import { ProbabilityCard } from "@/components/dashboard/ProbabilityCard";
import { FourWeekChart } from "@/components/charts/FourWeekChart";
import { useMosaic } from "@/components/providers/MosaicProvider";
import { PageTitle } from "@/components/ui/PageTitle";
import { SectionHeader } from "@/components/ui/SectionHeader";
import type { TargetName } from "@/types/mosaic";

const targets: TargetName[] = ["onset", "break", "revival", "heavy_rain"];

export default function OverviewPage() {
  const { forecast, health, input } = useMosaic();
  const week1 = forecast?.weeks[0];

  return (
    <>
      <PageTitle
        eyebrow="Decision dashboard"
        title="Monsoon intelligence for local agricultural planning"
        description="Review 1–4 week probabilities for sustained onset, break spells, rainfall revival and heavy-rain risk using the trained MOSAIC historical baseline."
        action={
          <Link
            href="/methodology"
            className="mosaic-btn-secondary inline-flex items-center gap-2 text-xs"
          >
            View methodology
            <ArrowRight size={14} />
          </Link>
        }
      />

      <div className="mb-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {targets.map((target) => (
          <ProbabilityCard
            key={target}
            target={target}
            result={week1?.probabilities[target]}
          />
        ))}
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.55fr_0.8fr]">
        <ForecastInputForm />
        <ClimateSignals />
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-[1.45fr_0.95fr]">
        <div className="mosaic-card overflow-hidden">
          <SectionHeader
            title="Four-week probability trajectory"
            description="Probability values are model outputs, not deterministic weather guarantees."
            right={
              forecast ? (
                <span className="rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.07em] text-emerald-700">
                  Latest run
                </span>
              ) : null
            }
          />
          <FourWeekChart forecast={forecast} />
        </div>

        <div className="mosaic-card overflow-hidden">
          <SectionHeader
            title="System context"
            description="What the current prototype is actually running"
          />
          <div className="space-y-0">
            {[
              {
                icon: Cpu,
                title: "Four calibrated ML models",
                body: "Onset, break, revival and heavy-rain classifiers loaded through FastAPI.",
              },
              {
                icon: ShieldCheck,
                title: "Historical hold-out testing",
                body: "Models were evaluated on years later than their training period.",
              },
              {
                icon: MapPin,
                title: `${input.district}, ${input.state}`,
                body: `Current request point: ${input.latitude.toFixed(
                  3
                )}, ${input.longitude.toFixed(3)}`,
              },
              {
                icon: CheckCircle2,
                title: health?.models_loaded
                  ? "Backend models online"
                  : "Backend connection pending",
                body: health?.models_loaded
                  ? "FastAPI reports the trained model files as loaded."
                  : "Start the FastAPI server on port 8000.",
              },
            ].map(({ icon: Icon, title, body }) => (
              <div
                key={title}
                className="flex gap-3 border-b border-slate-100 px-5 py-4 last:border-b-0"
              >
                <div className="mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-[#edf5f5] text-[#0f766e]">
                  <Icon size={16} />
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-700">{title}</div>
                  <p className="mt-1 text-[11px] leading-5 text-slate-500">
                    {body}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mosaic-card mt-5 overflow-hidden">
        <SectionHeader
          title="Week-by-week probability matrix"
          description="Use these probabilities as decision support. The frontend deliberately avoids reducing them to a single yes/no claim."
        />
        <ForecastTable forecast={forecast} />
      </div>

      {forecast?.disclaimer ? (
        <div className="mt-4 rounded-xl border border-slate-200 bg-white px-4 py-3 text-[11px] leading-5 text-slate-500">
          <strong className="text-slate-700">Prototype notice:</strong>{" "}
          {forecast.disclaimer}
        </div>
      ) : null}
    </>
  );
}
