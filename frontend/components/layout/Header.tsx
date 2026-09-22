"use client";

import { Activity, Database, Menu } from "lucide-react";
import { usePathname } from "next/navigation";

import { useMosaic } from "@/components/providers/MosaicProvider";

const titles: Record<string, string> = {
  "/": "Monsoon intelligence overview",
  "/forecast": "Four-week probabilistic forecast",
  "/risk-map": "Spatial risk view",
  "/advisory": "Crop advisory engine",
  "/analytics": "Historical model analytics",
  "/methodology": "Methodology & system design",
};

export function Header() {
  const pathname = usePathname();
  const { health } = useMosaic();

  return (
    <header className="sticky top-0 z-30 border-b border-[#dce5ea] bg-white/94 backdrop-blur">
      <div className="flex min-h-[68px] items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <div className="flex min-w-0 items-center gap-3">
          <button className="grid h-9 w-9 place-items-center rounded-lg border border-slate-200 lg:hidden">
            <Menu size={18} />
          </button>
          <div className="min-w-0">
            <div className="truncate text-[15px] font-bold text-slate-800">
              {titles[pathname] ?? "MOSAIC"}
            </div>
            <div className="mt-0.5 hidden text-[11px] text-slate-500 sm:block">
              Hyperlocal monsoon decision-support prototype
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <div className="hidden items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-600 md:flex">
            <Database size={14} />
            2001–2025 historical baseline
          </div>

          <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600">
            <Activity
              size={14}
              className={
                health?.models_loaded ? "text-emerald-600" : "text-amber-600"
              }
            />
            {health?.models_loaded ? "Models online" : "Checking API"}
          </div>
        </div>
      </div>
    </header>
  );
}
