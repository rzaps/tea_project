import React, { useState, useEffect } from "react";
import DiagramCanvas from "./DiagramCanvas";
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

interface TeaType {
  id: string;
  name: string;
}

const PolarDiagram: React.FC = () => {
  const [pointsData, setPointsData] = useState<PointData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedPoint, setSelectedPoint] = useState<PointData | null>(null);
  const [selectedSector, setSelectedSector] = useState<RingData | null>(null);
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [typeFilterDraft, setTypeFilterDraft] = useState<string>("");
  const [teaTypes, setTeaTypes] = useState<TeaType[]>([]);
  const [noteFilter, setNoteFilter] = useState<string>("");
  const [noteFilterDraft, setNoteFilterDraft] = useState<string>("");
  const [notes, setNotes] = useState<{id: string, name: string}[]>([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/teas/api/tea_types/")
      .then(res => res.json())
      .then(data => setTeaTypes(data));
    fetch("http://127.0.0.1:8000/teas/api/notes/")
      .then(res => res.json())
      .then(data => setNotes(data));
  }, []);

  const fetchTeas = async () => {
    try {
      let url = "http://127.0.0.1:8000/teas/api/teas/";
      const params = [];
      if (typeFilter) params.push(`type=${encodeURIComponent(typeFilter)}`);
      if (noteFilter) params.push(`note=${encodeURIComponent(noteFilter)}`);
      if (params.length) url += `?${params.join("&")}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
      const data: any[] = await res.json();

      const maxDistance = Math.max(
        ...data.map((tea) => Math.sqrt(tea.x_coord ** 2 + tea.y_coord ** 2)),
        1
      );

      const transformed = data.map((tea): PointData => ({
        angle: ((Math.atan2(tea.y_coord, tea.x_coord) * 180) / Math.PI + 450) % 360,
        radius: Math.sqrt(tea.x_coord ** 2 + tea.y_coord ** 2),
        label: tea.translated_name || tea.name || "Чай",
        color: tea.color || "#8D6E63",
        id: tea.id,
        type: tea.type?.translated_name || tea.type?.name || "—",
        region: tea.region?.translated_name || tea.region?.name || "—",
        notes: Array.isArray(tea.notes) ? tea.notes.map((n: any) => n.name || n.translated_name).filter(Boolean) : [],
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