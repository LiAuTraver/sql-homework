import typing
import psycopg2
import logging
import psycopg2.pool
import psycopg2.sql
import orm


class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.db_params = {
            "dbname": "bkmgr",
            "user": "",
            "password": "",
            "host": Exception("set the url, you idiot!"),
            "port": "Exception('set the port, you idiot!')",
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

    def add_book(self, book: orm.Book) -> bool:
        conn = self.pool.getconn() # type: ignore
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
            self.pool.putconn(conn) # type: ignore

    def delete_book(self, isbn: str) -> bool:
        conn = self.pool.getconn() # type: ignore
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
            self.pool.putconn(conn) # type: ignore

    def get_book_by_isbn(self, isbn: str):
        conn = self.pool.getconn() # type: ignore
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM books WHERE isbn = %s", (isbn,))
                result = cur.fetchone()
                if result:
                    return orm.Book(
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
            self.pool.putconn(conn) # type: ignore

    def update_book(self, new_book) -> bool:
        conn = self.pool.getconn() # type: ignore
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
            conn.rollback()
            return False
        finally:
            self.pool.putconn(conn) # type: ignore

    def search_books(self, keyword: str) -> typing.List[orm.Book]:
        logging.info(f"Searching for books with keyword: {keyword}")
        conn = self.pool.getconn() # type: ignore
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
                    orm.Book(
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
            self.pool.putconn(conn) # type: ignore

if __name__ == '__main__':
    raise Exception("don't execute me, you idiot!")
else:
    print("Well done!")

