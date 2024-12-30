BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER,
	"user_id"	TEXT NOT NULL UNIQUE,
	"role"	INTEGER NOT NULL DEFAULT 2,
	"name"	TEXT NOT NULL,
	"email"	TEXT NOT NULL UNIQUE,
	"password"	TEXT NOT NULL,
	"profile_picture"	TEXT,
	"gender"	TEXT NOT NULL,
	"dob"	DATE NOT NULL,
	"prefer_pdf_monthly_report"	INTEGER NOT NULL DEFAULT 0,
	"is_active"	INTEGER NOT NULL DEFAULT 1,
	"is_deleted"	INTEGER NOT NULL DEFAULT 0,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "books" (
	"id"	INTEGER,
	"book_id"	TEXT NOT NULL UNIQUE,
	"title"	TEXT NOT NULL,
	"isbn"	TEXT NOT NULL,
	"publication_date"	DATE NOT NULL,
	"edition"	TEXT NOT NULL,
	"description"	TEXT NOT NULL,
	"cover_image"	TEXT,
	"content"	TEXT,
	"price"	FLOAT NOT NULL DEFAULT 0,
	"added_by"	TEXT NOT NULL,
	"is_active"	BOOL NOT NULL DEFAULT FALSE,
	"is_deleted"	BOOL NOT NULL DEFAULT FALSE,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	FOREIGN KEY("added_by") REFERENCES "users"("user_id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "publisher" (
	"id"	INTEGER,
	"publisher_id"	TEXT NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"desc"	TEXT NOT NULL,
	"is_active"	BOOL NOT NULL DEFAULT FALSE,
	"is_deleted"	BOOL NOT NULL DEFAULT FALSE,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "language" (
	"id"	INTEGER,
	"lang_id"	TEXT NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"is_active"	BOOL NOT NULL DEFAULT FALSE,
	"is_deleted"	BOOL NOT NULL DEFAULT FALSE,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "category" (
	"id"	INTEGER,
	"category_id"	TEXT NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"is_active"	BOOL NOT NULL DEFAULT FALSE,
	"is_deleted"	BOOL NOT NULL DEFAULT FALSE,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "genre" (
	"id"	INTEGER,
	"genre_id"	TEXT NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"is_active"	BOOL NOT NULL DEFAULT FALSE,
	"is_deleted"	BOOL NOT NULL DEFAULT FALSE,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "authors" (
	"id"	INTEGER,
	"author_id"	TEXT NOT NULL,
	"name"	TEXT NOT NULL,
	"biography"	TEXT NOT NULL,
	"is_active"	BOOL NOT NULL DEFAULT FALSE,
	"is_deleted"	BOOL NOT NULL DEFAULT FALSE,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "reviews" (
	"id"	INTEGER,
	"book_id"	TEXT NOT NULL,
	"user_id"	TEXT NOT NULL,
	"rating"	INTEGER NOT NULL,
	"feedback"	TEXT NOT NULL,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	FOREIGN KEY("book_id") REFERENCES "books"("book_id"),
	FOREIGN KEY("user_id") REFERENCES "users"("user_id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "borrow_requests" (
	"id"	INTEGER,
	"book_id"	TEXT NOT NULL,
	"requested_by"	TEXT NOT NULL,
	"issued_by"	TEXT,
	"date_requested"	DATE NOT NULL,
	"date_issued"	DATE,
	"request_processed"	BOOL NOT NULL,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	FOREIGN KEY("issued_by") REFERENCES "users"("user_id"),
	FOREIGN KEY("requested_by") REFERENCES "users"("user_id"),
	FOREIGN KEY("book_id") REFERENCES "books"("book_id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "borrow_history" (
	"id"	INTEGER,
	"book_id"	TEXT NOT NULL,
	"issued_by"	TEXT,
	"issued_to"	TEXT NOT NULL,
	"date_of_issue"	DATE,
	"date_of_return"	DATE,
	"access_allowed"	BOOL NOT NULL,
	"access_token"	TEXT,
	"is_returned"	BOOL NOT NULL,
	"is_purchased"	BOOL NOT NULL DEFAULT 0,
	"is_opened"	INTEGER NOT NULL DEFAULT 0,
	"date_returned"	DATE,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	FOREIGN KEY("book_id") REFERENCES "books"("book_id"),
	FOREIGN KEY("issued_by") REFERENCES "users"("user_id"),
	FOREIGN KEY("issued_to") REFERENCES "users"("user_id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "book_purchases" (
	"id"	INTEGER,
	"book_id"	TEXT NOT NULL,
	"user_id"	TEXT NOT NULL,
	"cost"	FLOAT NOT NULL,
	"transaction_id"	TEXT NOT NULL,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	FOREIGN KEY("user_id") REFERENCES "users"("user_id"),
	FOREIGN KEY("book_id") REFERENCES "books"("book_id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "rel_books_publisher" (
	"id"	INTEGER,
	"publisher_id"	TEXT NOT NULL,
	"book_id"	TEXT NOT NULL,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	FOREIGN KEY("publisher_id") REFERENCES "publisher"("publisher_id"),
	FOREIGN KEY("book_id") REFERENCES "books"("book_id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "rel_books_language" (
	"id"	INTEGER,
	"lang_id"	TEXT NOT NULL,
	"book_id"	TEXT NOT NULL,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	FOREIGN KEY("lang_id") REFERENCES "language"("lang_id"),
	FOREIGN KEY("book_id") REFERENCES "books"("book_id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "rel_books_category" (
	"id"	INTEGER,
	"category_id"	TEXT NOT NULL,
	"book_id"	TEXT NOT NULL,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("book_id") REFERENCES "books"("book_id"),
	FOREIGN KEY("category_id") REFERENCES "category"("category_id")
);
CREATE TABLE IF NOT EXISTS "rel_books_genre" (
	"id"	INTEGER,
	"genre_id"	TEXT NOT NULL,
	"book_id"	TEXT NOT NULL,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("genre_id") REFERENCES "genre"("genre_id"),
	FOREIGN KEY("book_id") REFERENCES "books"("book_id")
);
CREATE TABLE IF NOT EXISTS "rel_books_authors" (
	"id"	INTEGER,
	"author_id"	TEXT NOT NULL,
	"book_id"	TEXT NOT NULL,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("author_id") REFERENCES "authors"("author_id"),
	FOREIGN KEY("book_id") REFERENCES "books"("book_id")
);
CREATE TABLE IF NOT EXISTS "trace" (
	"id"	INTEGER,
	"event"	INTEGER NOT NULL,
	"ip"	TEXT,
	"browser"	TEXT,
	"query"	TEXT NOT NULL,
	"error"	TEXT,
	"page_url"	TEXT,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "login_trace" (
	"id"	INTEGER,
	"role"	INT,
	"email"	TEXT NOT NULL,
	"ip"	TEXT NOT NULL,
	"browser"	TEXT NOT NULL,
	"user_agent"	TEXT NOT NULL,
	"user_id"	TEXT,
	"jwt"	TEXT,
	"process"	TEXT,
	"current_timestamp"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_updated_timestamp"	TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("user_id") REFERENCES "users"("user_id")
);
CREATE TRIGGER uist_users
	AFTER UPDATE ON users
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_books
	AFTER UPDATE ON books
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_category
	AFTER UPDATE ON category
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_genre
	AFTER UPDATE ON genre
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_authors
	AFTER UPDATE ON authors
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_reviews
	AFTER UPDATE ON reviews
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_language
	AFTER UPDATE ON language
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_publisher
	AFTER UPDATE ON publisher
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_borrow_requests
	AFTER UPDATE ON borrow_requests
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_borrow_history
	AFTER UPDATE ON borrow_history
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_book_purchases
	AFTER UPDATE ON book_purchases
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_rel_books_category
	AFTER UPDATE ON rel_books_category
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_rel_books_genre
	AFTER UPDATE ON rel_books_genre
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_rel_books_authors
	AFTER UPDATE ON rel_books_authors
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_rel_books_language
	AFTER UPDATE ON rel_books_language
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_rel_books_publisher
	AFTER UPDATE ON rel_books_publisher
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_trace
	AFTER UPDATE ON trace
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
CREATE TRIGGER uist_login_trace
	AFTER UPDATE ON login_trace
BEGIN
	UPDATE users SET last_updated_timestamp = CURRENT_TIMESTAMP WHERE NEW.id = OLD.id;
END;
COMMIT;
