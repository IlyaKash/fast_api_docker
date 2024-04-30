import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_session
from sqlalchemy import create_engine, text, insert, select
from config import settings


ur_s=settings.POSTGRES_DATABASE_URLS
ur_a=settings.POSTGRES_DATABASE_URLA


engine_s=create_engine(ur_s, echo=True)
engine_a=create_async_engine(ur_a, echo=True)

