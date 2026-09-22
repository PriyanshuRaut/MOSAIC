"use client";

import { CalendarRange } from "lucide-react";

import { FourWeekChart } from "@/components/charts/FourWeekChart";
import { ForecastInputForm } from "@/components/dashboard/ForecastInputForm";
import { ForecastTable } from "@/components/dashboard/ForecastTable";
import { ProbabilityCard } from "@/components/dashboard/ProbabilityCard";
import { useMosaic } from "@/components/providers/MosaicProvider";
import { PageTitle } from "@/components/ui/PageTitle";
import { SectionHeader } from "@/components/ui/SectionHeader";
import type { TargetName } from "@/types/mosaic";

const targets: TargetName[] = ["onset", "break", "revival", "heavy_rain"];

export default function ForecastPage() {
  const { forecast } = useMosaic();

  return (
    <>
      <PageTitle
        eyebrow="1–4 week outlook"
        title="Probabilistic monsoon forecast"
        description="Run all four MOSAIC classifiers on a common atmospheric and local-state snapshot, then compare how risk changes from Week 1 through Week 4."
        action={
          <div className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600">
            <CalendarRange size={15} />
            7–28 day lead horizon
          </div>
        }
      />

      <ForecastInputForm />

      <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {targets.map((target) => (
          <ProbabilityCard
            key={target}
            target={target}
            result={forecast?.weeks[0]?.probabilities[target]}
          />
        ))}
      </div>

      <div className="mosaic-card mt-5 overflow-hidden">
        <SectionHeader
          title="Probability trajectory"
          description="Week-level variation across the four monsoon event models."
        />
        <FourWeekChart forecast={forecast} />
      </div>

      <div className="mosaic-card mt-5 overflow-hidden">
        <SectionHeader
          title="Detailed forecast matrix"
          description="Raw probability and qualitative risk band for every lead week."
        />
        <ForecastTable forecast={forecast} />
      </div>
    </>
  );
}
