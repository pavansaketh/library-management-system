create database mysql;
show databases;
use mysql;

CREATE TABLE Library (
    library_id     INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    campus_location VARCHAR(100),
    contact_email  VARCHAR(100),
    phone_number   VARCHAR(20),
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_library_name UNIQUE (name)
);

CREATE TABLE Book (
    book_id           INT AUTO_INCREMENT PRIMARY KEY,
    title             VARCHAR(200) NOT NULL,
    isbn              VARCHAR(20) UNIQUE,
    publication_date  DATE,
    total_copies      INT DEFAULT 0,
    available_copies  INT DEFAULT 0,
    library_id        INT,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_book_library
        FOREIGN KEY (library_id) REFERENCES Library(library_id),
    CONSTRAINT chk_book_copies CHECK (available_copies <= total_copies)
);

CREATE TABLE Author (
    author_id    INT AUTO_INCREMENT PRIMARY KEY,
    first_name   VARCHAR(100) NOT NULL,
    last_name    VARCHAR(100) NOT NULL,
    birth_date   DATE,
    nationality  VARCHAR(100),
    biography    TEXT,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_author_natural UNIQUE (first_name, last_name, birth_date)
);

CREATE TABLE Category (
    category_id  INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    description  TEXT,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_category_name UNIQUE (name)
);

CREATE TABLE Member (
    member_id         INT AUTO_INCREMENT PRIMARY KEY,
    first_name        VARCHAR(100) NOT NULL,
    last_name         VARCHAR(100) NOT NULL,
    email             VARCHAR(100) UNIQUE,
    phone             VARCHAR(20),
    member_type       ENUM('student','faculty') NOT NULL,
    registration_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE Borrowing (
    borrowing_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id    INT NOT NULL,
    book_id      INT NOT NULL,
    borrow_date  DATE NOT NULL,
    due_date     DATE NOT NULL,
    return_date  DATE,
    late_fee     DECIMAL(6,2) NOT NULL DEFAULT 0,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_borrowing_member FOREIGN KEY (member_id) REFERENCES Member(member_id),
    CONSTRAINT fk_borrowing_book   FOREIGN KEY (book_id)   REFERENCES Book(book_id),
    CONSTRAINT chk_borrowing_dates CHECK (due_date >= borrow_date),
    CONSTRAINT chk_return_after_borrow CHECK (return_date IS NULL OR return_date >= borrow_date),
    CONSTRAINT chk_late_fee_nonneg CHECK (late_fee >= 0)
);

CREATE TABLE Review (
    review_id   INT AUTO_INCREMENT PRIMARY KEY,
    member_id   INT NOT NULL,
    book_id     INT NOT NULL,
    rating      TINYINT NOT NULL,
    comment     TEXT,
    review_date DATE NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_review_member FOREIGN KEY (member_id) REFERENCES Member(member_id),
    CONSTRAINT fk_review_book   FOREIGN KEY (book_id)   REFERENCES Book(book_id),
    CONSTRAINT chk_rating_1_5   CHECK (rating BETWEEN 1 AND 5)
);

CREATE TABLE BookAuthor (
    book_id    INT NOT NULL,
    author_id  INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (book_id, author_id),
    CONSTRAINT fk_ba_book   FOREIGN KEY (book_id)   REFERENCES Book(book_id),
    CONSTRAINT fk_ba_author FOREIGN KEY (author_id) REFERENCES Author(author_id)
);

CREATE TABLE BookCategory (
    book_id     INT NOT NULL,
    category_id INT NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (book_id, category_id),
    CONSTRAINT fk_bc_book     FOREIGN KEY (book_id)     REFERENCES Book(book_id),
    CONSTRAINT fk_bc_category FOREIGN KEY (category_id) REFERENCES Category(category_id)
);
