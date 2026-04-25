from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from recommender import RecommenderService

app = FastAPI(title="Book Recommender API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = RecommenderService()


class PredictRequest(BaseModel):
    user_id: int
    isbn: str


@app.get("/")
def root():
    return {"message": "Book recommendation API is running", "ready": service.ready}


@app.get("/dataset-info")
def dataset_info():
    return service.dataset_info()


@app.get("/metrics")
def metrics():
    return service.metrics


@app.get("/model-status")
def model_status():
    return service.model_status()


@app.get("/popular-books")
def popular_books():
    info = service.dataset_info()
    return {"top_books": info["top_books"]}


@app.get("/users")
def users():
    return {"user_ids": service.available_user_ids()}


@app.get("/recommendations/{user_id}")
def recommendations(user_id: int):
    try:
        recs = service.recommendations(user_id=user_id, top_k=10)
        return {"user_id": user_id, "recommendations": recs}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"User-ID {user_id} not found in dataset")


@app.get("/user-profile/{user_id}")
def user_profile(user_id: int):
    try:
        return service.user_profile(user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"User-ID {user_id} not found in dataset")


@app.post("/predict")
def predict(req: PredictRequest):
    try:
        return service.predict_single(user_id=req.user_id, isbn=req.isbn)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
