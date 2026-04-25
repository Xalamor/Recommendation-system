export default function MetricCard({ title, value, subtitle }) {
  return (
    <div className="metric-card">
      <p>{title}</p>
      <h3>{value}</h3>
      {subtitle && <small>{subtitle}</small>}
    </div>
  )
}
