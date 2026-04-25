import { useEffect, useMemo, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { fetchDatasetInfo } from '../api'
import ChartBlock from '../components/ChartBlock'
import MetricCard from '../components/MetricCard'

export default function Dataset() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchDatasetInfo()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const ratingChart = useMemo(() => {
    if (!data?.rating_distribution) return []
    return Object.entries(data.rating_distribution).map(([rating, count]) => ({ rating, count }))
  }, [data])

  if (loading) return <main className="page">Загрузка данных...</main>
  if (error) return <main className="page">Ошибка: {error}</main>

  return (
    <main className="page">
      <h2>Описание датасета</h2>
      <div className="grid-3">
        <MetricCard title="Пользователи" value={data.num_users} />
        <MetricCard title="Книги" value={data.num_books} />
        <MetricCard title="Оценки" value={data.num_ratings} />
      </div>

      <p><b>Файлы:</b> {data.files.join(', ')}</p>
      <p><b>Explicit:</b> {(data.explicit_share * 100).toFixed(1)}% | <b>Implicit:</b> {(data.implicit_share * 100).toFixed(1)}%</p>

      <ChartBlock title="Распределение оценок Book-Rating">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={ratingChart}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="rating" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </ChartBlock>

      <h3>Примеры строк</h3>
      <pre>{JSON.stringify({ users: data.users_sample, books: data.books_sample, ratings: data.ratings_sample }, null, 2)}</pre>
    </main>
  )
}
