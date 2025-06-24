import React, { useState } from "react";
import { PointData } from "./RingData";

const TeaPointForm: React.FC<{ onAddPoint: (point: PointData) => void }> = ({ onAddPoint }) => {
  const [newTea, setNewTea] = useState<PointData>({ angle: 0, radius: 0.5, label: '', color: '#000000', info: '' });
  const [xCoord, setXCoord] = useState<number>(0);
  const [yCoord, setYCoord] = useState<number>(0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onAddPoint({ ...newTea, x_coord: xCoord, y_coord: yCoord });
    setNewTea({ angle: 0, radius: 0.5, label: '', color: '#000000', info: '' });
    setXCoord(0);
    setYCoord(0);
  };

  return (
    <div className="form-card">
      <div className="form-header">Добавить чай</div>
      <div className="form-body">
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="x_coord" className="form-label">X координата</label>
            <input type="number" className="form-control" id="x_coord" value={xCoord} onChange={(e) => setXCoord(Number(e.target.value))} required />
          </div>
          <div className="mb-3">
            <label htmlFor="y_coord" className="form-label">Y координата</label>
            <input type="number" className="form-control" id="y_coord" value={yCoord} onChange={(e) => setYCoord(Number(e.target.value))} required />
          </div>
          <button type="submit" className="btn btn-primary">Добавить</button>
        </form>
      </div>
    </div>
  );
};

export default TeaPointForm;
