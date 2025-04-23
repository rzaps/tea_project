import React, { useRef, useEffect } from "react";
import * as d3 from "d3";
import { createGradients, createRing } from "./utils/d3Helpers";
import { RingData, PointData, AxisLabel } from "./RingData";

const DiagramCanvas: React.FC<{
  rings: { inner: RingData[]; middle: RingData[]; outer: RingData[] };
  points: PointData[];
  labels: AxisLabel[];
  onPointClick: (point: PointData) => void;
  onSectorClick: (sector: RingData) => void;
}> = ({ rings, points, labels, onPointClick, onSectorClick }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;
    const width = 700, height = 700;
    const radius = Math.min(width, height) / 2;
    const center = { x: width / 2, y: height / 2 };

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    const g = svg.attr("width", width).attr("height", height).append("g")
      .attr("transform", `translate(${center.x},${center.y})`);

    const defs = g.append("defs");
    createGradients(rings.inner, "inner", radius * 0.5, defs);
    createGradients(rings.middle, "middle", radius * 0.75, defs);
    createGradients(rings.outer, "outer", radius, defs);

    createRing(g, rings.inner, 0, radius * 0.5, "inner", onSectorClick);
    createRing(g, rings.middle, radius * 0.5, radius * 0.75, "middle", onSectorClick);
    createRing(g, rings.outer, radius * 0.75, radius, "outer", onSectorClick);

    console.log("Рисуем точки:", points); // ← для отладки

    points.forEach(point => {
      const angleRad = (point.angle - 90) * (Math.PI / 180);
      const x = point.radius * radius * Math.cos(angleRad);
      const y = point.radius * radius * Math.sin(angleRad);

      g.append("circle")
        .attr("cx", x).attr("cy", y).attr("r", 10)
        .attr("fill", point.color).attr("stroke", "#5D4037").attr("stroke-width", 2)
        .on("click", () => onPointClick(point)).append("title").text(point.label);

      g.append("text")
        .attr("x", x).attr("y", y - 15).attr("text-anchor", "middle")
        .attr("font-family", "Georgia, serif").attr("font-size", "12px")
        .attr("fill", "#5D4037").text(point.label);
    });

    labels.forEach(label => {
      const angleRad = (label.angle - 90) * (Math.PI / 180);
      const r = radius * 0.3;
      const x = r * Math.cos(angleRad);
      const y = r * Math.sin(angleRad);
      const rotation = label.angle === 0 ? -90 : label.angle === 180 ? 90 : 0;
      const dy = label.angle === 90 ? "16" : label.angle === 270 ? "-10" : "12";
      const text = g.append("text").attr("x", x).attr("y", y).attr("dy", dy)
        .attr("text-anchor", "middle").attr("font-size", "18px")
        .attr("font-weight", "bold").attr("fill", label.color).text(label.text);
      if (rotation) text.attr("transform", `rotate(${rotation}, ${x}, ${y})`);
    });
  }, [points]);

  return <svg ref={svgRef} className="polar-svg" />;
};

export default DiagramCanvas;
