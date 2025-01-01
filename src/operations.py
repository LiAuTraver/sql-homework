import asyncio
import datetime
import typing
import asyncpg

from src import orm


async def fetch_students(conn: asyncpg.connection) -> typing.List[orm.Student]:
    records = await conn.fetch("SELECT * FROM students")
    students = [orm.Student(**record) for record in records]
    return students

async def fetch_books(conn: asyncpg.connection) -> typing.List[orm.Book]:
    records = await conn.fetch("SELECT * FROM books")
    books = [orm.Book(**record) for record in records]
    return books
# Utility function to execute SQL queries
async def execute_query(conn, query, *args):
    try:
        await conn.execute(query, *args)
        print(f"Query executed successfully: {query}")
    except Exception as e:
        print(f"Error executing query: {query}\nError: {e}")

# Insert functions
async def insert_students(conn):
    query = """
    INSERT INTO students (id, name, gender, violation_count)
    VALUES ($1, $2, $3, $4)
    """
    students = [
        ("S001", "Alice", "Female", 0),
        ("S002", "Bob", "Male", 2),
        ("S003", "Charlie", "Other", 1),
    ]
    for student in students:
        await execute_query(conn, query, *student)

async def insert_books(conn):
    query = """
    INSERT INTO books (isbn, name, copies, available_copies, description, publish_date)
    VALUES ($1, $2, $3, $4, $5, $6)
    """
    books = [
        ("B001", "The Great Gatsby", 10, 8, "A classic novel.", datetime.date(1925, 4, 10)),
        ("B002", "1984", 15, 15, "Dystopian fiction.", datetime.date(1949, 6, 8)),
        ("B003", "To Kill a Mockingbird", 12, 12, "A novel about racial injustice.", datetime.date(1960, 7, 11)),
    ]
    for book in books:
        await execute_query(conn, query, *book)

async def insert_rooms(conn):
    query = """
    INSERT INTO rooms (id, name, location)
    VALUES ($1, $2, $3)
    """
    rooms = [
        (1, "Study Room A", "First Floor"),
        (2, "Study Room B", "Second Floor"),
        (3, "Study Room C", "Third Floor"),
    ]
    for room in rooms:
        await execute_query(conn, query, *room)

async def insert_seats(conn):
    query = """
    INSERT INTO seats (room_id, seat_id)
    VALUES ($1, $2)
    """
    seats = [
        (1, 1),
        (1, 2),
        (2, 1),
        (2, 2),
        (3, 1),
    ]
    for seat in seats:
        await execute_query(conn, query, *seat)

async def insert_borrow_records(conn):
    query = """
    INSERT INTO borrow_records (sid, isbn, borrow_date, return_date, due_date, is_overdue)
    VALUES ($1, $2, $3, $4, $5, $6)
    """
    borrow_records = [
        ("S001", "B001", datetime.date(2024, 1, 1), None, datetime.date(2024, 1, 15), False),
        ("S002", "B002", datetime.date(2024, 1, 2), datetime.date(2024, 1, 16), datetime.date(2024, 1, 16), False),
        ("S003", "B003", datetime.date(2024, 1, 3), None, datetime.date(2024, 1, 17), True),
    ]
    for record in borrow_records:
        await execute_query(conn, query, *record)

if __name__ == '__main__':
    async def main():
        """
        insert some sample data into the database
        :return: None
        """
        conn = await asyncpg.connect(**orm.db_params)
        try:
            print("Inserting sample data...")
            await insert_students(conn)
            await insert_books(conn)
            await insert_rooms(conn)
            await insert_seats(conn)
            await insert_borrow_records(conn)
            print("Sample data inserted successfully.")
        finally:
            await conn.close()

    asyncio.run(main())
    pass
