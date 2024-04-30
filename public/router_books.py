from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import JSONResponse, Response
from starlette import status
from models.good import *
from sqlalchemy.orm import sessionmaker, Session
from public.db import engine_s, engine_a
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async_session = sessionmaker(
    engine_a, class_=AsyncSession, expire_on_commit=False
)

async def get_async_session():
    async with async_session() as session:
        try:
            yield session
        finally:
            session.close()

books_router=APIRouter(tags=[Tags.books], prefix='/api/books')

@books_router.get('/{book_id}', response_model=Union[New_Respons, Book_constraint], tags=[Tags.books])
async def get_book_(book_id: int, DB: AsyncSession=Depends(get_async_session)):
    '''Получение книги по id'''
    book=await DB.execute(select(Book).where(Book.book_id==book_id))
    book=book.scalars().first()
    if book is None:
        return New_Respons(message='ошибка Книга не найдена')
    else:
        return book
@books_router.get("/", response_model=Union[list[Book_constraint], New_Respons], tags=[Tags.books])
async def get_books(DB: AsyncSession=Depends(get_async_session)):
    '''Все книги таблицы'''
    books=await DB.execute(select(Book).order_by(Book.book_id.desc()))
    #DB.query(Author).all()
    books=books.scalars().all()
    if books is None:
        return JSONResponse(status_code=404, content={'message': 'Книги не найдены'})
    else:
        return books

@books_router.post('/', response_model=Union[ New_Respons, Book_constraint], tags=[Tags.books], status_code=status.HTTP_201_CREATED)
async def create_book(item: Annotated[Book_constraint, Body(embed=True, description='Новая книга')], DB: AsyncSession=Depends(get_async_session)):
    '''Создает книгу, проверяет есть ли такой id автора в базе, если нет выводит, что такого автора в базе нет'''
    try:
        book=Book(title=item.title, publication_year=int(item.publication_year), author_id=item.author_id)
        if book is None:
            return New_Respons(message='ошибка в post объект не определен')
            #raise HTTPException(status_code=404, detail='Объект не определен')
        set_authors_id=await DB.execute(select(Author).where(Author.author_id==item.author_id))
        set_authors_id=set_authors_id.scalars().first()
        if not set_authors_id:
            return New_Respons(message='Такого автора в базе нет')
        DB.add(book)
        await DB.commit()
        await DB.refresh(book)
        return book
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Произошла ошибка при добавление объекта {book}')


@books_router.put('/', response_model=Union[Book_constraint, New_Respons], tags=[Tags.books])
async def edit_user_(item: Annotated[Book_constraint, Body(embed=True, description='Изменяем данные книги по id')], DB: AsyncSession=Depends(get_async_session)):
    book = await DB.execute(select(Book).where(Book.book_id == item.book_id))
    book=book.scalars().first()
    if book is None:
        return JSONResponse(status_code=404, content={'message': "Книга не найдена"})
    book.title=item.title
    book.publication_year=item.publication_year
    set_authors_id = await DB.execute(select(Author).where(Author.author_id == item.author_id))
    set_authors_id = set_authors_id.scalars().first()
    if not set_authors_id:
        return New_Respons(message='Такого автора в базе нет')
    book.author_id=item.author_id
    try:
        await DB.commit()
        await DB.refresh(book)
    except HTTPException:
        return JSONResponse(status_code=404, content={'message': "Ошибка в put"})
    return book

@books_router.delete('/{id}',response_model=Union[Book_constraint, New_Respons], tags=[Tags.books])
async def delete_book(book_id: int, DB: AsyncSession=Depends(get_async_session)):
    '''Удаление книги'''
    book = await DB.execute(select(Book).where(Book.book_id == book_id))
    book = book.scalars().first()
    if book is None:
        return JSONResponse(status_code=404, content={'message': 'Автор не найден'})
    try:
        await DB.delete(book)
        await DB.commit()
    except HTTPException:
        JSONResponse(content={'message': 'Ошибка'})
    return JSONResponse(content={'message': f'Книга {id} удален'})

