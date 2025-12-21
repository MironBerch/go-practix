from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class FilmworkBookmark(BaseModel):
    """Модель ответа для представления закладки."""

    filmwork_id: UUID


class Text(BaseModel):
    text: str


class Score(BaseModel):
    score: int = Field(gt=0, le=10)


class ReviewScore(BaseModel):
    score: Literal[1, 10]


class Review(BaseModel):
    """Модель ответа для представления рецензии на фильм."""

    id: UUID
    author_id: UUID
    filmwork_id: UUID
    text: str
    pub_date: datetime


class Vote(BaseModel):
    user_id: UUID
    score: int = Field(gt=0, le=10)


class Rating(BaseModel):
    average_rating: float | None = None
    votes: list[Vote] | None = Field(exclude=True)

    @model_validator(mode='before')
    @classmethod
    def scoring(cls, data: dict) -> dict:
        """
        Валидатор для подсчета средней пользовательской оценки.
        """
        votes: list[dict] = data.get('votes', [])
        if votes:
            data['average_rating'] = sum([Vote(**vote).score for vote in votes]) / (len(votes))
        return data


class ReviewRating(BaseModel):
    votes: list[Vote] | None = Field(exclude=True)
    likes: int = Field(default=0)
    dislikes: int = Field(default=0)
    likes_sum: int = Field(default=0)

    @model_validator(mode='before')
    @classmethod
    def scoring(cls, data: dict) -> dict:
        """
        Валидатор для подсчета лайков и дизлайков.
        """
        votes: list[dict] = data.get('votes', [])
        data['likes'] = data.get('likes', 0)
        data['dislikes'] = data.get('dislikes', 0)
        data['likes_sum'] = data.get('likes_sum', 0)
        if votes:
            for vote in votes:
                vote = Vote(**vote)
                if vote.score == 10:
                    data['likes'] += 1
                if vote.score == 1:
                    data['dislikes'] += 1
            data['likes_sum'] = data['likes'] - data['dislikes']
        return data
