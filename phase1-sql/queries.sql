use mysql;


-- BOOKS WITH THEIR AUTHORS AND CATEGORIES (one row per book)
SELECT
  b.book_id,
  b.title,
  l.name AS library_name,
  -- get authors as a comma-separated string
  (SELECT GROUP_CONCAT(CONCAT(a.first_name,' ',a.last_name) SEPARATOR ', ')
   FROM BookAuthor ba JOIN Author a ON ba.author_id = a.author_id
   WHERE ba.book_id = b.book_id
  ) AS authors,
  -- get categories as a comma-separated string
  (SELECT GROUP_CONCAT(c.name SEPARATOR ', ')
   FROM BookCategory bc JOIN Category c ON bc.category_id = c.category_id
   WHERE bc.book_id = b.book_id
  ) AS categories
FROM Book b
LEFT JOIN Library l ON b.library_id = l.library_id
ORDER BY b.title;


-- MOST BORROWED BOOKS IN THE LAST 30 DAYS (simple COUNT)

SELECT
  b.book_id,
  b.title,
  COUNT(*) AS borrow_count
FROM Borrowing br
JOIN Book b ON br.book_id = b.book_id
WHERE br.borrow_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY b.book_id, b.title
ORDER BY borrow_count DESC
LIMIT 10;


-- MEMBERS WITH OVERDUE BOOKS AND A SIMPLE LATE FEE CALCULATION
SELECT
  m.member_id,
  CONCAT(m.first_name, ' ', m.last_name) AS member_name,
  b.book_id,
  b.title,
  br.due_date,
  DATEDIFF(CURDATE(), br.due_date) AS days_overdue,
  ROUND(GREATEST(0, DATEDIFF(CURDATE(), br.due_date)) * 0.50, 2) AS computed_late_fee
FROM Borrowing br
JOIN Member m ON br.member_id = m.member_id
JOIN Book b ON br.book_id = b.book_id
WHERE br.return_date IS NULL
  AND br.due_date < CURDATE()
ORDER BY days_overdue DESC;


-- AVERAGE RATING PER BOOK (simple aggregation) WITH ONE AUTHOR SHOWN
SELECT
  b.book_id,
  b.title,
  ROUND(AVG(r.rating), 2) AS avg_rating,
  COUNT(r.review_id) AS num_reviews,
  -- pick one author to keep it simple
  (SELECT CONCAT(a.first_name,' ',a.last_name)
   FROM BookAuthor ba JOIN Author a ON ba.author_id = a.author_id
   WHERE ba.book_id = b.book_id
   LIMIT 1
  ) AS one_author
FROM Book b
LEFT JOIN Review r ON b.book_id = r.book_id
GROUP BY b.book_id, b.title
ORDER BY avg_rating DESC, num_reviews DESC;

-- BOOKS AVAILABLE IN EACH LIBRARY (stock levels)
SELECT
  l.library_id,
  l.name AS library_name,
  COALESCE(SUM(b.available_copies), 0) AS total_available,
  COALESCE(SUM(b.total_copies), 0) AS total_copies
FROM Library l
LEFT JOIN Book b ON b.library_id = l.library_id
GROUP BY l.library_id, l.name;

-- (b) Per-book listing (which library each book is in)
SELECT
  b.book_id,
  b.title,
  l.name AS library_name,
  b.total_copies,
  b.available_copies
FROM Book b
LEFT JOIN Library l ON b.library_id = l.library_id
ORDER BY l.name, b.title;


-- SUBQUERY EXAMPLES (very simple)
-- a) Books never borrowed
SELECT b.book_id, b.title
FROM Book b
WHERE NOT EXISTS (
  SELECT 1 FROM Borrowing br WHERE br.book_id = b.book_id
);

-- b) Members with more than 2 borrowings
SELECT
  m.member_id,
  CONCAT(m.first_name,' ',m.last_name) AS member_name,
  COUNT(br.borrowing_id) AS borrow_count
FROM Member m
JOIN Borrowing br ON m.member_id = br.member_id
GROUP BY m.member_id
HAVING COUNT(br.borrowing_id) > 2;

-- 7) CTE (Common Table Expression) + simple WINDOW function example
WITH borrow_counts AS (
  SELECT book_id, COUNT(*) AS total_borrows
  FROM Borrowing
  GROUP BY book_id
)
SELECT
  ROW_NUMBER() OVER (ORDER BY bc.total_borrows DESC) AS ranks,
  b.book_id,
  b.title,
  bc.total_borrows
FROM borrow_counts bc
JOIN Book b ON bc.book_id = b.book_id
ORDER BY bc.total_borrows DESC
LIMIT 5;

