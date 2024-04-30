from typing import Union, Annotated, Optional, List
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, Sequence, Identity
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from enum import Enum

Base=declarative_base()


class User(Base):
    __tablename__='users'
    id=Column(Integer, Identity(start=10), primary_key=True)
    name=Column(String, index=True, nullable=False)
    hashed_password=Column(String)

#третья практическая
class Author(Base):
    __tablename__='authors'
    author_id=Column(Integer, Identity(start=0), primary_key=True)
    name=Column(String, index=True, nullable=False)
    birth_year=Column(Integer)
    #связь один ко многим
    #books :Mapped[List['Book']] = relationship()
    def update(self, **new_data):
        for field, value in new_data.items():
            print("!!!!!!!!!!!!!!!!!!!!",field, value)
            setattr(self, field, value)

class Book(Base):
    __tablename__ = 'books'
    book_id=Column(Integer, Identity(start=0), primary_key=True)
    title=Column(String, index=True, nullable=False)
    publication_year=Column(Integer)
    #внешний ключ для связи с таблицей Author
    author_id : Mapped[int] = mapped_column(ForeignKey('authors.author_id'))





class Author_constraint(BaseModel):
    author_id: Annotated[Union[int, None], Field(default=1, ge=0, lt=200)] = None
    name: Union[str, None] = 'string'
    birth_year: Union[int, None]= 0


class Book_constraint(BaseModel):
    book_id : Annotated[Union[int, None], Field(default=1, ge=0, lt=200)] = None
    title : Union[str, None] = 'string'
    publication_year: Union[int, None] = 0
    author_id : Union[int, None] = 0


class Tags(Enum):
    authors='author'
    users='users'
    advents='advents'
    info='info'
    good='good'
    books='book'


class New_Respons(BaseModel):
    message: str



