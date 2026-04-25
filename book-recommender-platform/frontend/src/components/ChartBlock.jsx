export default function ChartBlock({ title, children }) {
  return (
    <section className="chart-block">
      <h3>{title}</h3>
      <div className="chart-inner">{children}</div>
    </section>
  )
}
