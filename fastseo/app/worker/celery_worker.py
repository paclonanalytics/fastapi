from time import sleep
from typing import List
from celery import current_task

from .celery_app import celery_app

from .client import RestClient # клиент API Dataforseo

from .config import Config

seoclient = RestClient(Config.DATAFORSEO_LOGIN, Config.DATAFORSEO_PASSWORD)

@celery_app.task(acks_late=True)
def searhvolume_celery(items):
    # Перебираем список ключей и отправляем их 
    for row_start in range(0, len(items["keywords"]), 700):
        end_row = row_start + 700
        keys_list = items["keywords"][row_start:end_row]# формирую список из 700 ключей
        # Формирую запрос для отправки
        post_data = dict()
        post_data[len(post_data)] = dict(
            location_name=items["country_name"],
            language_name=items["language_name"],
            keywords=keys_list,
            pingback_url="https://fastseo.paclonanalytics.com/pingback?id=$id&tag=$tag"
        )
        response = seoclient.post("/v3/keywords_data/google/search_volume/task_post", post_data)
        if response["status_code"] == 20000:
            print('Отправлено ключей {}'.format(len(keys_list)))
        else:
            print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))
        
        keys_list = []
        
    return f"Task: searhvolume_celery - {response}"


@celery_app.task(acks_late=True)
def test_celery(word: str):
    for i in range(1, 11):
        current_task.update_state(state='PROGRESS',
                                  meta={'process_percent': i*10})
    return f"Task: test_celery return {word}"


