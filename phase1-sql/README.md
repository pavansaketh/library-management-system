# Library Management System – Phase 1: SQL

## Files Included
schema.sql - Defines all database tables, relationships, and constraints
data.sql - Inserts sample data into all tables for testing 
queries.sql -  Contains example SQL queries (JOINs, aggregations, subqueries, CTEs, window functions, and transactions) 


## schema.sql – Database Definition (DDL)

This file contains all SQL statements required to **create the database schema**.

### Includes:
- Database creation and table definitions
- Primary keys and Foreign keys
- UNIQUE, CHECK and NOT NULL constraints
- created_at and **updated_at timestamp fields

### Main Tables:
`Library`  Stores information about different library branches 
`Book`  Contains details about books and copies available per library 
`Author`  Stores information about authors 
`Category`  Defines various book categories 
`Member`  Represents students and faculty members 
`Borrowing`  Tracks which member borrowed which book and manages due/return dates 
`Review`  Stores book ratings and comments 
`BookAuthor`  Junction table linking books and authors 
`BookCategory`  Junction table linking books and categories 


## data.sql – Sample Data (DML):

This file populates the database with test data for all entities.

Includes:

Sample libraries (Central, Science, Arts)
Books, authors, and categories
Members (students and faculty)
Borrowing records and reviews
Book-author and book-category relationships

This dataset helps test the relationships and queries defined in the schema.

## queries.sql:

performs complex SQL queries on the database.

Example Queries:
    Books with their authors and categories
    Most borrowed books in the last 30 days
    Members with overdue books and calculated late fees
    Average rating per book
    Books available in each library with stock levels