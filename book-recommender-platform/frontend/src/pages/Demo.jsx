import { useEffect, useState } from 'react'
import { fetchRecommendations, fetchUsers } from '../api'
import BookCard from '../components/BookCard'

export default function Demo() {
  const [users, setUsers] = useState([])
  const [selectedUser, setSelectedUser] = useState('')
  const [recs, setRecs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
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
      setRecs(data.recommendations || [])
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
      setRecs([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page">
      <h2>Демонстрация работы</h2>
      <div className="row">
        <select value={selectedUser} onChange={(e) => setSelectedUser(Number(e.target.value))}>
          {users.map((u) => <option key={u} value={u}>{u}</option>)}
        </select>
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
