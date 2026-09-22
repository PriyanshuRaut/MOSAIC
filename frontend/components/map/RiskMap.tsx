"use client";

import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";

import { mapColor } from "@/lib/risk";
import type {
  ForecastResponse,
  HistoricalLocation,
  TargetName,
} from "@/types/mosaic";

export function RiskMap({
  locations,
  forecast,
  latitude,
  longitude,
  target,
}: {
  locations: HistoricalLocation[];
  forecast: ForecastResponse | null;
  latitude: number;
  longitude: number;
  target: TargetName;
}) {
  const week1 = forecast?.weeks[0];
  const selected = week1?.probabilities[target];
  const selectedColor = mapColor(selected?.percent ?? 0);

  return (
    <MapContainer
      center={[latitude || 22.8, longitude || 79.5]}
      zoom={5}
      scrollWheelZoom
      style={{ height: "100%", minHeight: 520 }}
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {locations.map((location, index) => (
        <CircleMarker
          key={`${location.state}-${location.district}-${index}`}
          center={[location.latitude, location.longitude]}
          radius={5}
          pathOptions={{
            color: "#607987",
            fillColor: "#8da0aa",
            fillOpacity: 0.6,
            weight: 1,
          }}
        >
          <Popup>
            <strong>{location.district}</strong>
            <br />
            {location.state}
            <br />
            Historical baseline location
          </Popup>
        </CircleMarker>
      ))}

      <CircleMarker
        center={[latitude, longitude]}
        radius={11}
        pathOptions={{
          color: selectedColor,
          fillColor: selectedColor,
          fillOpacity: 0.78,
          weight: 3,
        }}
      >
        <Popup>
          <strong>Selected forecast point</strong>
          <br />
          Week 1 {target.replace("_", " ")}:{" "}
          {selected ? `${selected.percent.toFixed(1)}%` : "Run forecast"}
        </Popup>
      </CircleMarker>
    </MapContainer>
  );
}
