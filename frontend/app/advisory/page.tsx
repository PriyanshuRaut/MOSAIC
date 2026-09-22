"use client";

import { Check, Leaf, Loader2, Sprout, TriangleAlert } from "lucide-react";
import { useState } from "react";

import { useMosaic } from "@/components/providers/MosaicProvider";
import { PageTitle } from "@/components/ui/PageTitle";
import { SectionHeader } from "@/components/ui/SectionHeader";

const crops = [
  "Rice",
  "Maize",
  "Soybean",
  "Groundnut",
  "Cotton",
  "Millet",
  "Pulses",
];

const stages = [
  "pre-sowing",
  "sowing",
  "germination",
  "vegetative",
  "flowering",
  "harvest",
] as const;

export default function AdvisoryPage() {
  const {
    runAdvisory,
    advisory,
    advisoryLoading,
    error,
  } = useMosaic();

  const [crop, setCrop] = useState("Rice");
  const [stage, setStage] = useState<(typeof stages)[number]>("pre-sowing");
  const [irrigation, setIrrigation] = useState(false);

  return (
    <>
      <PageTitle
        eyebrow="Expert-system layer"
        title="Crop advisory"
        description="Translate probabilistic monsoon signals into simple agricultural planning guidance using crop stage, irrigation context and the current model input."
      />

      <div className="grid gap-5 xl:grid-cols-[0.62fr_1.38fr]">
        <div className="mosaic-card overflow-hidden">
          <SectionHeader
            title="Advisory configuration"
            description="Prototype rules are not yet ICAR/KVK validated."
          />
          <div className="space-y-4 p-5">
            <label className="block">
              <span className="mb-1.5 block text-[11px] font-bold text-slate-600">
                Crop
              </span>
              <select
                className="mosaic-input text-sm"
                value={crop}
                onChange={(event) => setCrop(event.target.value)}
              >
                {crops.map((value) => (
                  <option key={value}>{value}</option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="mb-1.5 block text-[11px] font-bold text-slate-600">
                Crop stage
              </span>
              <select
                className="mosaic-input text-sm"
                value={stage}
                onChange={(event) =>
                  setStage(event.target.value as (typeof stages)[number])
                }
              >
                {stages.map((value) => (
                  <option key={value} value={value}>
                    {value.replace("-", " ")}
                  </option>
                ))}
              </select>
            </label>

            <label className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-4 py-3.5">
              <span>
                <span className="block text-xs font-bold text-slate-700">
                  Protective irrigation
                </span>
                <span className="mt-1 block text-[11px] text-slate-500">
                  Available if a dry spell develops
                </span>
              </span>
              <input
                type="checkbox"
                checked={irrigation}
                onChange={(event) => setIrrigation(event.target.checked)}
                className="h-4 w-4 accent-[#0f766e]"
              />
            </label>

            {error ? (
              <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-xs font-medium text-red-700">
                {error}
              </div>
            ) : null}

            <button
              type="button"
              className="mosaic-btn-primary flex w-full items-center justify-center gap-2 text-sm"
              disabled={advisoryLoading}
              onClick={() =>
                void runAdvisory({
                  crop,
                  crop_stage: stage,
                  irrigation_available: irrigation,
                  language: "English",
                })
              }
            >
              {advisoryLoading ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Sprout size={16} />
              )}
              {advisoryLoading ? "Generating..." : "Generate advisory"}
            </button>
          </div>
        </div>

        <div className="space-y-5">
          <div className="mosaic-card overflow-hidden">
            <SectionHeader
              title="Decision summary"
              description="Action text is derived from the probability output, not generated independently."
            />
            {advisory ? (
              <div className="p-5">
                <div className="flex gap-3 rounded-xl border border-[#cde5df] bg-[#f1f9f7] p-4">
                  <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-white text-[#0f766e] shadow-sm">
                    <Leaf size={18} />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-[#1f4d47]">
                      {advisory.crop} •{" "}
                      {advisory.crop_stage.replace("-", " ")}
                    </div>
                    <p className="mt-1.5 text-sm leading-6 text-[#315f59]">
                      {advisory.overall_advisory}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="grid min-h-[170px] place-items-center px-6 text-center">
                <div>
                  <Sprout
                    size={28}
                    className="mx-auto text-slate-300"
                  />
                  <div className="mt-3 text-sm font-bold text-slate-600">
                    No advisory generated
                  </div>
                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    Configure the crop and stage, then run the expert-system
                    endpoint.
                  </p>
                </div>
              </div>
            )}
          </div>

          {advisory ? (
            <div className="mosaic-card overflow-hidden">
              <SectionHeader
                title="Weekly action plan"
                description="Week-specific actions derived from the forecast probabilities."
              />
              <div>
                {advisory.weekly_advisories.map((week) => (
                  <div
                    key={week.lead_week}
                    className="border-b border-slate-100 p-5 last:border-b-0"
                  >
                    <div className="flex items-start gap-4">
                      <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-slate-200 bg-slate-50 text-xs font-extrabold text-slate-700">
                        W{week.lead_week}
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-700">
                          {week.risk_summary}
                        </div>
                        <div className="mt-2 space-y-2">
                          {week.actions.map((action) => (
                            <div
                              key={action}
                              className="flex items-start gap-2 text-xs leading-5 text-slate-600"
                            >
                              <Check
                                size={14}
                                className="mt-0.5 shrink-0 text-[#0f766e]"
                              />
                              {action}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : null}

          <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3">
            <TriangleAlert
              size={16}
              className="mt-0.5 shrink-0 text-amber-700"
            />
            <p className="text-[11px] leading-5 text-amber-800">
              Prototype agronomic decision support only. Rules must be validated
              with crop experts and official agricultural advisories before
              public operational use.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
