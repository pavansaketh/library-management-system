### Library Management System

Phase 1: Database Design & SQL Implementation
Phase 2: Data Ingestion (Python ETL)
Phase 3: Django REST API Development

Objectives:
  Design a normalized, relational database for library operations.
  Build a Python ETL pipeline to validate and load real data.
  Expose the data via Django REST APIs for CRUD, analytics, and book management.

Phase 1: Database Design & SQL Implementation
  Design and implement the relational schema for the Library Management System in MySQL.

schema.sql → Database schema (tables, constraints, relationships)
insert_data.sql → Sample data (Books, Authors, Members, etc.)
queries.sql → Example queries (JOINs, CTEs, Window functions)

Foreign Keys and Constraints
CHECK and UNIQUE constraints
Many-to-Many relationships
Aggregations and JOIN queries

Phase 2: Data Ingestion (Python ETL)
Creating a Python script that reads raw CSV files, validates them, and loads the data into a SQL database using SQLAlchemy and Pydantic.

Main Scripts
  data_processor.py	Reads and validates CSV files (libraries, authors, books, members)
  models.py	SQLAlchemy ORM definitions
  schemas.py	Pydantic validation and normalization models
  
Read CSV files → from the csv_data directory
Validate rows → using Pydantic (schemas.py)
Insert or update records into MySQL using SQLAlchemy ORM


Phase 3: Django REST API Development
Component	Description:
  models.py	Defines Django ORM tables (Library, Book, Author, etc.)
  serializers.py	Converts models to/from JSON
  views.py	Contains business logic for CRUD and endpoints
  urls.py	Maps endpoints to views

Commands:
  cd phase3-django-api
  pip install -r requirements.txt
  python manage.py migrate
  python manage.py runserver


Access the API:
  /api/libraries/	GET / POST	List or create libraries
  /api/libraries/{id}/	GET / PUT / DELETE	Retrieve, update, delete a library
  /api/books/	GET / POST	List or add books
  /api/books/{id}/	GET / PUT / DELETE	Retrieve, update, delete a book
  /api/books/search?q=	GET	Search books by title, author, or category
  /api/members/	GET / POST	List or add members
  /api/borrowings/	GET / POST	Borrow or list borrowings
  /api/return/	POST	Return a borrowed book
  /api/reviews/	GET / POST	View or add book reviews
  /api/statistics/	GET	System stats (counts, averages, top books)

Dependencies:
  MySQL
  Python,
  SQLAlchemy,
  Pydantic
  Django REST Framework

