import React, { useState, useEffect } from "react";
import DiagramCanvas from "./DiagramCanvas";
import {
  innerRing,
  middleRing,
  outerRing,
  axisLabels,
  PointData
} from "./RingData";

interface TeaType {
  id: string;
  name: string;
}

const API_BASE_URL = import.meta.env.PROD
  ? 'https://tea-project-0buv.onrender.com/teas/api'
  : 'http://127.0.0.1:8000/teas/api';

console.log('API_BASE_URL:', API_BASE_URL);
console.log('Environment:', import.meta.env);

const PolarDiagram: React.FC = () => {
  const [pointsData, setPointsData] = useState<PointData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedPoint, setSelectedPoint] = useState<PointData | null>(null);
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [typeFilterDraft, setTypeFilterDraft] = useState<string>("");
  const [teaTypes, setTeaTypes] = useState<TeaType[]>([]);
  const [noteFilter, setNoteFilter] = useState<string>("");
  const [noteFilterDraft, setNoteFilterDraft] = useState<string>("");
  const [notes, setNotes] = useState<{id: string, name: string}[]>([]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/tea_types/`)
      .then(res => res.json())
      .then(data => setTeaTypes(data));
    fetch(`${API_BASE_URL}/notes/`)
      .then(res => res.json())
      .then(data => setNotes(data));
  }, []);

  const fetchTeas = async () => {
    try {
      let url = `${API_BASE_URL}/teas/`;
      const params = [];
      if (typeFilter) params.push(`type=${encodeURIComponent(typeFilter)}`);
      if (noteFilter) params.push(`note=${encodeURIComponent(noteFilter)}`);
      if (params.length) url += `?${params.join("&")}`;
      
      console.log('Fetching from URL:', url);
      const res = await fetch(url);
      console.log('Response status:', res.status);
      
      if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
      const data: any[] = await res.json();
      console.log('Received data:', data);

      const transformed = data.map((tea): PointData => ({
        angle: ((Math.atan2(tea.y_coord, tea.x_coord) * 180) / Math.PI + 450) % 360,
        radius: Math.sqrt(tea.x_coord ** 2 + tea.y_coord ** 2),
        label: tea.translated_name || tea.name || "Чай",
        color: tea.color || "#8D6E63",
        id: tea.id,
        type: tea.type?.translated_name || tea.type?.name || "—",
        region: tea.region?.translated_name || tea.region?.name || "—",
        notes: Array.isArray(tea.notes) ? tea.notes.map((n: any) => n.name || n.translated_name).filter(Boolean) : [],
        x_coord: tea.x_coord,
        y_coord: tea.y_coord,
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
  }, [typeFilter, noteFilter]);

  const handlePointClick = (point: PointData) => {
    setSelectedPoint(point);
  };

  // Заглушка для onSectorClick, если обработчик не нужен
  const handleSectorClick = () => {};

  const handleApplyFilter = () => {
    setTypeFilter(typeFilterDraft);
    setNoteFilter(noteFilterDraft);
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

      {selectedPoint && (
        <>
          <style>{`
            .tea-modal-backdrop {
              position: fixed; left: 0; top: 0; width: 100vw; height: 100vh;
              background: rgba(0,0,0,0.3); z-index: 1000; display: flex; align-items: center; justify-content: center;
            }
            .tea-modal-card {
              background: #fff; border-radius: 12px; padding: 2em; min-width: 280px; max-width: 90vw; box-shadow: 0 4px 24px #0002;
            }
            @media (max-width: 600px) {
              .tea-modal-card { min-width: 90vw; padding: 1em; }
            }
          `}</style>
          <div className="tea-modal-backdrop" onClick={() => setSelectedPoint(null)}>
            <div className="tea-modal-card" onClick={e => e.stopPropagation()}>
              <h4>{selectedPoint.label}</h4>
              <div><b>Тип:</b> {selectedPoint.type || "—"}</div>
              <div><b>Регион:</b> {selectedPoint.region || "—"}</div>
              <div><b>Ноты:</b> {selectedPoint.notes && selectedPoint.notes.length > 0 ? selectedPoint.notes.join(", ") : "—"}</div>
              <button
                className="btn btn-primary mt-2"
                onClick={() => window.location.href = `/teas/${selectedPoint.id}/`}
              >
                Подробнее
              </button>
              <button
                className="btn btn-secondary mt-2 ms-2"
                onClick={() => setSelectedPoint(null)}
              >
                Закрыть
              </button>
            </div>
          </div>
        </>
      )}

      <div style={{ marginBottom: 16 }}>
        <label>
          Тип чая:&nbsp;
          <select value={typeFilterDraft} onChange={e => setTypeFilterDraft(e.target.value)}>
            <option value="">Все</option>
            {teaTypes.map(t => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
        </label>
        <label style={{ marginLeft: 16 }}>
          Нота:&nbsp;
          <select value={noteFilterDraft} onChange={e => setNoteFilterDraft(e.target.value)}>
            <option value="">Все</option>
            {notes.map(n => (
              <option key={n.id} value={n.id}>{n.name}</option>
            ))}
          </select>
        </label>
        <button
          style={{ marginLeft: 8 }}
          onClick={handleApplyFilter}
          type="button"
          className="btn btn-success btn-sm"
        >
          Применить
        </button>
      </div>

      <div className="row flex-column flex-md-row g-4">
        <div className="col-12">
          <div className="polar-card">
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
      </div>
    </div>
  );
};

export default PolarDiagram;