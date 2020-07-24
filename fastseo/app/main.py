import sys
import re

from fastapi import FastAPI, BackgroundTasks
from fastapi.encoders import jsonable_encoder

from typing import List, Optional

from app.schemas import Searhvolume
from app.worker.celery_app import celery_app

from celery.result import AsyncResult

from .config import Config


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Когда запросы собрались. Отправляет ID таски отдельноей задачей 
@app.get("/ping/task")
async def pingback(background_task: BackgroundTasks, id: Optional[str] = None, tag: Optional[str] = None):
    """
    ### Адрес на который возвращается идентификатор задачи из API
    """
    task = celery_app.send_task(
        "worker.celery_worker.searhvolume_get_celery", args=[{"id":id, "tag": tag}])
    background_task.add_task(background_on_message, task)
    return {"id": id, "tag:":tag}


@app.get("/ch/cratedatabase/{database_name}")
def create_clickhouse_database():
    """
    ### Создать таблицу keywords_volume в Кликхаус
    """
    if database_name == None:
        database_name = 'seodata'
    from clickhouse_driver import Client
    ch = Client(host='clickhouse')
    ch.execute(f'CREATE DATABASE IF NOT EXISTS {database_name}') # создаст базу данных если ее не существует
    ch = Client(host='clickhouse', database=f'{database_name}')
    # Если таблицы нет то создаем
    ch.execute("""
        CREATE TABLE IF NOT EXISTS seodata.keywords_volume
        (
            `ext_taskid` String,
            `se` String,
            `location_name` String,
            `language_name` String,
            `keyword` String,
            `competition` Float64,
            `cpc` Float64,
            `year` UInt64,
            `month` UInt64,
            `search_volume` UInt64,
            `date` Date,
            `create_date` DateTime
        ) 
        ENGINE = MergeTree() 
        PARTITION BY toYYYYMM(date) 
        ORDER BY (date) 
        SETTINGS index_granularity=8192
               """)
    
    print(ch.execute('SHOW TABLES'))
    return {}

# Сообщения о ходе выполнения
def celery_on_message(body):
    if body.get('status') == 'PROGRESS':
        res = body.get('result')
        sys.stdout.write(f"\n Статус по задаче: {res.get('process_percent')}%")
        sys.stdout.flush()
    elif body.get('status') == 'SUCCESS':
        print("\n Задача выполнена SUCCESS")
        print(body)
    elif body.get('status') == 'STARTED':
        print("\n Задача выполнена STARTED")
        print(body)
    else:
        print("\n Задача выполнена Else")
        print(body)

def background_on_message(task):
    print(task.get(on_message=celery_on_message, propagate=False))
    

@app.get('/get_result_task/{id}')
async def get_result_task(id):
    """
    ### Запросить статус по задаче по внутреннему идентификатору
    """
    task = AsyncResult(id=id, app=celery_app)
    if task.successful():
        return {'res':task.get()}


@app.post("/seoapi/keywordsvolume")
async def searhvolume(item: Searhvolume, background_task: BackgroundTasks):
    """
    ### Создать задачу на проверку частности ключевых слов

    #### Принимает параметры
    - **ext_taskid**: Внешний идентификатор задачи для поиска в базе ClickHouse
    - **date**: текущая дата
    - **country_name**: страна в которой снимаем частотность
    - **language_name**: язык для которого снимаем частотность ключей
    - **keywords**: список ключевых слов ['apple', 'microsoft']
    
    #### Возвращает параметры
    - **messag** - сообщение об успешной или не успешной отправке
    - **task_id** - внешний идентификатор по которому потом ищем в кликхаус
    - **inner_task_id** - внутренний идентификатор таски
    - **count_keys** - кол-во ключевых слов на проверку
    - **country_name** - страна
    - **language_name** - язык
    """
    item = jsonable_encoder(item)
    status = "success"
    ext_taskid = item["ext_taskid"] #Идентификтор по которому получаем датку
    
    #очищаем ключи от символов пробелов вначале и конце строки, от знаков табуляции и двйных пробелов
    clear_keys = []
    for key in item['keywords']:
        key = re.sub(r'\s+', ' ', key) # убираем двоные пробелы и специ символы
        key = key.strip() #убиарем пробелы вначале и конце строки
        if key.isspace() or key == "": #Состоит ли строка из неотображаемых символов
            continue
        elif key in clear_keys: # если такой ключ уже есть 
            continue
        else:
            clear_keys.append(key)
    if len(clear_keys) == 0:
        status = "faild"
    else:
        item['keywords'] = clear_keys
        task = celery_app.send_task(
            "worker.celery_worker.searhvolume_celery", args=[item])
        background_task.add_task(background_on_message, task)
    return {'message': status, 
            "task_id": ext_taskid, 
            "inner_task_id": task,
            "count_keys": len(clear_keys),
            "country_name": item['country_name'], 
            "language_name": item['language_name']}


