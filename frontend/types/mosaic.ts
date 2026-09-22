export type RiskLevel =
  | "Very Low"
  | "Low"
  | "Moderate"
  | "High"
  | "Very High";

export type TargetName = "onset" | "break" | "revival" | "heavy_rain";

export interface LeadWeek {
  lead_week: 1 | 2 | 3 | 4;
}

export interface ForecastRequest {
  state: string;
  district: string;
  block: string;
  panchayat: string;
  latitude: number;
  longitude: number;
  date: string;

  rainfall_1d: number;
  rainfall_3d: number;
  rainfall_7d: number;
  rainfall_14d: number;
  rainfall_30d: number;
  rainfall_anomaly_pct: number;

  rainy_days_7d: number;
  dry_days_7d: number;

  soil_moisture: number;
  soil_moisture_7d_mean: number;

  humidity: number;
  humidity_7d_mean: number;

  temperature_c: number;
  temperature_7d_mean: number;

  wind_speed_ms: number;
  wind_7d_mean: number;

  enso: number;
  iod: number;

  mjo_phase: number;
  mjo_amplitude: number;
  rmm1: number;
  rmm2: number;

  weeks: LeadWeek[];
}

export interface ProbabilityResult {
  probability: number;
  percent: number;
  level: RiskLevel;
  event: boolean;
  threshold: number;
}

export interface WeekForecast {
  lead_week: number;
  probabilities: Record<TargetName, ProbabilityResult>;
}

export interface ForecastResponse {
  location: {
    state: string;
    district: string;
    block: string;
    panchayat: string;
  };
  forecast_date: string;
  weeks: WeekForecast[];
  model: {
    version?: string;
    trained_at_utc?: string | null;
    targets?: string[];
    data_mode?: string;
  };
  disclaimer: string;
}

export interface HealthResponse {
  status: string;
  api_version: string;
  models_loaded: boolean;
  model_directory?: string;
}

export interface ModelInfo {
  loaded: boolean;
  targets: string[];
  model_directory?: string;
  manifest?: Record<string, unknown>;
  evaluation?: Record<string, unknown>;
  limitations?: string[];
}

export interface HistoricalLocation {
  state: string;
  district: string;
  block: string;
  panchayat: string;
  latitude: number;
  longitude: number;
}

export interface LocationsResponse {
  count: number;
  locations: HistoricalLocation[];
  note: string;
}

export interface AdvisoryRequest {
  forecast: ForecastRequest;
  crop: string;
  crop_stage:
    | "pre-sowing"
    | "sowing"
    | "germination"
    | "vegetative"
    | "flowering"
    | "harvest";
  irrigation_available: boolean;
  language: string;
}

export interface WeeklyAdvisory {
  lead_week: number;
  risk_summary: string;
  actions: string[];
}

export interface AdvisoryResponse {
  crop: string;
  crop_stage: string;
  irrigation_available: boolean;
  forecast: ForecastResponse;
  overall_advisory: string;
  weekly_advisories: WeeklyAdvisory[];
  disclaimer: string;
}
