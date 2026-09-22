"use client";

import {
  BarChart3,
  CloudRain,
  Gauge,
  Landmark,
  Leaf,
  Map,
  Waves,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Overview", icon: Gauge },
  { href: "/forecast", label: "Forecast", icon: CloudRain },
  { href: "/risk-map", label: "Risk map", icon: Map },
  { href: "/advisory", label: "Crop advisory", icon: Leaf },
  { href: "/analytics", label: "Model analytics", icon: BarChart3 },
  { href: "/methodology", label: "Methodology", icon: Landmark },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="desktop-sidebar fixed inset-y-0 left-0 z-40 w-[252px] border-r border-[#183f4b] bg-[#0f2d3a] text-white">
      <div className="flex h-full flex-col">
        <div className="border-b border-white/10 px-5 py-5">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-xl border border-white/15 bg-white/10">
              <Waves size={21} />
            </div>
            <div>
              <div className="text-[19px] font-extrabold tracking-[0.13em]">
                MOSAIC
              </div>
              <div className="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-300">
                Monsoon intelligence
              </div>
            </div>
          </div>
        </div>

        <div className="px-4 py-5">
          <div className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-400">
            Decision console
          </div>

          <nav className="space-y-1">
            {links.map(({ href, label, icon: Icon }) => {
              const active =
                href === "/" ? pathname === "/" : pathname.startsWith(href);

              return (
                <Link
                  key={href}
                  href={href}
                  className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition ${
                    active
                      ? "bg-white text-[#123543]"
                      : "text-slate-300 hover:bg-white/7 hover:text-white"
                  }`}
                >
                  <Icon size={17} strokeWidth={2} />
                  {label}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="mt-auto border-t border-white/10 p-4">
          <div className="rounded-xl border border-white/10 bg-white/5 p-3.5">
            <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">
              Model status
            </div>
            <div className="mt-2 flex items-center gap-2 text-sm font-semibold">
              <span className="h-2 w-2 rounded-full bg-emerald-400" />
              Historical baseline v1
            </div>
            <p className="mt-2 text-[11px] leading-5 text-slate-400">
              Research prototype. Not an official operational warning service.
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
