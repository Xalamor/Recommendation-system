import { useEffect, useMemo, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts'
import { fetchMetrics } from '../api'
import MetricCard from '../components/MetricCard'
import ChartBlock from '../components/ChartBlock'

export default function Results() {
  const [m, setM] = useState(null)

  useEffect(() => {
    fetchMetrics().then(setM).catch(() => setM({}))
  }, [])

  const lossData = useMemo(() => {
    if (!m?.train_loss?.length) return []
    return m.train_loss.map((v, i) => ({ epoch: i + 1, train: v, val: m.val_loss?.[i] }))
  }, [m])

  return (
    <main className="page">
      <h2>Результаты</h2>
      <div className="grid-2">
        <MetricCard title="RMSE" value={m?.rmse ?? 'N/A'} subtitle={`Baseline: ${m?.baseline_rmse ?? 'N/A'}`} />
        <MetricCard title="MAE" value={m?.mae ?? 'N/A'} subtitle={`Baseline: ${m?.baseline_mae ?? 'N/A'}`} />
      </div>
      <ChartBlock title="Train/Validation Loss">
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={lossData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="epoch" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="train" stroke="#3b82f6" />
            <Line type="monotone" dataKey="val" stroke="#22c55e" />
          </LineChart>
        </ResponsiveContainer>
      </ChartBlock>
      <p>Чем ниже RMSE и MAE, тем точнее модель предсказывает пользовательские предпочтения.</p>
    </main>
  )
}
