import dataclasses
import datetime
import os
import typing

db_params: dict[str, str] = {
    "database": "bkmgr",
    "user": "",
    "password": "",
    "host": os.getenv('DB_HOST' , 'localhost'),
    "port": "31001"
}


@dataclasses.dataclass
class Student:
    id: str
    name: str
    gender: typing.Optional[str]
    violation_count: int = 0


@dataclasses.dataclass
class Book:
    isbn: str
    name: str
    copies: int
    available_copies: int
    description: typing.Optional[str]
    publish_date: typing.Optional[datetime.date]


@dataclasses.dataclass
class Room:
    id: int
    name: typing.Optional[str]
    location: str


@dataclasses.dataclass
class Seat:
    room_id: int
    seat_id: int


@dataclasses.dataclass
class BorrowRecord:
    id: int
    sid: str
    isbn: str
    borrow_date: datetime.date
    return_date: typing.Optional[datetime.date]
    due_date: datetime.date
    is_overdue: bool = False


@dataclasses.dataclass
class ReservationRecord:
    id: int
    sid: str
    room_id: int
    seat_id: typing.Optional[int]
    start_time: datetime.datetime
    end_time: datetime.datetime


@dataclasses.dataclass
class BorrowViolationRecord:
    sid: str
    record_id: int
    violation_date: datetime.date
    violation_reason: typing.Optional[str]


@dataclasses.dataclass
class ReservationViolationRecord:
    sid: str
    record_id: int
    violation_date: datetime.date
    violation_reason: typing.Optional[str]


@dataclasses.dataclass
class Author:
    isni: str
    name: str
    desc: typing.Optional[str]
    birth_date: typing.Optional[datetime.date]
    death_date: typing.Optional[datetime.date]


@dataclasses.dataclass
class BookGenre:
    genres: str  # Matches the `bk_genres` ENUM
    isbn: str


@dataclasses.dataclass
class Genre:
    genres: str  # Matches the `bk_genres` ENUM


@dataclasses.dataclass
class BookAuthor:
    isni: str
    isbn: str
