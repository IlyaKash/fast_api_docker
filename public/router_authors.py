from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import JSONResponse, Response
from starlette import status
from models.good import *
from sqlalchemy.orm import sessionmaker, Session
from public.db import engine_s, engine_a
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

#session_make=sessionmaker(engine_s)
async_session = sessionmaker(
    engine_a, class_=AsyncSession, expire_on_commit=False
)
# async def init_models():
#     async with engine_a.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#заменить на асинхронный
def get_session():
    with Session(engine_s) as session:
        try:
            yield session
        finally:
            session.close()
async def get_async_session():
    async with async_session() as session:
        try:
            yield session
        finally:
            session.close()

#конкретизация роутера
authors_router=APIRouter(tags=[Tags.authors], prefix='/api/authors')
info_router=APIRouter(tags=[Tags.info])


@authors_router.get('/{author_id}', response_model=Union[New_Respons, Author_constraint], tags=[Tags.authors])
async def get_author_(author_id: int, DB: AsyncSession=Depends(get_async_session)):
    '''Получение автора по id'''
    author=await DB.execute(select(Author).where(Author.author_id==author_id))
    author=author.scalars().first()
    if author is None:
        return New_Respons(message='ошибка Автор не найден')
    else:
        return author
@authors_router.get("/", response_model=Union[list[Author_constraint], New_Respons], tags=[Tags.authors])
async def get_authors(DB: AsyncSession=Depends(get_async_session)):
    '''Все авторы таблицы'''
    authors=await DB.execute(select(Author).order_by(Author.author_id.desc()))
    #DB.query(Author).all()
    authors=authors.scalars().all()
    if authors is None:
        return JSONResponse(status_code=404, content={'message': 'Авторы не найдены'})
    else:
        return authors

@authors_router.post('/', response_model=Union[ New_Respons, Author_constraint], tags=[Tags.authors], status_code=status.HTTP_201_CREATED)
async def create_author(item: Annotated[Author_constraint, Body(embed=True, description='Новый автор')], DB: AsyncSession=Depends(get_async_session)):
    try:
        author=Author(name=item.name, birth_year=int(item.birth_year))
        if author is None:
            return New_Respons(message='ошибка в post объект не определен')
            #raise HTTPException(status_code=404, detail='Объект не определен')
        DB.add(author)
        await DB.commit()
        await DB.refresh(author)
        return author
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Произошла ошибка при добавление объекта {author}')


@authors_router.put('/', response_model=Union[Author_constraint, New_Respons], tags=[Tags.authors])
async def edit_user_(item: Annotated[Author_constraint, Body(embed=True, description='Изменяем данные автора по id')], DB: AsyncSession=Depends(get_async_session)):
    author = await DB.execute(select(Author).where(Author.author_id == item.author_id))
    author=author.scalars().first()
    if author is None:
        return JSONResponse(status_code=404, content={'message': "Автор не найден"})
    author.name=item.name
    author.birth_year=item.birth_year
    try:
        await DB.commit()
        await DB.refresh(author)
    except HTTPException:
        return JSONResponse(status_code=404, content={'message': ""})
    return author

@authors_router.delete('/{id}',response_model=Union[Author_constraint, New_Respons], tags=[Tags.authors])
async def delete_author(author_id: int, DB: AsyncSession=Depends(get_async_session)):
    '''Удаляет автора, и все книги к которым он привязан по ключю'''
    author = await DB.execute(select(Author).where(Author.author_id == author_id))
    author = author.scalars().first()
    if author is None:
        return JSONResponse(status_code=404, content={'message': 'Автор не найден'})
    try:
        books=await DB.execute(select(Book).where(author.author_id==Book.author_id))
        books=books.scalars().all()
        for book in books:
            await DB.delete(book)
        await DB.commit()
        await DB.delete(author)
        await DB.commit()
    except HTTPException:
        JSONResponse(content={'message': 'Ошибка'})
    return JSONResponse(content={'message': f'Автор {id} удален'})

#patch
@authors_router.patch('/{author_id}', response_model=Union[Author_constraint, New_Respons], tags=[Tags.authors])
async def edit_author(item: Annotated[Author_constraint,
Body(embed=True, description='Изменяем данные по id')], response: Response, DB: AsyncSession=Depends(get_async_session)):
    '''Находим автора, делаем словарь из данных на входе, посылаем в метод update, обновляем данные'''
    try:
        author = await DB.execute(select(Author).where(Author.author_id == item.author_id))
        author = author.scalars().first()
        if author is None:
            return New_Respons(message='ошибка в patch автор не найден')
        update_author_dict=item.model_dump(exclude_defaults=True)
        print(update_author_dict)
        #author_copy=author.model_copy(update=update_author_dict)
        author.update(**update_author_dict)
        await DB.commit()
        await DB.refresh(author)
        return author
    except HTTPException:
        return New_Respons(message=f'Ошибка в patch')