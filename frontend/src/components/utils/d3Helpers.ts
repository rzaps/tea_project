import * as d3 from "d3";
import { RingData, PieArcDatum } from "../RingData";

export const createGradients = (
  data: RingData[], prefix: string, gradientRadius: number, defs: d3.Selection<SVGDefsElement, unknown, null, undefined>
) => {
  data.forEach((d, i) => {
    const gradient = defs.append("radialGradient")
      .attr("id", `${prefix}-gradient-${i}`)
      .attr("gradientUnits", "userSpaceOnUse")
      .attr("cx", 0).attr("cy", 0).attr("r", gradientRadius);
    gradient.append("stop").attr("offset", "0%").attr("stop-color", d.colors[0]);
    gradient.append("stop").attr("offset", "100%").attr("stop-color", d.colors[1]);
  });
};

export const createRing = (
  g: d3.Selection<SVGGElement, unknown, null, undefined>,
  data: RingData[],
  innerRadius: number,
  outerRadius: number,
  prefix: string,
  onClick: (d: RingData) => void
) => {
  const pie = d3.pie<RingData>().value(d => d.value);
  const arc = d3.arc<PieArcDatum>().innerRadius(innerRadius).outerRadius(outerRadius);
  g.selectAll(`.${prefix}-arc`).data(pie(data)).enter().append("path")
    .attr("class", `${prefix}-sector`).attr("d", d => arc({ ...d, innerRadius, outerRadius })!)
    .attr("fill", (_, i) => `url(#${prefix}-gradient-${i})`).attr("stroke", "#5D4037").attr("stroke-width", 1)
    .on("click", (_, d) => onClick(d.data)).append("title").text(d => d.data.label);
};
