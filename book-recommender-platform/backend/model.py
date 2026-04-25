import torch
import torch.nn as nn


class BookRecommenderNet(nn.Module):
    """Embedding-based neural recommender for user-book rating prediction."""

    def __init__(self, num_users: int, num_books: int, embedding_dim: int = 64, hidden_dim: int = 128, dropout: float = 0.2):
        super().__init__()
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.book_embedding = nn.Embedding(num_books, embedding_dim)

        self.mlp = nn.Sequential(
            nn.Linear(embedding_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
        )

    def forward(self, user_ids: torch.Tensor, book_ids: torch.Tensor) -> torch.Tensor:
        user_vec = self.user_embedding(user_ids)
        book_vec = self.book_embedding(book_ids)
        x = torch.cat([user_vec, book_vec], dim=1)
        return self.mlp(x).squeeze(-1)
