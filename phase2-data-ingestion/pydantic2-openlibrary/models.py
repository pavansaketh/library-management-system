from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    JSON,
    create_engine,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json


class AuthorSearchDoc(BaseModel):
    key: str
    name: str
    top_work: Optional[str] 
    work_count: Optional[int] 

class WorkDetail(BaseModel):
    key: str
    title: str
    description: Optional[Any] = None
    subjects: Optional[List[str]] = None
    created: Optional[Dict[str, Any]] = None
    first_publish_date: Optional[str] = None
    covers: Optional[List[int]] = None
    links: Optional[List[Dict[str, Any]]] = None
    subjects_times: Optional[List[Any]] = None
    raw: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("description", mode="before")
    def description_to_str(cls, v):
        if v is None:
            return None
        if isinstance(v, dict) and "value" in v:
            return v["value"]
        if isinstance(v, str):
            return v
        return str(v)

    @field_validator("raw", mode="before")
    def set_raw(cls, v, values, **kwargs):
        return v or {k: values.get(k) for k in values.keys()}


Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, autoincrement=True)
    work_key = Column(String(64), nullable=False, unique=True, index=True)
    title = Column(String(1000), nullable=False)
    authors = Column(String(1000), nullable=True)
    first_publish_date = Column(String(50), nullable=True)

    subjects = Column(SA_JSON, nullable=True)     
    isbn = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    raw = Column(JSON, nullable=True)           

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("isbn", name="uq_books_isbn"),
    )


def get_engine(database_url: str):

    return create_engine(
        database_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
        connect_args={"charset": "utf8mb4"},
    )

def get_sessionmaker(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)
