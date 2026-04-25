from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset

from model import BookRecommenderNet
from preprocess import preprocess_data

BASE_DIR = Path(__file__).parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def train(epochs: int = 8, batch_size: int = 1024, lr: float = 1e-3):
    data = preprocess_data()
    ratings = data["ratings"]

    X_user = ratings["user_idx"].values.astype(np.int64)
    X_book = ratings["book_idx"].values.astype(np.int64)
    y = ratings["Book-Rating"].values.astype(np.float32)

    x_u_train, x_u_val, x_b_train, x_b_val, y_train, y_val = train_test_split(
        X_user, X_book, y, test_size=0.2, random_state=42
    )

    train_ds = TensorDataset(
        torch.tensor(x_u_train), torch.tensor(x_b_train), torch.tensor(y_train)
    )
    val_ds = TensorDataset(
        torch.tensor(x_u_val), torch.tensor(x_b_val), torch.tensor(y_val)
    )

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)

    model = BookRecommenderNet(
        num_users=ratings["user_idx"].nunique(),
        num_books=ratings["book_idx"].nunique(),
        embedding_dim=64,
        hidden_dim=128,
        dropout=0.2,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    train_losses, val_losses = [], []

    for epoch in range(epochs):
        model.train()
        epoch_train = 0.0
        for u, b, target in train_loader:
            u, b, target = u.to(device), b.to(device), target.to(device)
            optimizer.zero_grad()
            pred = model(u, b)
            loss = criterion(pred, target)
            loss.backward()
            optimizer.step()
            epoch_train += loss.item() * len(u)

        epoch_train /= len(train_ds)

        model.eval()
        epoch_val = 0.0
        preds, trues = [], []
        with torch.no_grad():
            for u, b, target in val_loader:
                u, b, target = u.to(device), b.to(device), target.to(device)
                pred = model(u, b)
                loss = criterion(pred, target)
                epoch_val += loss.item() * len(u)
                preds.extend(pred.cpu().numpy().tolist())
                trues.extend(target.cpu().numpy().tolist())

        epoch_val /= len(val_ds)
        train_losses.append(epoch_train)
        val_losses.append(epoch_val)
        print(f"Epoch {epoch + 1}/{epochs}: train_loss={epoch_train:.4f}, val_loss={epoch_val:.4f}")

    rmse = mean_squared_error(trues, preds) ** 0.5
    mae = mean_absolute_error(trues, preds)
    baseline = float(np.mean(y_train))
    baseline_rmse = mean_squared_error(trues, np.full_like(trues, baseline)) ** 0.5
    baseline_mae = mean_absolute_error(trues, np.full_like(trues, baseline))

    torch.save(
        {
            "state_dict": model.cpu().state_dict(),
            "num_users": ratings["user_idx"].nunique(),
            "num_books": ratings["book_idx"].nunique(),
            "embedding_dim": 64,
            "hidden_dim": 128,
            "dropout": 0.2,
        },
        ARTIFACTS_DIR / "model.pt",
    )

    joblib.dump(data["user2idx"].to_dict(), ARTIFACTS_DIR / "user_encoder.pkl")
    joblib.dump(data["book2idx"].to_dict(), ARTIFACTS_DIR / "book_encoder.pkl")
    joblib.dump(data["books_meta"], ARTIFACTS_DIR / "books_metadata.pkl")

    metrics = {
        "rmse": float(rmse),
        "mae": float(mae),
        "baseline_rmse": float(baseline_rmse),
        "baseline_mae": float(baseline_mae),
        "train_loss": [float(x) for x in train_losses],
        "val_loss": [float(x) for x in val_losses],
        "num_users": int(ratings["User-ID"].nunique()),
        "num_books": int(ratings["ISBN"].nunique()),
        "num_ratings": int(len(ratings)),
    }

    with open(ARTIFACTS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print("Saved artifacts to backend/artifacts")


if __name__ == "__main__":
    train()
