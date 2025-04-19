export interface RingData {
  label: string;
  value: number;
  colors: [string, string];
}

export interface PointData {
  angle: number;
  radius: number;
  label: string;
  color: string;
  info: string;
}

export interface AxisLabel {
  angle: number;
  text: string;
  color: string;
}

export interface PieArcDatum extends d3.PieArcDatum<RingData> {
  innerRadius: number;
  outerRadius: number;
}

export const innerRing: RingData[] = [
  { label: "Белый", value: 1, colors: ["#f9f9f9", "#e0e0e0"] },
  { label: "Зеленый", value: 1, colors: ["#c8e6c9", "#81c784"] },
  { label: "Улун", value: 1, colors: ["#d7ccc8", "#a1887f"] },
  { label: "Черный", value: 1, colors: ["#cfd8dc", "#90a4ae"] }
];

export const middleRing: RingData[] = [
  { label: "Орехи", value: 1, colors: ["#ffffff", "#f3d36a"] },
  { label: "Фруктовый", value: 1, colors: ["#ffffff", "#f4ca43"] },
  { label: "Травяной", value: 1, colors: ["#fdfdfd", "#f8b84b"] },
  { label: "Дымный", value: 1, colors: ["#ffffff", "rgba(98,129,244,0.7)"] },
  { label: "Древесный", value: 1, colors: ["#ffffff", "#918076"] },
  { label: "Землистый", value: 1, colors: ["#ffffff", "#625038"] },
  { label: "Цветочный", value: 1, colors: ["#ffffff", "#AB8B5A"] },
  { label: "Фруктовый", value: 1, colors: ["#ffffff", "#B28765"] },
  { label: "Травяной", value: 1, colors: ["#ffffff", "#E1AC66"] },
  { label: "Дымный", value: 1, colors: ["#ffffff", "#B28683"] },
  { label: "Древесный", value: 1, colors: ["#ffffff", "#BB8772"] },
  { label: "Землистый", value: 1, colors: ["#ffffff", "#8A7071"] }
];

export const outerRing: RingData[] = [
  { label: "-", value: 1, colors: ["#ffffff", "#f3d36a"] },
  { label: "-", value: 1, colors: ["#ffffff", "#e6bb36"] },
  { label: "-", value: 1, colors: ["#ffffff", "#f49f46"] },
  { label: "-", value: 1, colors: ["#ffffff", "#BBDEFB"] },
  { label: "-", value: 1, colors: ["#ffffff", "#B2EBF2"] },
  { label: "-", value: 1, colors: ["#ffffff", "#C8E6C9"] },
  { label: "-", value: 1, colors: ["#ffffff", "#FFECB3"] },
  { label: "-", value: 1, colors: ["#ffffff", "#FFE0B2"] },
  { label: "-", value: 1, colors: ["#ffffff", "#FFCCBC"] },
  { label: "-", value: 1, colors: ["#ffffff", "#D7CCC8"] },
  { label: "-", value: 1, colors: ["#ffffff", "#F5F5F5"] },
  { label: "-", value: 1, colors: ["#ffffff", "#CFD8DC"] }
];

// export const defaultPoints: PointData[] = [
//   { angle: 45, radius: 0.6, label: "Бай Хао", color: "#D4AF37", info: "Элитный белый чай с цветочным ароматом" },
//   { angle: 120, radius: 0.4, label: "Лун Цзин", color: "#2E7D32", info: "Знаменитый зеленый чай из Ханчжоу" },
//   { angle: 210, radius: 0.7, label: "Да Хун Пао", color: "#4E342E", info: "Легендарный улун с Уишаньских гор" },
//   { angle: 300, radius: 0.5, label: "Шу Пуэр", color: "#5D4037", info: "Выдержанный пуэр с землистым вкусом" }
// ];

export const axisLabels: AxisLabel[] = [
  { angle: 0, text: "Север", color: "#5D4037" },
  { angle: 90, text: "Восток", color: "#5D4037" },
  { angle: 180, text: "Юг", color: "#5D4037" },
  { angle: 270, text: "Запад", color: "#5D4037" }
];
