import type { RiskLevel, TargetName } from "@/types/mosaic";

export function riskTone(level?: RiskLevel) {
  switch (level) {
    case "Very High":
      return "border-red-200 bg-red-50 text-red-800";
    case "High":
      return "border-orange-200 bg-orange-50 text-orange-800";
    case "Moderate":
      return "border-amber-200 bg-amber-50 text-amber-800";
    case "Low":
      return "border-sky-200 bg-sky-50 text-sky-800";
    default:
      return "border-emerald-200 bg-emerald-50 text-emerald-800";
  }
}

export function mapColor(percent: number) {
  if (percent >= 80) return "#b42318";
  if (percent >= 60) return "#d97706";
  if (percent >= 40) return "#ca8a04";
  if (percent >= 20) return "#0284c7";
  return "#0f766e";
}

export const targetCopy: Record<
  TargetName,
  { title: string; subtitle: string }
> = {
  onset: {
    title: "Monsoon onset",
    subtitle: "Probability of sustained wet-season establishment",
  },
  break: {
    title: "Break risk",
    subtitle: "Probability of an upcoming prolonged dry spell",
  },
  revival: {
    title: "Revival",
    subtitle: "Probability of rainfall returning after suppressed conditions",
  },
  heavy_rain: {
    title: "Heavy rain",
    subtitle: "Probability of a heavy-rain event in the target period",
  },
};
