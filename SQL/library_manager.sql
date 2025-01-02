CREATE TYPE "bk_genres" AS ENUM (
    'fiction',
    'mystery',
    'fantasy',
    'biography',
    'history',
    'romance',
    'self_help',
    'young_adult',
    'horror',
    'poetry',
    'children',
    'thriller',
    'graphic_novel',
    'philosophy',
    'business',
    'art',
    'psychology',
    'education'
    );

CREATE TABLE "students"
(
    "id"              VARCHAR(32) NOT NULL,
    "name"            VARCHAR(32) NOT NULL,
    "gender"          VARCHAR(32),
    "violation_count" INTEGER     NOT NULL DEFAULT 0,
    PRIMARY KEY ("id")
);

CREATE TABLE "books"
(
    "isbn"             VARCHAR(32) NOT NULL,
    "name"             VARCHAR(32) NOT NULL,
    "copies"           INTEGER     NOT NULL,
    "available_copies" INTEGER     NOT NULL,
    "description"      TEXT,
    "publish_date"     DATE,
    PRIMARY KEY ("isbn")
);

CREATE TABLE "rooms"
(
    "id"       INTEGER     NOT NULL,
    "name"     VARCHAR(32),
    "location" VARCHAR(32) NOT NULL,
    PRIMARY KEY ("id")
);

CREATE TABLE "seats"
(
    "room_id" INTEGER NOT NULL,
    "seat_id" INTEGER NOT NULL,
    PRIMARY KEY ("room_id", "seat_id"),
    FOREIGN KEY ("room_id") REFERENCES "rooms" ("id")
);

CREATE TABLE "borrow_records"
(
    "id"          SERIAL      NOT NULL,
    "sid"         VARCHAR(32) NOT NULL,
    "isbn"        VARCHAR(32) NOT NULL,
    "borrow_date" DATE        NOT NULL,
    "return_date" DATE                 DEFAULT NULL,
    "due_date"    DATE        NOT NULL,
    "is_overdue"  BOOLEAN     NOT NULL DEFAULT false,
    PRIMARY KEY ("id"),
    FOREIGN KEY ("sid") REFERENCES "students" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
    FOREIGN KEY ("isbn") REFERENCES "books" ("isbn") ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE "reservation_records"
(
    "id"         SERIAL      NOT NULL,
    "sid"        VARCHAR(32) NOT NULL,
    "room_id"    INTEGER     NOT NULL,
    "seat_id"    INTEGER,
    "start_time" TIMESTAMP   NOT NULL,
    "end_time"   TIMESTAMP   NOT NULL,
    PRIMARY KEY ("id"),
    FOREIGN KEY ("sid") REFERENCES "students" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
    FOREIGN KEY ("room_id") REFERENCES "rooms" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE "borrow_violation_records"
(
    "sid"              VARCHAR(32) NOT NULL,
    "record_id"        SERIAL NOT NULL,
    "violation_date"   DATE        NOT NULL,
    "violation_reason" TEXT,
    PRIMARY KEY ("sid", "record_id"),
    FOREIGN KEY ("sid") REFERENCES "students" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
    FOREIGN KEY ("record_id") REFERENCES "borrow_records" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE "reservation_violation_records"
(
    "sid"              VARCHAR(32) NOT NULL,
    "record_id"        SERIAL NOT NULL,
    "violation_date"   DATE        NOT NULL,
    "violation_reason" TEXT,
    PRIMARY KEY ("sid", "record_id"),
    FOREIGN KEY ("sid") REFERENCES "students" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
    FOREIGN KEY ("record_id") REFERENCES "reservation_records" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE "authors"
(
    "isni"       VARCHAR(32) NOT NULL UNIQUE,
    "name"       VARCHAR(32) NOT NULL,
    "desc"       TEXT,
    "birth_date" DATE,
    "death_date" DATE,
    PRIMARY KEY ("isni")
);

CREATE TABLE "book_genres"
(
    "genres" BK_GENRES NOT NULL UNIQUE,
    "isbn"   VARCHAR(32) NOT NULL,
    PRIMARY KEY ("genres", "isbn"),
    FOREIGN KEY ("isbn") REFERENCES "books" ("isbn") ON UPDATE NO ACTION ON DELETE NO ACTION
);
CREATE TABLE "genres"
(
    "genres" BK_GENRES NOT NULL,
    PRIMARY KEY ("genres"),
    FOREIGN KEY ("genres") REFERENCES "book_genres" ("genres") ON UPDATE NO ACTION ON DELETE NO ACTION
);


CREATE TABLE "book_author"
(
    "isni" VARCHAR(32) NOT NULL UNIQUE,
    "isbn" VARCHAR(32) NOT NULL,
    PRIMARY KEY ("isni", "isbn"),
    FOREIGN KEY ("isni") REFERENCES "authors" ("isni") ON UPDATE NO ACTION ON DELETE NO ACTION,
    FOREIGN KEY ("isbn") REFERENCES "books" ("isbn") ON UPDATE NO ACTION ON DELETE NO ACTION
);



CREATE OR REPLACE VIEW book_view AS
SELECT b.isbn,
       b.name                   AS book_name,
       b.copies                 AS total_copies,
       b.available_copies,
       b.description,
       b.publish_date,
       STRING_AGG(a.name, ', ') AS authors
FROM books b
         LEFT JOIN book_author ba ON b.isbn = ba.isbn
         LEFT JOIN authors a ON ba.isni = a.isni
GROUP BY b.isbn;


CREATE VIEW student_borrow_summary AS
SELECT s.id                                                   AS student_id,
       s.name                                                 AS student_name,
       COUNT(CASE WHEN br.return_date IS NULL THEN 1 END)     AS current_borrowed_books,
       COUNT(CASE WHEN br.return_date IS NOT NULL THEN 1 END) AS returned_books,
       COUNT(*)                                               AS total_borrowed_books
FROM students s
         LEFT JOIN borrow_records br ON s.id = br.sid
GROUP BY s.id, s.name;


CREATE VIEW student_violation_summary AS
SELECT s.id                                                            AS student_id,
       s.name                                                          AS student_name,
       COUNT(DISTINCT bvr.record_id)                                   AS book_violations,
       COUNT(DISTINCT rvr.record_id)                                   AS reservation_violations,
       (COUNT(DISTINCT bvr.record_id) + COUNT(DISTINCT rvr.record_id)) AS total_violations
FROM students s
         LEFT JOIN borrow_violation_records bvr ON s.id = bvr.sid
         LEFT JOIN reservation_violation_records rvr ON s.id = rvr.sid
GROUP BY s.id;


CREATE VIEW overdue_borrow_records AS
SELECT br.id                        AS record_id,
       br.sid                       AS student_id,
       s.name                       AS student_name,
       br.isbn                      AS book_isbn,
       b.name                       AS book_name,
       br.borrow_date,
       br.due_date,
       br.return_date,
       (CURRENT_DATE - br.due_date) AS overdue_days
FROM borrow_records br
         JOIN students s ON br.sid = s.id
         JOIN books b ON br.isbn = b.isbn
WHERE br.is_overdue = TRUE;


CREATE VIEW borrow_analysis_view AS
SELECT b.isbn,
       b.name       AS book_name,
       COUNT(br.id) AS borrow_count
FROM books b
         LEFT JOIN borrow_records br ON b.isbn = br.isbn
GROUP BY b.isbn;


CREATE OR REPLACE VIEW all_records_view AS
SELECT 'borrow'       AS record_type,
       br.id          AS record_id,
       br.sid         AS student_id,
       s.name         AS student_name,
       br.isbn        AS book_isbn,
       b.name         AS book_name,
       br.borrow_date AS start_time,
       br.due_date    AS end_time,
       br.return_date,
       NULL           AS room_id,
       NULL           AS seat_id
FROM borrow_records br
         JOIN students s ON br.sid = s.id
         JOIN books b ON br.isbn = b.isbn

UNION ALL

SELECT 'reservation' AS record_type,
       rr.id         AS record_id,
       rr.sid        AS student_id,
       s.name        AS student_name,
       NULL          AS book_isbn,
       NULL          AS book_name,
       rr.start_time,
       rr.end_time,
       NULL          AS return_date,
       rr.room_id,
       rr.seat_id
FROM reservation_records rr
         JOIN students s ON rr.sid = s.id;



CREATE OR REPLACE FUNCTION check_book_availability() RETURNS TRIGGER AS
$$
DECLARE
    current_copies INTEGER;
BEGIN

    SELECT available_copies INTO current_copies FROM books WHERE isbn = NEW.isbn;


    IF current_copies IS NULL THEN
        RAISE EXCEPTION 'The book with ISBN % does not exist.', NEW.isbn;
    ELSIF current_copies = 0 THEN
        RAISE EXCEPTION 'No available copies for the book with ISBN %.', NEW.isbn;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_book_availability
    BEFORE INSERT
    ON borrow_records
    FOR EACH ROW
EXECUTE FUNCTION check_book_availability();


CREATE OR REPLACE FUNCTION decrement_available_copies()
    RETURNS TRIGGER AS
$$
BEGIN
    UPDATE books
    SET available_copies = available_copies - 1
    WHERE isbn = NEW.isbn;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_decrement_available_copies
    AFTER INSERT
    ON borrow_records
    FOR EACH ROW
EXECUTE FUNCTION decrement_available_copies();


CREATE OR REPLACE FUNCTION increment_available_copies()
    RETURNS TRIGGER AS
$$
BEGIN
    UPDATE books
    SET available_copies = available_copies + 1
    WHERE isbn = NEW.isbn
      AND NEW.return_date IS NOT NULL;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_increment_available_copies
    AFTER UPDATE
    ON borrow_records
    FOR EACH ROW
    WHEN (NEW.return_date IS NOT NULL)
EXECUTE FUNCTION increment_available_copies();


CREATE OR REPLACE FUNCTION check_seat_reservation()
    RETURNS TRIGGER AS
$$
DECLARE
    overlapping_reservation_count INTEGER;
BEGIN

    SELECT COUNT(*)
    INTO overlapping_reservation_count
    FROM reservation_records
    WHERE room_id = NEW.room_id
      AND seat_id = NEW.seat_id
      AND (NEW.start_time < end_time AND NEW.end_time > start_time);


    IF overlapping_reservation_count > 0 THEN
        RAISE EXCEPTION 'The seat in room % with seat ID % is already reserved during the specified time period.', NEW.room_id, NEW.seat_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_seat_reservation
    BEFORE INSERT
    ON reservation_records
    FOR EACH ROW
EXECUTE FUNCTION check_seat_reservation();


CREATE OR REPLACE FUNCTION decrease_violation_count()
    RETURNS TRIGGER AS
$$
BEGIN

    IF OLD.sid IS NOT NULL THEN
        UPDATE students
        SET violation_count = GREATEST(violation_count - 1, 0)
        WHERE id = OLD.sid;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_decrease_borrow_violation_count
    AFTER DELETE
    ON borrow_violation_records
    FOR EACH ROW
EXECUTE FUNCTION decrease_violation_count();

CREATE TRIGGER trg_decrease_reservation_violation_count
    AFTER DELETE
    ON reservation_violation_records
    FOR EACH ROW
EXECUTE FUNCTION decrease_violation_count();



CREATE OR REPLACE PROCEDURE borrow_book(
    student_id VARCHAR,
    book_isbn VARCHAR,
    borrow_date DATE,
    due_date DATE
) AS
$$
DECLARE
    available_copies INTEGER;
BEGIN

    SELECT available_copies
    INTO available_copies
    FROM books
    WHERE isbn = book_isbn;

    IF available_copies IS NULL THEN
        RAISE EXCEPTION 'Book with ISBN % does not exist.', book_isbn;
    ELSIF available_copies = 0 THEN
        RAISE EXCEPTION 'No available copies for book with ISBN %.', book_isbn;
    END IF;


    INSERT INTO borrow_records (sid, isbn, borrow_date, due_date)
    VALUES (student_id, book_isbn, borrow_date, due_date);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE return_book(
    record_id INTEGER,
    return_date DATE
) AS
$$
BEGIN
    UPDATE borrow_records
    SET return_date = return_date
    WHERE id = record_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE reserve_seat(
    student_id VARCHAR,
    room_id INTEGER,
    seat_id INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP
) AS
$$
BEGIN
    INSERT INTO reservation_records (sid, room_id, seat_id, start_time, end_time)
    VALUES (student_id, room_id, seat_id, start_time, end_time);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE add_new_book(
    book_isbn VARCHAR,
    book_name VARCHAR,
    add_copies INTEGER,
    description TEXT,
    publish_date DATE
) AS
$$
DECLARE
    existing_copies INTEGER;
BEGIN

    SELECT copies
    INTO existing_copies
    FROM books
    WHERE isbn = book_isbn;

    IF existing_copies IS NULL THEN

        INSERT INTO books (isbn, name, copies, available_copies, description, publish_date)
        VALUES (book_isbn, book_name, add_copies, add_copies, description, publish_date);
    ELSE

        UPDATE books
        SET copies           = copies + add_copies,
            available_copies = available_copies + add_copies
        WHERE isbn = book_isbn;
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE update_borrow_records_and_generate_violations() AS
$$
DECLARE
    record_id        INTEGER;
    student_id       VARCHAR;
    book_isbn        VARCHAR;
    due_date         DATE;
    violation_reason TEXT := 'Overdue return';
BEGIN

    FOR record_id, student_id, book_isbn, due_date IN
        SELECT id, sid, isbn, due_date
        FROM borrow_records
        WHERE return_date IS NULL
          AND due_date < CURRENT_DATE
        LOOP

            UPDATE borrow_records
            SET is_overdue = TRUE
            WHERE id = record_id;


            INSERT INTO borrow_violation_records (sid, record_id, violation_date, violation_reason)
            VALUES (student_id, record_id, CURRENT_DATE, violation_reason);

            UPDATE students
            SET violation_count = violation_count + 1
            WHERE id = student_id;
        END LOOP;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_available_seats_in_room(
    p_room_id INTEGER,
    p_start_time TIMESTAMP,
    p_end_time TIMESTAMP
)
    RETURNS TABLE
            (
                seat_id INTEGER
            )
AS
$$
BEGIN
    RETURN QUERY
        SELECT seat_id
        FROM seats
        WHERE room_id = p_room_id
          AND seat_id NOT IN (SELECT seat_id
                              FROM reservation_records
                              WHERE room_id = p_room_id
                                AND (p_start_time < end_time AND p_end_time > start_time));
END;
$$ LANGUAGE plpgsql;
