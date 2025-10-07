Data Processor (Python + Pydantic + SQLAlchemy)


Project Overview:
This project processes raw or “noisy” CSV files — such as libraries, authors, books, and members — validates the data using Pydantic schemas, and loads it into a structured SQL database automatically.


Create and Activate Virtual Environment:
    python -m venv venv
    venv\Scripts\activate   # Windows


Install Required Packages
    pip install -r requirements.txt

Running the Script:
    python data_processor.py --directory ./csv_data --db mysql+pymysql://root:root@localhost:3306/sqlalchemy --log-level INFO

    - `--directory` or `-d`: Path to directory containing CSV files
    - `--database-url` or `--db`: Database connection URL
    - `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR)


dependencies:
    - Python
    - Pydantic v2 — Data validation & cleaning
    - SQLAlchemy ORM — Database interactions
    - MySQL — Supported databases
    - Logging