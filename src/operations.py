import psycopg2
import psycopg2.pool
import logging
from typing import Optional, List
from orm import Book
from datetime import datetime


class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.db_params = {
            'dbname': 'bkmgr',
            'user': 'postgres',
            'password': 'postgres',
            'host': 'psql.liautraver.dev',
            'port': '31001'
        }

    def connect(self):
        if self.pool:
            return
       
        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(
                1, 20, **self.db_params)
            # print("Database connected")
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
                cur.execute('''
                    INSERT INTO books (isbn, name, copies, available_copies, description, publish_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (book.isbn, book.name, book.copies, book.available_copies, book.description, book.publish_date))
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
                cur.execute('DELETE FROM books WHERE isbn = %s', (isbn,))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error deleting book: {e}")
            conn.rollback()
            return False
        finally:
            self.pool.putconn(conn)

    def update_book(self, book: Book) -> bool:
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('''
                    UPDATE books 
                    SET name = %s, copies = %s, available_copies = %s,
                        description = %s, publish_date = %s
                    WHERE isbn = %s
                ''', (book.name, book.copies, book.available_copies, book.description, book.publish_date, book.isbn))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error updating book: {e}")
            conn.rollback()
            return False
        finally:
            self.pool.putconn(conn)

    def search_books(self, keyword: str) -> List[Book]:
        print("keyword:",keyword)
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT * FROM books 
                    WHERE name ILIKE %s OR description ILIKE %s
                ''', (f'%{keyword}%', f'%{keyword}%'))
                bks = [Book(
                    isbn=r[0],
                    name=r[1],
                    copies=r[2],
                    available_copies=r[3],
                    description=r[4],
                    publish_date=r[5]
                ) for r in cur.fetchall()]
                for bk in bks:
                    print(bk)
                return bks
        except Exception as e:
            logging.error(f"Error searching books: {e}")
            return []
        finally:
            self.pool.putconn(conn)


def test():
    print("1")
    db = DatabaseManager()
    db.connect()
    db.search_books('')
    db.close()


if __name__ == '__main__':
    test()
