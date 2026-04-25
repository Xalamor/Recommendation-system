export default function BookCard({ book }) {
  return (
    <article className="book-card">
      <img src={book.image_url || 'https://via.placeholder.com/120x180?text=Book'} alt={book.title} />
      <div>
        <h4>{book.title}</h4>
        <p><b>Автор:</b> {book.author}</p>
        <p><b>Год:</b> {book.year}</p>
        <p><b>Издатель:</b> {book.publisher}</p>
        {book.predicted_rating !== undefined && <p><b>Прогноз:</b> {book.predicted_rating.toFixed(2)}</p>}
      </div>
    </article>
  )
}
