Open Library Data Fetcher

A Python script that fetches book data from the Open Library API for your favorite author, validates the data, and stores it in the database.

openlibrary-data-fetcher/
    -api_client.py         
    -api_fetcher.py        
    -models.py             
    -README.md             

Dependencies:
    requests 
    sqlalchemy 
    pymysql 
    pydantic


Commands:
    python api_fetcher.py --author "Charles Dickens" --limit 10 --db "mysql+pymysql://root:root@localhost:3306/openlibrary"

Parameters:
 `--author`  Author name to fetch     
 `--limit`   Number of works to fetch 
 `--db`      SQLAlchemy DB URL         

