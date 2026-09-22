"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { ForecastResponse } from "@/types/mosaic";

export function FourWeekChart({
  forecast,
}: {
  forecast: ForecastResponse | null;
}) {
  const data =
    forecast?.weeks.map((week) => ({
      week: `W${week.lead_week}`,
      onset: week.probabilities.onset.percent,
      break: week.probabilities.break.percent,
      revival: week.probabilities.revival.percent,
      heavyRain: week.probabilities.heavy_rain.percent,
    })) ?? [];

  if (!forecast) {
    return (
      <div className="grid h-[320px] place-items-center px-6 text-center">
        <div>
          <div className="text-sm font-bold text-slate-600">
            No forecast generated yet
          </div>
          <p className="mt-1 max-w-md text-xs leading-5 text-slate-500">
            Run the trained historical models to populate the four-week
            probability outlook.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[320px] w-full px-2 pb-3 pt-5">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 4, right: 16, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="week"
            tick={{ fontSize: 11, fill: "#667984" }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            domain={[0, 100]}
            tickFormatter={(value) => `${value}%`}
            tick={{ fontSize: 11, fill: "#667984" }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            formatter={(value) => [`${Number(value).toFixed(1)}%`]}
            contentStyle={{
              borderRadius: 10,
              border: "1px solid #dce5ea",
              fontSize: 12,
            }}
          />
          <Legend wrapperStyle={{ fontSize: 11, paddingTop: 12 }} />
          <Line
            type="monotone"
            dataKey="onset"
            name="Onset"
            stroke="#0f766e"
            strokeWidth={2.2}
            dot={{ r: 3 }}
          />
          <Line
            type="monotone"
            dataKey="break"
            name="Break"
            stroke="#b45309"
            strokeWidth={2.2}
            dot={{ r: 3 }}
          />
          <Line
            type="monotone"
            dataKey="revival"
            name="Revival"
            stroke="#2563eb"
            strokeWidth={2.2}
            dot={{ r: 3 }}
          />
          <Line
            type="monotone"
            dataKey="heavyRain"
            name="Heavy rain"
            stroke="#b42318"
            strokeWidth={2.2}
            dot={{ r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
