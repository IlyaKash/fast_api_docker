from fastapi import FastAPI
from fastapi.responses import FileResponse
from datetime import datetime
from public.router_authors import authors_router
from public.router_books import books_router
import uvicorn

app=FastAPI()


app.include_router(authors_router)
app.include_router(books_router)
@app.on_event ("startup")
def on_startup():
    open('log_p.txt', mode='a').write(f'{datetime.utcnow()}: Begin\n')

@app.on_event('shutdown')
def shutdown():
    open('log_p.txt', mode='a').write(f"{datetime.utcnow()}: End\n")

@app.get('/')
def main():
    return FileResponse('files/index.html')
