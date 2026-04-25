# Book Recommender Platform (Course Project, Deep Learning)

Веб-платформа для демонстрации рекомендательной системы книг на основе нейронной сети (embeddings + MLP) по мотивам Book Recommendation Dataset (Book-Crossing).

## Бизнес-идея
Платформа помогает онлайн-библиотекам и книжным магазинам персонализировать рекомендации книг, увеличивать вовлеченность пользователей и повышать продажи.

## Датасет
Источник: Kaggle — Book Recommendation Dataset  
https://www.kaggle.com/datasets/arashnic/book-recommendation-dataset

### Состав
- `Users.csv`: `User-ID`, `Location`, `Age`
- `Books.csv`: `ISBN`, `Book-Title`, `Book-Author`, `Year-Of-Publication`, `Publisher`, `Image-URL-*`
- `Ratings.csv`: `User-ID`, `ISBN`, `Book-Rating`
  - explicit: 1..10
  - implicit: 0

> Если у вас есть только `Books.csv`, backend поддерживает fallback-режим: генерирует mock-пользователей и ratings, чтобы демо работало.

## Структура проекта

```text
book-recommender-platform/
  backend/
    main.py
    preprocess.py
    train_model.py
    model.py
    recommender.py
    requirements.txt
    data/
    artifacts/
  frontend/
    package.json
    src/
      App.jsx
      main.jsx
      api.js
      pages/
        Home.jsx
        Dataset.jsx
        Model.jsx
        Demo.jsx
        Results.jsx
        Business.jsx
      components/
        Navbar.jsx
        BookCard.jsx
        MetricCard.jsx
        ChartBlock.jsx
  README.md
```

## Подготовка данных

1. Скачайте датасет с Kaggle.
2. Положите CSV в `backend/data/`:
   - `Users.csv`
   - `Books.csv`
   - `Ratings.csv`

## Обучение модели

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python train_model.py
```

После обучения сохраняются:
- `artifacts/model.pt`
- `artifacts/user_encoder.pkl`
- `artifacts/book_encoder.pkl`
- `artifacts/books_metadata.pkl`
- `artifacts/metrics.json`

## Запуск backend (FastAPI)

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### API endpoints
- `GET /dataset-info`
- `GET /metrics`
- `GET /model-status`
- `GET /popular-books`
- `GET /users`
- `GET /user-profile/{user_id}`
- `GET /popular-books`
- `GET /users`
- `GET /recommendations/{user_id}`
- `POST /predict`

## Запуск frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Опционально укажите API url:

```bash
VITE_API_BASE=http://127.0.0.1:8000 npm run dev
```

## Метрики
- **RMSE** (root mean squared error)
- **MAE** (mean absolute error)
- **train loss** и **validation loss** по эпохам
- baseline: средняя оценка train

Интерпретация: чем ниже RMSE/MAE, тем точнее прогноз пользовательских предпочтений.

## Как работает рекомендательная система
1. `preprocess.py` очищает данные, фильтрует редких пользователей/книги, кодирует `User-ID` и `ISBN`.
2. `train_model.py` обучает embedding-модель (`model.py`).
3. `recommender.py` загружает модель и артефакты, вычисляет top-N рекомендации.
4. FastAPI в `main.py` отдает рекомендации frontend-части.

