import argparse
import json
import logging
import time
from typing import Any, Dict

from api_client import OpenLibraryClient
from models import WorkDetail, AuthorSearchDoc, Book, get_engine, get_sessionmaker, Base

from sqlalchemy import select


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("api_fetcher")



def get_author_key(client: OpenLibraryClient, author_name: str) -> str:
    """Find author key from the Open Library API."""
    data = client.search_authors(author_name)
    docs = data.get("docs", [])
    if not docs:
        raise ValueError(f"No author found for '{author_name}'")
    author = AuthorSearchDoc.model_validate(docs[0])
    logger.info(f"Found author: {author.name} ({author.key})")
    return author.key.lstrip("/") 


def fetch_books(client: OpenLibraryClient, author_key: str, limit: int):
    """Fetch works (books) for a given author."""
    data = client.get_author_works(author_key, limit=limit)
    return data.get("entries", [])


def save_book(session, detail: Dict[str, Any]):
    try:
        validated = WorkDetail.parse_obj(detail)
    except Exception:
        validated = WorkDetail(key=detail.get("key"), title=detail.get("title", "Untitled"), raw=detail)

    work_key = validated.key.lstrip("/") if validated.key else None
    title = validated.title or "Untitled"
    description = str(validated.description or "")
    subjects = json.dumps(validated.subjects or [])
    authors = ", ".join([a.get("author", {}).get("key", "") for a in detail.get("authors", [])])
    first_publish_date = validated.first_publish_date

    if session.execute(select(Book).where(Book.work_key == work_key)).first():
        logger.info(f"Skipping duplicate: {title}")
        return


    book = Book(
        work_key=work_key,
        title=title,
        authors=authors,
        first_publish_date=first_publish_date,
        subjects=subjects,
        description=description,
        raw=json.dumps(detail),
    )
    session.add(book)
    session.commit()
    logger.info(f"Saved: {title}")


def main():
    parser = argparse.ArgumentParser(description="Fetch author books from OpenLibrary API")
    parser.add_argument("--author", required=True, help="Author name (e.g., 'Charles Dickens')")
    parser.add_argument("--limit", type=int, default=10, help="Number of books to fetch")
    parser.add_argument("--db", required=True, help="Database URL (e.g., mysql+pymysql://user:pass@localhost/db)")
    args = parser.parse_args()


    client = OpenLibraryClient(rate_limit_seconds=1)
    engine = get_engine(args.db)
    Base.metadata.create_all(engine)
    Session = get_sessionmaker(engine)
    session = Session()

    author_key = get_author_key(client, args.author)
    works = fetch_books(client, author_key, args.limit)

    logger.info(f"Found {len(works)} works for {args.author}")


    for w in works:
        work_key = w["key"].lstrip("/")
        logger.info(f"Fetching details for {work_key}")
        detail = client.get_work_detail(work_key)
        save_book(session, detail)
        time.sleep(1) 

    logger.info("All books saved successfully!")
    session.close()
    client.close()


if __name__ == "__main__":
    main()
