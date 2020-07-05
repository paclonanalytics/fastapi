import sys

from fastapi import FastAPI, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from typing import List
from app.schemas import Searhvolume

from app.worker.celery_app import celery_app

from celery.result import AsyncResult




app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


def celery_on_message(body):
    if body.get('status') == 'PROGRESS':
        res = body.get('result')
        sys.stdout.write(f"\n Статус по задаче: {res.get('process_percent')}%")
        sys.stdout.flush()
    elif body.get('status') == 'SUCCESS':
        print("\n Задача выполнена SUCCESS")
        print(body)
    else:
        print("\n Задача выполнена Else")
        print(body)

def background_on_message(task):
    print(task.get(on_message=celery_on_message, propagate=False))
    

@app.get('/get_res/{id}')
async def get_res(id):
    task = AsyncResult(id=id, app=celery_app)
    if task.successful():
        return {'res':task.get()}


@app.post("/seoapi/keywordsvolume")
async def searhvolume(item: Searhvolume, background_task: BackgroundTasks):
    item = jsonable_encoder(item)
    task = celery_app.send_task(
        "worker.celery_worker.searhvolume_celery", args=[item])
    background_task.add_task(background_on_message, task)
    return {'message': "Ставим задачу"}




@app.get("/{word}")
async def root(word: str, background_task: BackgroundTasks):
    task = celery_app.send_task(
        "worker.celery_worker.test_celery", args=[word]) # отпправляем задачу в calary
    print(task)
    background_task.add_task(background_on_message, task)
    return {"message": "Word received"}
