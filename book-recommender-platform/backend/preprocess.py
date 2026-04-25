from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"


USERS_COLS = ["User-ID", "Location", "Age"]
BOOKS_COLS = [
    "ISBN",
    "Book-Title",
    "Book-Author",
    "Year-Of-Publication",
    "Publisher",
    "Image-URL-S",
    "Image-URL-M",
    "Image-URL-L",
]
RATINGS_COLS = ["User-ID", "ISBN", "Book-Rating"]


def _read_csv_safe(path: Path, cols: list[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=cols)
    # Book-Crossing often uses latin-1 and ; separator
    for sep in [";", ","]:
        try:
            df = pd.read_csv(path, sep=sep, encoding="latin-1", on_bad_lines="skip")
            if len(df.columns) >= 2:
                return df
        except Exception:
            continue
    return pd.read_csv(path, encoding="latin-1", on_bad_lines="skip")


def load_raw_data(data_dir: Path | None = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    data_dir = data_dir or DATA_DIR
    users = _read_csv_safe(data_dir / "Users.csv", USERS_COLS)
    books = _read_csv_safe(data_dir / "Books.csv", BOOKS_COLS)
    ratings = _read_csv_safe(data_dir / "Ratings.csv", RATINGS_COLS)

    users = users[[c for c in USERS_COLS if c in users.columns]].copy()
    books = books[[c for c in BOOKS_COLS if c in books.columns]].copy()
    ratings = ratings[[c for c in RATINGS_COLS if c in ratings.columns]].copy()
    return users, books, ratings


def build_mock_ratings_from_books(books: pd.DataFrame, n_users: int = 120, interactions_per_user: int = 18) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Fallback data generator so demo works even with only Books.csv."""
    if books.empty:
        books = pd.DataFrame(
            {
                "ISBN": [f"MOCK-{i:05d}" for i in range(1, 501)],
                "Book-Title": [f"Demo Book {i}" for i in range(1, 501)],
                "Book-Author": [f"Author {i % 40}" for i in range(1, 501)],
                "Year-Of-Publication": [1990 + (i % 30) for i in range(1, 501)],
                "Publisher": [f"Publisher {i % 20}" for i in range(1, 501)],
                "Image-URL-M": ["https://via.placeholder.com/120x180?text=Book" for _ in range(500)],
            }
        )

    rng = np.random.default_rng(42)
    users = pd.DataFrame(
        {
            "User-ID": np.arange(1, n_users + 1),
            "Location": ["Unknown" for _ in range(n_users)],
            "Age": rng.integers(16, 70, size=n_users),
        }
    )

    isbn_values = books["ISBN"].dropna().astype(str).unique()
    rows = []
    for uid in users["User-ID"]:
        picks = rng.choice(isbn_values, size=min(interactions_per_user, len(isbn_values)), replace=False)
        for isbn in picks:
            raw = rng.normal(7.0, 1.7)
            rating = int(np.clip(round(raw), 0, 10))
            rows.append({"User-ID": int(uid), "ISBN": str(isbn), "Book-Rating": rating})
    ratings = pd.DataFrame(rows)
    return users, ratings


def preprocess_data(data_dir: Path | None = None, min_user_ratings: int = 5, min_book_ratings: int = 5) -> Dict[str, pd.DataFrame]:
    users, books, ratings = load_raw_data(data_dir)

    if ratings.empty:
        users, ratings = build_mock_ratings_from_books(books)

    for col in ["User-ID", "ISBN", "Book-Rating"]:
        if col not in ratings.columns:
            raise ValueError(f"Missing required ratings column: {col}")

    ratings = ratings.dropna(subset=["User-ID", "ISBN", "Book-Rating"]).copy()
    ratings["User-ID"] = pd.to_numeric(ratings["User-ID"], errors="coerce")
    ratings["Book-Rating"] = pd.to_numeric(ratings["Book-Rating"], errors="coerce")
    ratings["ISBN"] = ratings["ISBN"].astype(str)
    ratings = ratings.dropna(subset=["User-ID", "Book-Rating"]).copy()
    ratings["User-ID"] = ratings["User-ID"].astype(int)

    if books.empty:
        isbn_unique = ratings["ISBN"].unique()
        books = pd.DataFrame({"ISBN": isbn_unique, "Book-Title": isbn_unique, "Book-Author": "Unknown", "Year-Of-Publication": "N/A", "Publisher": "Unknown", "Image-URL-M": "https://via.placeholder.com/120x180?text=Book"})

    # Keep users/books with enough interactions
    user_counts = ratings["User-ID"].value_counts()
    valid_users = user_counts[user_counts >= min_user_ratings].index
    ratings = ratings[ratings["User-ID"].isin(valid_users)]

    book_counts = ratings["ISBN"].value_counts()
    valid_books = book_counts[book_counts >= min_book_ratings].index
    ratings = ratings[ratings["ISBN"].isin(valid_books)].copy()

    # Encode ids
    unique_users = sorted(ratings["User-ID"].unique())
    unique_books = sorted(ratings["ISBN"].unique())
    user2idx = {u: i for i, u in enumerate(unique_users)}
    book2idx = {b: i for i, b in enumerate(unique_books)}

    ratings["user_idx"] = ratings["User-ID"].map(user2idx)
    ratings["book_idx"] = ratings["ISBN"].map(book2idx)

    books_meta = books.copy()
    books_meta["ISBN"] = books_meta["ISBN"].astype(str)
    books_meta = books_meta.drop_duplicates(subset=["ISBN"])
    books_meta = books_meta[books_meta["ISBN"].isin(unique_books)]

    return {
        "users": users,
        "books": books,
        "ratings": ratings,
        "books_meta": books_meta,
        "user2idx": pd.Series(user2idx),
        "book2idx": pd.Series(book2idx),
    }
