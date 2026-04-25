from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd
import torch

from model import BookRecommenderNet
from preprocess import preprocess_data

BASE_DIR = Path(__file__).parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"


class RecommenderService:
    def __init__(self):
        self.ready = False
        self._load_or_bootstrap()

    def _load_or_bootstrap(self):
        model_path = ARTIFACTS_DIR / "model.pt"
        if not model_path.exists():
            # lazy bootstrap with preprocessing-only metadata for demo mode
            data = preprocess_data()
            self.user2idx = data["user2idx"].to_dict()
            self.book2idx = data["book2idx"].to_dict()
            self.books_meta = data["books_meta"]
            self.metrics = {
                "rmse": None,
                "mae": None,
                "baseline_rmse": None,
                "baseline_mae": None,
                "train_loss": [],
                "val_loss": [],
                "num_users": int(data["ratings"]["User-ID"].nunique()),
                "num_books": int(data["ratings"]["ISBN"].nunique()),
                "num_ratings": int(len(data["ratings"])),
                "note": "Model not trained yet. Run train_model.py for full metrics.",
            }
            self.model = None
            self.ready = True
            return

        checkpoint = torch.load(model_path, map_location="cpu")
        self.model = BookRecommenderNet(
            checkpoint["num_users"],
            checkpoint["num_books"],
            checkpoint["embedding_dim"],
            checkpoint["hidden_dim"],
            checkpoint["dropout"],
        )
        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.eval()

        self.user2idx = joblib.load(ARTIFACTS_DIR / "user_encoder.pkl")
        self.book2idx = joblib.load(ARTIFACTS_DIR / "book_encoder.pkl")
        self.books_meta = joblib.load(ARTIFACTS_DIR / "books_metadata.pkl")

        metrics_file = ARTIFACTS_DIR / "metrics.json"
        if metrics_file.exists():
            with open(metrics_file, "r", encoding="utf-8") as f:
                self.metrics = json.load(f)
        else:
            self.metrics = {}

        self.ready = True

    def dataset_info(self) -> Dict[str, Any]:
        data = preprocess_data()
        ratings = data["ratings"]
        users = data["users"]
        books = data["books"]

        explicit_share = float((ratings["Book-Rating"] > 0).mean()) if len(ratings) else 0.0
        implicit_share = float((ratings["Book-Rating"] == 0).mean()) if len(ratings) else 0.0

        top_books = (
            ratings.groupby("ISBN").size().sort_values(ascending=False).head(10).reset_index(name="count")
        )
        top_authors = []
        if "Book-Author" in books.columns:
            bmap = books[["ISBN", "Book-Author"]].drop_duplicates()
            joined = top_books.merge(bmap, on="ISBN", how="left")
            top_authors = joined["Book-Author"].fillna("Unknown").value_counts().head(10).to_dict()

        return {
            "files": ["Users.csv", "Books.csv", "Ratings.csv"],
            "users_columns": list(users.columns),
            "books_columns": list(books.columns),
            "ratings_columns": list(ratings.columns),
            "num_users": int(ratings["User-ID"].nunique()),
            "num_books": int(ratings["ISBN"].nunique()),
            "num_ratings": int(len(ratings)),
            "explicit_share": explicit_share,
            "implicit_share": implicit_share,
            "rating_distribution": ratings["Book-Rating"].value_counts().sort_index().to_dict(),
            "age_distribution": users["Age"].dropna().astype(float).tolist()[:2000] if "Age" in users.columns else [],
            "top_books": top_books.to_dict(orient="records"),
            "top_authors": top_authors,
            "users_sample": users.head(5).fillna("N/A").to_dict(orient="records"),
            "books_sample": books.head(5).fillna("N/A").to_dict(orient="records"),
            "ratings_sample": ratings.head(5).fillna("N/A").to_dict(orient="records"),
        }

    def _predict_scores_for_user(self, user_id: int) -> pd.DataFrame:
        if user_id not in self.user2idx:
            raise KeyError("User not found")

        user_idx = self.user2idx[user_id]
        all_books = list(self.book2idx.keys())
        book_indices = np.array([self.book2idx[b] for b in all_books], dtype=np.int64)
        user_indices = np.full_like(book_indices, fill_value=user_idx)

        if self.model is None:
            # heuristic fallback when no trained model exists
            preds = np.random.default_rng(user_idx).uniform(5.5, 9.5, size=len(book_indices))
        else:
            with torch.no_grad():
                preds = self.model(
                    torch.tensor(user_indices, dtype=torch.long),
                    torch.tensor(book_indices, dtype=torch.long),
                ).numpy()

        recs = pd.DataFrame({"ISBN": all_books, "predicted_rating": preds})
        return recs

    def recommendations(self, user_id: int, top_k: int = 10) -> List[Dict[str, Any]]:
        recs = self._predict_scores_for_user(user_id)
        merged = recs.merge(self.books_meta, on="ISBN", how="left")
        merged = merged.sort_values("predicted_rating", ascending=False).head(top_k)

        out = []
        for _, row in merged.iterrows():
            out.append(
                {
                    "isbn": row.get("ISBN"),
                    "title": row.get("Book-Title", "Unknown"),
                    "author": row.get("Book-Author", "Unknown"),
                    "year": row.get("Year-Of-Publication", "N/A"),
                    "publisher": row.get("Publisher", "Unknown"),
                    "image_url": row.get("Image-URL-M", "https://via.placeholder.com/120x180?text=Book"),
                    "predicted_rating": float(row.get("predicted_rating", 0.0)),
                }
            )
        return out

    def predict_single(self, user_id: int, isbn: str) -> Dict[str, Any]:
        if user_id not in self.user2idx:
            raise KeyError("User not found")
        if isbn not in self.book2idx:
            raise KeyError("Book not found")

        u = torch.tensor([self.user2idx[user_id]], dtype=torch.long)
        b = torch.tensor([self.book2idx[isbn]], dtype=torch.long)

        if self.model is None:
            score = float(np.random.default_rng(self.user2idx[user_id]).uniform(5, 9))
        else:
            with torch.no_grad():
                score = float(self.model(u, b).item())

        return {"user_id": user_id, "isbn": isbn, "predicted_rating": score}

    def available_user_ids(self, limit: int = 300) -> List[int]:
        return list(self.user2idx.keys())[:limit]
