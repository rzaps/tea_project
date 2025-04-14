import React, { useState } from "react";
import DiagramCanvas from "./DiagramCanvas";
import TeaPointForm from "./TeaPointForm";
import InfoCard from "./InfoCard";
import {
  innerRing,
  middleRing,
  outerRing,
  defaultPoints,
  axisLabels,
  PointData,
  RingData,
} from "./RingData";


const PolarDiagram: React.FC = () => {
  const [pointsData, setPointsData] = useState<PointData[]>(defaultPoints);
  const [selectedPoint, setSelectedPoint] = useState<PointData | null>(null);
  const [selectedSector, setSelectedSector] = useState<RingData | null>(null);

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
