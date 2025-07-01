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

console.log('[PolarDiagram] API_BASE_URL:', API_BASE_URL);
console.log('[PolarDiagram] Environment:', import.meta.env);
console.log('[PolarDiagram] Production mode:', import.meta.env.PROD);
console.log('[PolarDiagram] Development mode:', import.meta.env.DEV);

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
    console.log('[PolarDiagram] Монтирование компонента');
    console.log('[PolarDiagram] Загрузка типов чая...');
    fetch(`${API_BASE_URL}/tea_types/`)
      .then(res => {
        console.log('[PolarDiagram] tea_types status:', res.status);
        console.log('[PolarDiagram] tea_types headers:', Object.fromEntries(res.headers.entries()));
        return res.json();
      })
      .then(data => {
        console.log('[PolarDiagram] tea_types data:', data);
        setTeaTypes(data);
      })
      .catch(e => {
        console.error('[PolarDiagram] tea_types error:', e);
        setError(`Ошибка загрузки типов чая: ${e.message}`);
      });

    console.log('[PolarDiagram] Загрузка нот...');
    fetch(`${API_BASE_URL}/notes/`)
      .then(res => {
        console.log('[PolarDiagram] notes status:', res.status);
        console.log('[PolarDiagram] notes headers:', Object.fromEntries(res.headers.entries()));
        return res.json();
      })
      .then(data => {
        console.log('[PolarDiagram] notes data:', data);
        setNotes(data);
      })
      .catch(e => {
        console.error('[PolarDiagram] notes error:', e);
        setError(`Ошибка загрузки нот: ${e.message}`);
      });
  }, []);

  const fetchTeas = async () => {
    try {
      let url = `${API_BASE_URL}/teas/`;
      const params = [];
      if (typeFilter) params.push(`type=${encodeURIComponent(typeFilter)}`);
      if (noteFilter) params.push(`note=${encodeURIComponent(noteFilter)}`);
      if (params.length) url += `?${params.join("&")}`;
      
      console.log('[PolarDiagram] Fetching teas from URL:', url);
      const res = await fetch(url);
      console.log('[PolarDiagram] teas response status:', res.status);
      console.log('[PolarDiagram] teas response headers:', Object.fromEntries(res.headers.entries()));
      
      if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
      const data: any[] = await res.json();
      console.log('[PolarDiagram] teas data:', data);

      const transformed = data.map((tea): PointData => {
        const point = {
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
        };
        console.log('[PolarDiagram] Transformed point:', point);
        return point;
      });

      console.log('[PolarDiagram] All transformed points:', transformed);
      setPointsData(prev =>
        JSON.stringify(prev) === JSON.stringify(transformed) ? prev : transformed
      );
    } catch (err) {
      const errorMsg = "Ошибка загрузки данных. Обновите страницу.";
      setError(errorMsg);
      console.error("[PolarDiagram] Fetch error:", err);
      console.error("[PolarDiagram] Error details:", {
        message: err instanceof Error ? err.message : String(err),
        stack: err instanceof Error ? err.stack : undefined,
      });
    }
  };

  useEffect(() => {
    console.log('[PolarDiagram] Starting fetch interval');
    fetchTeas();
    const interval = setInterval(fetchTeas, 5000);
    return () => {
      console.log('[PolarDiagram] Cleaning up fetch interval');
      clearInterval(interval);
    };
  }, [typeFilter, noteFilter]);

  const handlePointClick = (point: PointData) => {
    console.log('[PolarDiagram] Point clicked:', point);
    setSelectedPoint(point);
  };

  const handleSectorClick = () => {
    console.log('[PolarDiagram] Sector clicked');
  };

  const handleApplyFilter = () => {
    console.log('[PolarDiagram] Applying filters:', { typeFilterDraft, noteFilterDraft });
    setTypeFilter(typeFilterDraft);
    setNoteFilter(noteFilterDraft);
  };

  useEffect(() => {
    console.log('[PolarDiagram] pointsData updated:', pointsData);
  }, [pointsData]);

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

      {pointsData.length === 0 && (
        <div style={{color: 'red', margin: 16}}>
          [PolarDiagram] Нет данных для отображения (pointsData пустой)
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