import React from "react";
import { PointData, RingData } from "./RingData";

const InfoCard: React.FC<{ point: PointData | null; sector: RingData | null }> = ({ point, sector }) => (
  <div className="info-card mb-4">
    <div className="info-header">Информация</div>
    <div className="info-body">
      {point ? (
        <>
          <h5 className="info-title">{point.label}</h5>
          <p className="info-text">{point.info}</p>
        </>
      ) : sector ? (
        <>
          <h5 className="info-title">{sector.label}</h5>
          <p className="info-text">Выбран сектор: {sector.label}</p>
        </>
      ) : (
        <p className="info-placeholder">Кликните на точку или сектор для получения информации</p>
      )}
    </div>
  </div>
);

export default InfoCard;
