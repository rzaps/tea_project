import React, { useState, useEffect } from "react";
import DiagramCanvas from "./DiagramCanvas";
import TeaPointForm from "./TeaPointForm";
import InfoCard from "./InfoCard";
import {
  innerRing,
  middleRing,
  outerRing,
  axisLabels,
  PointData,
  RingData,
} from "./RingData";

interface TeaData {
  x_coord: number;
  y_coord: number;
  name?: string;
  color?: string;
  type?: string;
  taste?: string;
  region?: string;
}

const PolarDiagram: React.FC = () => {
  const [pointsData, setPointsData] = useState<PointData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedPoint, setSelectedPoint] = useState<PointData | null>(null);
  const [selectedSector, setSelectedSector] = useState<RingData | null>(null);

  const fetchTeas = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/teas/api/teas/");
      if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
      const data: TeaData[] = await res.json();

      const maxDistance = Math.max(
        ...data.map((tea) => Math.sqrt(tea.x_coord ** 2 + tea.y_coord ** 2)),
        1
      );

      const transformed = data.map((tea): PointData => ({
        angle: ((Math.atan2(tea.y_coord, tea.x_coord) * 180) / Math.PI + 360) % 360,
        radius: (Math.sqrt(tea.x_coord ** 2 + tea.y_coord ** 2) / maxDistance) * 0.4 + 0.4,
        label: tea.name || "Чай",
        color: tea.color || "#8D6E63",
        info: `${tea.type || ""} - ${tea.taste || ""} из ${tea.region || "неизвестно"}`,
      }));

      setPointsData(prev =>
        JSON.stringify(prev) === JSON.stringify(transformed) ? prev : transformed
      );
    } catch (err) {
      setError("Ошибка загрузки данных. Обновите страницу.");
      console.error("Fetch error:", err);
    }
  };

  useEffect(() => {
    fetchTeas();
    const interval = setInterval(fetchTeas, 5000);
    return () => clearInterval(interval);
  }, []);

  const handlePointClick = (point: PointData) => {
    setSelectedPoint(point);
    setSelectedSector(null);
  };

  const handleSectorClick = (sector: RingData) => {
    setSelectedSector(sector);
    setSelectedPoint(null);
  };

  const handleAddPoint = async (point: PointData) => {
    try {
      const csrfToken = (document.querySelector("[name=csrfmiddlewaretoken]") as HTMLInputElement)?.value;

      const res = await fetch("http://127.0.0.1:8000/teas/api/teas/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          x_coord: Math.cos((point.angle - 90) * (Math.PI / 180)) * point.radius,
          y_coord: Math.sin((point.angle - 90) * (Math.PI / 180)) * point.radius,
          ...point
        }),
      });

      if (!res.ok) throw new Error("Ошибка сохранения");
      setPointsData(prev => [...prev, point]);
    } catch (err) {
      setError("Ошибка при сохранении точки");
      console.error("Save error:", err);
    }
  };

  return (
    <div className="polar-container">
      <h2 className="polar-title d-md-none mb-4">Чайная карта</h2>

      {error && (
        <div className="alert alert-danger mx-3">
          {error}
          <button
            className="btn btn-sm btn-light ms-3"
            onClick={() => setError(null)}
          >
            ×
          </button>
        </div>
      )}

      <div className="row flex-column flex-md-row g-4">
        <div className="col-12 col-md-7 order-2 order-md-1">
          <div className="polar-card">
            {/*<h2 className="polar-title d-none d-md-block mb-4">Чайная карта</h2>*/}
            <div className="polar-svg-container">
              <DiagramCanvas
                rings={{ inner: innerRing, middle: middleRing, outer: outerRing }}
                points={pointsData}
                labels={axisLabels}
                onPointClick={handlePointClick}
                onSectorClick={handleSectorClick}
              />
            </div>
          </div>
        </div>

        <div className="col-12 col-md-5 order-1 order-md-2">
          <div className="sticky-md-top" style={{ top: "20px" }}>
            <InfoCard point={selectedPoint} sector={selectedSector} />
            <TeaPointForm onAddPoint={handleAddPoint} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default PolarDiagram;