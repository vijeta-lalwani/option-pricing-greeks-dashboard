type MetricCardProps = {
  label: string;
  value: number;
  accent?: "blue" | "gold";
};

export function MetricCard({ label, value, accent = "blue" }: MetricCardProps) {
  return (
    <div className={`metric-card metric-card-${accent}`}>
      <p className="metric-label">{label}</p>
      <p className="metric-value">{value.toFixed(4)}</p>
    </div>
  );
}
