import type { SensitivityPoint } from "../types";

type SensitivityChartProps = {
  points: SensitivityPoint[];
  showPredicted: boolean;
};

type ChartPoint = {
  x: number;
  y: number;
};

function toPath(points: ChartPoint[]): string {
  return points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ");
}

export function SensitivityChart({ points, showPredicted }: SensitivityChartProps) {
  const width = 640;
  const height = 280;
  const padding = 36;

  const minX = Math.min(...points.map((point) => point.stock_price));
  const maxX = Math.max(...points.map((point) => point.stock_price));
  const allYValues = points.flatMap((point) =>
    showPredicted && point.predicted_price !== null
      ? [point.exact_price, point.predicted_price]
      : [point.exact_price]
  );
  const minY = Math.min(...allYValues);
  const maxY = Math.max(...allYValues);

  function scaleX(value: number): number {
    if (maxX === minX) {
      return width / 2;
    }
    return padding + ((value - minX) / (maxX - minX)) * (width - padding * 2);
  }

  function scaleY(value: number): number {
    if (maxY === minY) {
      return height / 2;
    }
    return height - padding - ((value - minY) / (maxY - minY)) * (height - padding * 2);
  }

  const exactPoints = points.map((point) => ({
    x: scaleX(point.stock_price),
    y: scaleY(point.exact_price)
  }));

  const predictedPoints = points
    .filter((point) => point.predicted_price !== null)
    .map((point) => ({
      x: scaleX(point.stock_price),
      y: scaleY(point.predicted_price as number)
    }));

  return (
    <div className="chart-shell">
      <svg viewBox={`0 0 ${width} ${height}`} className="chart-svg" role="img" aria-label="Price sensitivity chart">
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} className="axis-line" />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} className="axis-line" />

        <path d={toPath(exactPoints)} className="line-exact" />
        {showPredicted && predictedPoints.length > 0 ? (
          <path d={toPath(predictedPoints)} className="line-predicted" />
        ) : null}

        <text x={width / 2} y={height - 8} textAnchor="middle" className="axis-label">
          Stock Price (S)
        </text>
        <text
          x={18}
          y={height / 2}
          textAnchor="middle"
          transform={`rotate(-90 18 ${height / 2})`}
          className="axis-label"
        >
          Call Price
        </text>
      </svg>

      <div className="chart-legend">
        <div className="legend-item">
          <span className="legend-swatch legend-swatch-blue" />
          <span>Exact Black-Scholes</span>
        </div>
        {showPredicted ? (
          <div className="legend-item">
            <span className="legend-swatch legend-swatch-gold" />
            <span>Neural Approximation</span>
          </div>
        ) : null}
      </div>
    </div>
  );
}
