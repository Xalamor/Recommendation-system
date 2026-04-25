export default function Model() {
  return (
    <main className="page">
      <h2>Модель</h2>
      <p>
        Архитектура: User Embedding + Book Embedding → Concatenate → Dense → ReLU → Dropout → Dense → Output rating.
      </p>
      <ul>
        <li>Кодирование User-ID и ISBN в индексы</li>
        <li>Train/Test split</li>
        <li>Оптимизация MSELoss</li>
        <li>Метрики: RMSE, MAE, train/validation loss</li>
      </ul>
      <p>Файлы backend: preprocess.py, model.py, train_model.py, recommender.py</p>
    </main>
  )
}
