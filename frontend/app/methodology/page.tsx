import {
  BrainCircuit,
  Database,
  GitBranch,
  Leaf,
  Map,
  RadioTower,
} from "lucide-react";

import { PageTitle } from "@/components/ui/PageTitle";
import { SectionHeader } from "@/components/ui/SectionHeader";

const steps = [
  {
    icon: Database,
    title: "Historical state",
    body: "Past rainfall windows, soil moisture, humidity, temperature and wind describe the local atmospheric state.",
  },
  {
    icon: RadioTower,
    title: "Teleconnections",
    body: "ENSO, IOD and daily MJO/RMM signals add planetary-scale monsoon context.",
  },
  {
    icon: BrainCircuit,
    title: "Four ML models",
    body: "Separate calibrated classifiers estimate onset, break, revival and heavy-rain probabilities.",
  },
  {
    icon: GitBranch,
    title: "Lead-week inference",
    body: "The same issue-date state is evaluated for Weeks 1–4 using the trained lead-week feature.",
  },
  {
    icon: Map,
    title: "Decision layer",
    body: "Probabilities are presented spatially and numerically without pretending to be deterministic guarantees.",
  },
  {
    icon: Leaf,
    title: "Agronomic rules",
    body: "Crop stage and irrigation context convert risk probabilities into prototype actions.",
  },
];

export default function MethodologyPage() {
  return (
    <>
      <PageTitle
        eyebrow="Technical design"
        title="How MOSAIC turns climate signals into farm decisions"
        description="The current system is a historical-data research baseline. The interface keeps the distinction between model output, agricultural rules and future operational data sources explicit."
      />

      <div className="mosaic-card overflow-hidden">
        <SectionHeader
          title="End-to-end workflow"
          description="Current working pipeline"
        />
        <div className="mosaic-grid grid gap-3 p-5 md:grid-cols-2 xl:grid-cols-3">
          {steps.map(({ icon: Icon, title, body }, index) => (
            <div
              key={title}
              className="rounded-xl border border-slate-200 bg-white p-4"
            >
              <div className="flex items-center justify-between">
                <div className="grid h-9 w-9 place-items-center rounded-lg bg-[#eef6f5] text-[#0f766e]">
                  <Icon size={17} />
                </div>
                <div className="text-[10px] font-extrabold tracking-[0.1em] text-slate-300">
                  0{index + 1}
                </div>
              </div>
              <h3 className="mt-4 text-sm font-bold text-slate-800">{title}</h3>
              <p className="mt-1.5 text-xs leading-6 text-slate-500">{body}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-2">
        <div className="mosaic-card overflow-hidden">
          <SectionHeader
            title="Historical data currently used"
            description="Baseline model inputs"
          />
          <div className="p-5">
            <div className="grid grid-cols-2 gap-2 text-xs">
              {[
                "Rainfall 1/3/7/14/30 day",
                "Rainfall anomaly",
                "Rainy / dry day counts",
                "Root-zone soil moisture",
                "Humidity",
                "Temperature",
                "Wind speed",
                "ENSO",
                "IOD",
                "MJO phase / amplitude",
                "RMM1 / RMM2",
                "Latitude / longitude",
              ].map((item) => (
                <div
                  key={item}
                  className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 text-slate-600"
                >
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mosaic-card overflow-hidden">
          <SectionHeader
            title="Planned operational upgrades"
            description="Not presented as already implemented"
          />
          <div className="divide-y divide-slate-100">
            {[
              "Historical NCMRWF/IMD hindcasts as genuine forecast features",
              "Higher-resolution rainfall and verified administrative boundaries",
              "Geographical hold-out validation across unseen regions",
              "Automated live feature ingestion",
              "Crop rules validated with ICAR/KVK/state agriculture experts",
              "Regional-language delivery over approved SMS/WhatsApp gateways",
            ].map((item, index) => (
              <div key={item} className="flex gap-3 px-5 py-3.5">
                <span className="grid h-6 w-6 shrink-0 place-items-center rounded-md bg-slate-100 text-[10px] font-extrabold text-slate-600">
                  {index + 1}
                </span>
                <span className="text-xs leading-5 text-slate-600">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
