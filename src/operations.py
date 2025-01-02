import psycopg2
import logging
from typing import List

import psycopg2.pool
import psycopg2.sql
from orm import Book


class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.db_params = {
            "dbname": "bkmgr",
            "user": "postgres",
            "password": "postgres",
            "host": "psql.liautraver.dev",
            "port": "31001",
        }

    def connect(self):
        if self.pool:
            return

        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(1, 20, **self.db_params)
            print("Database connected")
            logging.info("Database connection pool created successfully")
        except Exception as e:
            logging.error(f"Failed to create connection pool: {e}")
            raise

    def close(self):
        if self.pool:
            self.pool.closeall()
            print("DataBase closed successfully")

    def add_book(self, book: Book) -> bool:
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """CALL add_new_book(
                        %s::VARCHAR,           -- book_isbn
                        %s::VARCHAR,           -- book_name
                        %s::INTEGER,           -- add_copies
                        %s::TEXT,             -- description
                        %s::DATE              -- publish_date
                    )
                """,
                    (
                        book.isbn,
                        book.name,
                        book.copies,
                        book.description,
                        book.publish_date,
                    ),
                )
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error adding book: {e}")
            conn.rollback()
            return False
        finally:
            self.pool.putconn(conn)

    def delete_book(self, isbn: str) -> bool:
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM books WHERE isbn = %s", (isbn,))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error deleting book: {e}")
            conn.rollback()
            return False
        finally:
            self.pool.putconn(conn)

    def get_book_by_isbn(self, isbn: str):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM books WHERE isbn = %s", (isbn,))
                result = cur.fetchone()
                if result:
                    return Book(
                        isbn=result[0],
                        name=result[1],
                        copies=result[2],
                        available_copies=result[3],
                        description=result[4],
                        publish_date=result[5],
                    )
                return None
        except Exception as e:
            logging.error(f"Error fetching book: {e}")
            return None
        finally:
            self.pool.putconn(conn)

    def update_book(self, new_book) -> bool:
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE books 
                    SET name = %s,  description = %s, publish_date = %s
                    WHERE isbn = %s
                """,
                    (
                        new_book.name,
                        new_book.description,
                        new_book.publish_date,
                        new_book.isbn,
                    ),
                )
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error updating book: {e}")
            # print("Error updating book: ", e)
            conn.rollback()
            return False
        finally:
            self.pool.putconn(conn)

    def search_books(self, keyword: str) -> List[Book]:
        # print("keyword:", keyword)
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM books 
                    WHERE name ILIKE %s OR description ILIKE %s
                """,
                    (f"%{keyword}%", f"%{keyword}%"),
                )
                bks = [
                    Book(
                        isbn=r[0],
                        name=r[1],
                        copies=r[2],
                        available_copies=r[3],
                        description=r[4],
                        publish_date=r[5],
                    )
                    for r in cur.fetchall()
                ]
                # for bk in bks:
                #     print(bk)
                return bks
        except Exception as e:
            logging.error(f"Error searching books: {e}")
            return []
        finally:
            self.pool.putconn(conn)


# def test():
#     print("1")
#     db = DatabaseManager()
#     db.connect()

#     # bks = db.search_books('')
#     # for bk in bks:
#     #     print(bk)

#     # isbn = '978-3-16-148410-0'

#     # bk = db.get_book_by_isbn(isbn)

#     # edited_bk = Book(
#     #     isbn='978-3-16-148410-0',
#     #     name='The Testbook',
#     #     copies=10,
#     #     available_copies=10,
#     #     description='A novel tested by zxs',
#     #     publish_date=datetime(2025, 1, 2)
#     # )

#     # db.update_book(isbn, edited_bk.name, edited_bk.copies,
#     #                edited_bk.description, edited_bk.publish_date)

#     print("After adding book")

#     bks = db.search_books('')
#     for bk in bks:
#         print(bk)
#     db.close()


# if __name__ == '__main__':
#     test()
