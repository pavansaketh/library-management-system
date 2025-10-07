from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
import re

def clean_isbn(s: str) -> str:
    if not s:
        return None
    return re.sub(r"[\s-]", "", s)

def is_valid_isbn10(s: str) -> bool:
    if len(s) != 10:
        return False
    total = 0
    for i, ch in enumerate(s, start=1):
        if ch == 'X' and i == 10:
            val = 10
        elif ch.isdigit():
            val = int(ch)
        else:
            return False
        total += i * val
    return total % 11 == 0

def is_valid_isbn13(s: str) -> bool:
    if len(s) != 13 or not s.isdigit():
        return False
    total = 0
    for i, ch in enumerate(s):
        n = int(ch)
        total += n if i % 2 == 0 else 3 * n
    return total % 10 == 0

def parse_date(s: str):
    if not s or not str(s).strip():
        return None
    s = str(s).strip()
    # accept a couple of very basic formats
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None  # if we can't parse, we just return None (not an error)

def normalize_name(name: str) -> str:
    if not name:
        return ""
    return " ".join(name.strip().split()).title()

def normalize_phone(phone: str) -> str:
    if not phone:
        return None
    digits = re.sub(r"\D", "", str(phone))
    if not digits:
        return None
    # Very simple: return E.164-like, just prefix '+' and keep digits
    return "+" + digits

class LibraryIn(BaseModel):
    name: str
    email: EmailStr 
    phone: str 

    @field_validator("name")
    @classmethod
    def _v_name(cls, v):
        v = normalize_name(v)
        if not v:
            raise ValueError("name is required")
        return v

    @field_validator("phone")
    @classmethod
    def _v_phone(cls, v):
        return normalize_phone(v)

class AuthorIn(BaseModel):
    name: str
    birth_date: str  # accept string then parse

    @field_validator("name")
    @classmethod
    def _v_name(cls, v):
        return normalize_name(v)

    @field_validator("birth_date")
    @classmethod
    def _v_birth_date(cls, v):
        return parse_date(v)

    # expose normalized fields (tiny trick)
    @property
    def normalized_name(self) -> str:
        return normalize_name(self.name)

    @property
    def birth_date_parsed(self):
        return parse_date(self.birth_date)

class BookIn(BaseModel):
    title: str
    isbn: str
    author_name: str
    published_date: str

    @field_validator("title")
    @classmethod
    def _v_title(cls, v):
        v = " ".join(str(v).strip().split())
        if not v:
            raise ValueError("title is required")
        return v

    @field_validator("isbn")
    @classmethod
    def _v_isbn(cls, v):
        if v is None or str(v).strip() == "":
            return None
        clean = clean_isbn(str(v))
        if clean is None:
            return None
        if len(clean) == 10 and is_valid_isbn10(clean):
            return clean
        if len(clean) == 13 and is_valid_isbn13(clean):
            return clean
        raise ValueError("invalid ISBN")

    @field_validator("author_name")
    @classmethod
    def _v_author_name(cls, v):
        return normalize_name(v) if v else None

    @field_validator("published_date")
    @classmethod
    def _v_pubdate(cls, v):
        return parse_date(v)

class MemberIn(BaseModel):
    name: str
    email: EmailStr
    phone: str

    @field_validator("name")
    @classmethod
    def _v_name(cls, v):
        v = normalize_name(v)
        if not v:
            raise ValueError("name is required")
        return v

    @field_validator("phone")
    @classmethod
    def _v_phone(cls, v):
        return normalize_phone(v)
