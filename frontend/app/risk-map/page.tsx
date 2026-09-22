"use client";

import { Layers3, MapPinned } from "lucide-react";
import { useState } from "react";

import { useMosaic } from "@/components/providers/MosaicProvider";
import { RiskMapLoader } from "@/components/map/RiskMapLoader";
import { PageTitle } from "@/components/ui/PageTitle";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { TARGET_LABELS } from "@/data/defaults";
import type { TargetName } from "@/types/mosaic";

const targets: TargetName[] = ["onset", "break", "revival", "heavy_rain"];

export default function RiskMapPage() {
  const { locations, forecast, input } = useMosaic();
  const [target, setTarget] = useState<TargetName>("break");

  const week1 = forecast?.weeks[0]?.probabilities[target];

  return (
    <>
      <PageTitle
        eyebrow="Spatial decision layer"
        title="Risk map"
        description="The map shows the selected forecast point alongside the representative locations used by the current historical baseline. It is not yet a Panchayat-wide interpolated risk surface."
        action={
          <div className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600">
            <MapPinned size={15} />
            {locations.length} historical baseline locations
          </div>
        }
      />

      <div className="grid gap-5 xl:grid-cols-[1.55fr_0.55fr]">
        <div className="mosaic-card overflow-hidden">
          <SectionHeader
            title={`${TARGET_LABELS[target]} • Week 1`}
            description="Selected point is driven by the active MOSAIC model run. Grey markers show historical baseline locations."
            right={
              <div className="flex items-center gap-2">
                <Layers3 size={14} className="text-slate-500" />
                <select
                  className="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-700"
                  value={target}
                  onChange={(event) =>
                    setTarget(event.target.value as TargetName)
                  }
                >
                  {targets.map((value) => (
                    <option key={value} value={value}>
                      {TARGET_LABELS[value]}
                    </option>
                  ))}
                </select>
              </div>
            }
          />
          <div className="min-h-[520px]">
            <RiskMapLoader
              locations={locations}
              forecast={forecast}
              latitude={input.latitude}
              longitude={input.longitude}
              target={target}
            />
          </div>
        </div>

        <div className="space-y-5">
          <div className="mosaic-card p-5">
            <div className="mosaic-label">Selected point</div>
            <div className="mt-2 text-lg font-extrabold text-slate-800">
              {input.district}
            </div>
            <div className="mt-1 text-xs text-slate-500">{input.state}</div>
            <div className="mt-5 border-t border-slate-100 pt-4">
              <div className="text-xs font-bold text-slate-600">
                Week 1 {TARGET_LABELS[target]}
              </div>
              <div className="mt-1 text-3xl font-extrabold tracking-tight text-[#17303d]">
                {week1 ? `${week1.percent.toFixed(1)}%` : "—"}
              </div>
              <div className="mt-1 text-xs font-semibold text-slate-500">
                {week1?.level ?? "Run a forecast first"}
              </div>
            </div>
          </div>

          <div className="mosaic-card p-5">
            <div className="mosaic-label">Resolution note</div>
            <p className="mt-2 text-xs leading-6 text-slate-600">
              Current training inputs use public gridded historical data and ten
              representative Indian locations. This view intentionally does not
              pretend to provide a validated national Panchayat heatmap yet.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
