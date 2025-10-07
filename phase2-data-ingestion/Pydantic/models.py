from datetime import date
from typing import Optional

from sqlalchemy import (
    String, Integer, Date, ForeignKey, UniqueConstraint, Index, create_engine, text
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass

class Library(Base):
    __tablename__ = "libraries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    __table_args__ = (
        Index("ix_libraries_name", "name"),
    )

class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(200), nullable=False)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    books = relationship("Book", back_populates="author", cascade="all,delete-orphan")

    __table_args__ = (
        UniqueConstraint("normalized_name", "birth_date", name="uq_author_unique"),
        Index("ix_authors_normalized_name", "normalized_name"),
    )

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    isbn: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True)
    published_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("authors.id"), nullable=True)
    author = relationship("Author", back_populates="books")

    __table_args__ = (
        Index("ix_books_title", "title"),
    )

class Member(Base):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    __table_args__ = (
        Index("ix_members_name", "name"),
    )



username = "root"
password = "root"
host = "localhost"
port = 3306
database = "sqlalchemy"


engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")

connection = engine.connect()

res = connection.execute(text("show databases"))
Base.metadata.create_all(engine)
connection.commit()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
