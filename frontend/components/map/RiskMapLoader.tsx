"use client";

import dynamic from "next/dynamic";

export const RiskMapLoader = dynamic(
  () => import("@/components/map/RiskMap").then((module) => module.RiskMap),
  {
    ssr: false,
    loading: () => (
      <div className="grid min-h-[520px] place-items-center bg-slate-50 text-sm font-semibold text-slate-500">
        Loading spatial view...
      </div>
    ),
  }
);
