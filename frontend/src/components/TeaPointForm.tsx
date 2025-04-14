import React, { useState } from "react";
import { PointData } from "./RingData";

const TeaPointForm: React.FC<{ onAddPoint: (point: PointData) => void }> = ({ onAddPoint }) => {
  const [newTea, setNewTea] = useState<PointData>({ angle: 0, radius: 0.5, label: '', color: '#000000', info: '' });
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onAddPoint(newTea);
    setNewTea({ angle: 0, radius: 0.5, label: '', color: '#000000', info: '' });
  };
  return (
    <div className="form-card">
      <div className="form-header">Добавить чай</div>
      <div className="form-body">
        <form onSubmit={handleSubmit}>
          {/* Форма как в оригинале */}
        </form>
      </div>
    </div>
  );
};

export default TeaPointForm;
