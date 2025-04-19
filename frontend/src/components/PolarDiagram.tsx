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

const PolarDiagram: React.FC = () => {
  const [pointsData, setPointsData] = useState<PointData[]>([]);
  const [selectedPoint, setSelectedPoint] = useState<PointData | null>(null);
  const [selectedSector, setSelectedSector] = useState<RingData | null>(null);

  // Получение данных с сервера Django
 useEffect(() => {
  fetch("http://localhost:8000/teas/api/teas/")
    .then((res) => {
      if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
      return res.json();
    })
    .then((data) => {
      // Преобразование координат x/y в полярные (угол, радиус)
      const maxDistance = Math.max(
        ...data.map((tea: any) => Math.sqrt(tea.x_coord ** 2 + tea.y_coord ** 2)),
        1 // Защита от деления на ноль
      );

      const transformed: PointData[] = data.map((tea: any) => {
        const angleRad = Math.atan2(tea.y_coord, tea.x_coord);
        const angle = ((angleRad * (180 / Math.PI)) + 360) % 360; // [0, 360)
        const distance = Math.sqrt(tea.x_coord ** 2 + tea.y_coord ** 2);
        const radius = (distance / maxDistance) * 0.4 + 0.4; // Нормализация в [0.4, 0.8]

        return {
          angle: angle,
          radius: radius,
          label: tea.name || "Чай",
          color: tea.color || "#8D6E63", // Используем цвет из данных
          info: `${tea.type || ""} - ${tea.taste || ""} из ${tea.region || "неизвестно"}`,
        };
      });

      console.log("Преобразованные точки:", transformed);
      setPointsData(transformed);
    })
    .catch((error) => {
      console.error("Ошибка при загрузке чаёв:", error);
    });
}, []);

  const handlePointClick = (point: PointData) => {
    setSelectedPoint(point);
    setSelectedSector(null);
  };

  const handleSectorClick = (sector: RingData) => {
    setSelectedSector(sector);
    setSelectedPoint(null);
  };

  const handleAddPoint = (point: PointData) => {
    setPointsData([...pointsData, point]);
  };

  return (
    <div className="polar-container">
      <h2 className="polar-title d-md-none mb-4">Чайная карта</h2>
      <div className="row flex-column flex-md-row g-4">
        <div className="col-12 col-md-7 order-2 order-md-1">
          <div className="polar-card">
            <h2 className="polar-title d-none d-md-block mb-4">Чайная карта</h2>
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
