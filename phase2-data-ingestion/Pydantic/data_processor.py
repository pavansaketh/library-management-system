import argparse
import csv
import logging
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from models import Base, Library, Author, Book, Member
from schemas import LibraryIn, AuthorIn, BookIn, MemberIn, normalize_name

def parse_args():
    p = argparse.ArgumentParser(description="Process noisy CSVs and insert into a database (very simple).")
    p.add_argument("--directory", "-d", required=True, help="Path to directory containing CSV files")
    p.add_argument("--database-url", "--db", "-db", required=True, help="Database URL (e.g., sqlite:///library.db)")
    p.add_argument("--log-level", "-l", default="INFO", help="DEBUG, INFO, WARNING, ERROR")
    return p.parse_args()

def setup_logging(level: str):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(levelname)s - %(message)s"
    )

def make_session(db_url: str):
    engine = create_engine(db_url, echo=False, future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)()

    # tiny helper
def get_or_create_author(session, name: str, birth_date):
    if not name:
        return None
    normalized = normalize_name(name)
    stmt = select(Author).where(Author.normalized_name == normalized, Author.birth_date == birth_date)
    obj = session.execute(stmt).scalar_one_or_none()
    if obj:
        return obj
    obj = Author(name=normalized, normalized_name=normalized, birth_date=birth_date)
    session.add(obj)
    session.flush()
    return obj

def process_libraries(session, path: Path, stats: dict):
    f = path / "libraries.csv"
    if not f.exists():
        logging.info("libraries.csv not found, skipping")
        return
    with f.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                data = LibraryIn(**row)
                # check duplicate by email if present, else by name
                lib = None
                if data.email:
                    lib = session.execute(select(Library).where(Library.email == str(data.email))).scalar_one_or_none()
                if lib is None:
                    lib = session.execute(select(Library).where(Library.name == data.name)).scalar_one_or_none()
                if lib is None:
                    lib = Library(name=data.name, email=str(data.email) if data.email else None, phone=data.phone)
                    session.add(lib)
                    stats["libraries_inserted"] += 1
                else:
                    # tiny update
                    lib.name = data.name
                    lib.phone = data.phone
                    if data.email:
                        lib.email = str(data.email)
                    stats["libraries_updated"] += 1
            except Exception as e:
                stats["libraries_skipped"] += 1
                logging.warning(f"libraries.csv row skipped: {e}")
    session.commit()

def process_authors(session, path: Path, stats: dict):
    f = path / "authors.csv"
    if not f.exists():
        logging.info("authors.csv not found, skipping")
        return
    with f.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                data = AuthorIn(**row)
                normalized = data.normalized_name
                bdate = data.birth_date_parsed
                # get or create on (normalized_name, birth_date)
                stmt = select(Author).where(Author.normalized_name == normalized, Author.birth_date == bdate)
                obj = session.execute(stmt).scalar_one_or_none()
                if obj is None:
                    obj = Author(name=data.name, normalized_name=normalized, birth_date=bdate)
                    session.add(obj)
                    stats["authors_inserted"] += 1
                else:
                    obj.name = data.name  # keep latest display casing
                    stats["authors_updated"] += 1
            except Exception as e:
                stats["authors_skipped"] += 1
                logging.warning(f"authors.csv row skipped: {e}")
    session.commit()

def process_books(session, path: Path, stats: dict):
    f = path / "books.csv"
    if not f.exists():
        logging.info("books.csv not found, skipping")
        return
    with f.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                data = BookIn(**row)
                # dedupe by ISBN if present, else title+author
                obj = None
                if data.isbn:
                    obj = session.execute(select(Book).where(Book.isbn == data.isbn)).scalar_one_or_none()

                author = None
                if data.author_name:
                    author = get_or_create_author(session, data.author_name, None)

                if obj is None:
                    # try by title+author if isbn missing
                    if not data.isbn and data.title and author:
                        obj = session.execute(
                            select(Book).where(Book.title == data.title, Book.author_id == author.id)
                        ).scalar_one_or_none()

                if obj is None:
                    obj = Book(
                        title=data.title,
                        isbn=data.isbn,
                        published_date=data.published_date,
                        author=author
                    )
                    session.add(obj)
                    stats["books_inserted"] += 1
                else:
                    obj.title = data.title
                    obj.published_date = data.published_date
                    if data.isbn:
                        obj.isbn = data.isbn
                    if author:
                        obj.author = author
                    stats["books_updated"] += 1
            except Exception as e:
                stats["books_skipped"] += 1
                logging.warning(f"books.csv row skipped: {e}")
    session.commit()

def process_members(session, path: Path, stats: dict):
    f = path / "members.csv"
    if not f.exists():
        logging.info("members.csv not found, skipping")
        return
    with f.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                data = MemberIn(**row)
                obj = None
                if data.email:
                    obj = session.execute(select(Member).where(Member.email == str(data.email))).scalar_one_or_none()
                if obj is None:
                    # fallback duplicate check by name+phone
                    obj = session.execute(
                        select(Member).where(Member.name == data.name, Member.phone == data.phone)
                    ).scalar_one_or_none()

                if obj is None:
                    obj = Member(name=data.name, email=str(data.email) if data.email else None, phone=data.phone)
                    session.add(obj)
                    stats["members_inserted"] += 1
                else:
                    obj.name = data.name
                    obj.phone = data.phone
                    if data.email:
                        obj.email = str(data.email)
                    stats["members_updated"] += 1
            except Exception as e:
                stats["members_skipped"] += 1
                logging.warning(f"members.csv row skipped: {e}")
    session.commit()

def main():
    args = parse_args()
    setup_logging(args.log_level)
    session = make_session(args.database_url)

    stats = {
        "libraries_inserted": 0, "libraries_updated": 0, "libraries_skipped": 0,
        "authors_inserted": 0, "authors_updated": 0, "authors_skipped": 0,
        "books_inserted": 0, "books_updated": 0, "books_skipped": 0,
        "members_inserted": 0, "members_updated": 0, "members_skipped": 0,
    }

    try:
        base = Path(args.directory)
        process_libraries(session, base, stats)
        process_authors(session, base, stats)
        process_books(session, base, stats)
        process_members(session, base, stats)
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        session.rollback()
    finally:
        # summary
        logging.info("""Summary:
libraries: inserted={libraries_inserted}, updated={libraries_updated}, skipped={libraries_skipped}
authors:   inserted={authors_inserted}, updated={authors_updated}, skipped={authors_skipped}
books:     inserted={books_inserted}, updated={books_updated}, skipped={books_skipped}
members:   inserted={members_inserted}, updated={members_updated}, skipped={members_skipped}
""".format(**stats))

if __name__ == "__main__":
    main()






