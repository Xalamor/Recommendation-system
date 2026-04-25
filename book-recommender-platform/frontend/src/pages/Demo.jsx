import { useEffect, useMemo, useState } from 'react'
import { fetchModelStatus, fetchRecommendations, fetchUserProfile, fetchUsers } from '../api'
import { useEffect, useState } from 'react'
import { fetchRecommendations, fetchUsers } from '../api'
import BookCard from '../components/BookCard'

export default function Demo() {
  const [users, setUsers] = useState([])
  const [selectedUser, setSelectedUser] = useState('')
  const [recs, setRecs] = useState([])
  const [profile, setProfile] = useState(null)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([fetchUsers(), fetchModelStatus()])
      .then(([usersData, statusData]) => {
        setUsers(usersData.user_ids || [])
        if (usersData.user_ids?.length) setSelectedUser(usersData.user_ids[0])
        setStatus(statusData)
      })
      .catch((e) => setError(e.message))
  }, [])

  useEffect(() => {
    if (!selectedUser) return
    fetchUserProfile(selectedUser)
      .then(setProfile)
      .catch((e) => setError(e.response?.data?.detail || e.message))
  }, [selectedUser])

    fetchUsers().then((data) => {
      setUsers(data.user_ids || [])
      if (data.user_ids?.length) setSelectedUser(data.user_ids[0])
    })
  }, [])

  const loadRecs = async () => {
    if (!selectedUser) return
    setLoading(true)
    setError('')
    try {
      const data = await fetchRecommendations(selectedUser)
      const userProfile = await fetchUserProfile(selectedUser)
      setRecs(data.recommendations || [])
      setProfile(userProfile)
      setRecs(data.recommendations || [])
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
      setRecs([])
    } finally {
      setLoading(false)
    }
  }

  const modeText = useMemo(() => {
    if (!status) return 'Проверяем режим...'
    return status.is_trained_model
      ? 'Режим: обученная нейронная сеть'
      : 'Режим: демо (без обученной модели, приближенные прогнозы)'
  }, [status])

  return (
    <main className="page">
      <h2>Демонстрация работы (понятный сценарий)</h2>

      <section className="info-box">
        <h3>Как читать эту страницу</h3>
        <ol>
          <li>Слева выбирается пользователь.</li>
          <li>Ниже показываем его историю (что он уже высоко оценивал).</li>
          <li>После этого показываем топ-10 новых рекомендаций от модели.</li>
        </ol>
        <p className="mode-badge">{modeText}</p>
        {status?.note && <p className="hint">{status.note}</p>}
      </section>

  return (
    <main className="page">
      <h2>Демонстрация работы</h2>
      <div className="row">
        <select value={selectedUser} onChange={(e) => setSelectedUser(Number(e.target.value))}>
          {users.map((u) => <option key={u} value={u}>{u}</option>)}
        </select>
        <button onClick={loadRecs}>Показать персональные рекомендации</button>
      </div>

      {profile && (
        <section className="profile-box">
          <h3>Профиль пользователя #{profile.user_id}</h3>
          <p>
            Взаимодействий: <b>{profile.num_interactions}</b> | Средняя оценка: <b>{profile.avg_rating?.toFixed?.(2) ?? 'N/A'}</b>
          </p>
          <h4>Что пользователю уже нравилось</h4>
          <ul className="history-list">
            {(profile.top_history || []).slice(0, 6).map((item) => (
              <li key={`${item.isbn}-${item.title}`}>
                <b>{item.title}</b> — {item.author} (оценка: {item.book_rating})
              </li>
            ))}
          </ul>
        </section>
      )}

      {loading && <p>Загрузка...</p>}
      {error && <p className="error">{error}</p>}

      <h3>Рекомендованные книги (Top-10)</h3>
        <button onClick={loadRecs}>Получить рекомендации</button>
      </div>
      {loading && <p>Загрузка...</p>}
      {error && <p className="error">{error}</p>}
      <div className="book-grid">
        {recs.map((book) => <BookCard key={book.isbn} book={book} />)}
      </div>
    </main>
  )
}
