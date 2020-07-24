from time import sleep
from datetime import datetime
from typing import List
from celery import current_task

from .celery_app import celery_app
from config import Config
from worker.apiclient.client import RestClient
seoclient = RestClient(Config.DATAFORSEO_LOGIN, Config.DATAFORSEO_PASSWORD)


#Бьем по 700 ключей пачки и отправяем задачи
@celery_app.task(acks_late=True)
def searhvolume_celery(items):
    # Перебираем список ключей и отправляем их 
    for row_start in range(0, len(items["keywords"]), 700):
        end_row = row_start + 700
        keys_list = items["keywords"][row_start:end_row]# формирую список из 700 ключей
        post_data = dict()
        post_data[len(post_data)] = dict(
            location_name=items["country_name"],
            language_name=items["language_name"],
            keywords=keys_list,
            tag=items["ext_taskid"],
            pingback_url=f"https://{Config.DOMAIN}/ping/task?id=$id&tag=$tag"
        )
        response = seoclient.post(path="/v3/keywords_data/google/search_volume/task_post", data=post_data)
        print(response)
        if response["status_code"] == 20000:
            print('Отправлено ключей {}'.format(len(keys_list)))
        else:
            print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))
        
        keys_list = []
        
    return "Task: searhvolume_celery - {response}"
            

#Получив ID выполненной задачи, разбираем данные и загружаем их в кликхаус
@celery_app.task(acks_late=True)
def searhvolume_get_celery(items):
    task_id = items["id"]
    task_tag = items["tag"]
    response = seoclient.get("/v3/keywords_data/google/search_volume/task_get/" + task_id)

    api_result = response['tasks'][0]
    
    from datetime import datetime

    def flatter_keywords_volume(data):
        result= []
        ext_taskid = data['data']['tag']
        se = data['data']['se']
        location_name = data['data']['location_name']
        language_name = data['data']['language_name']
        create_date = datetime.now()
        for key in data['result']:
            competition=key['competition']
            cpc=key['cpc']
            keyword=key['keyword']
            for monthly_searches in key['monthly_searches']:
                date = datetime.strptime(str(monthly_searches['year'])+'-'+str(monthly_searches['month'])+'-1', '%Y-%m-%d').date()
                year = monthly_searches['year']
                month = monthly_searches['month']
                search_volume = monthly_searches['search_volume']
                result.append((ext_taskid, se, location_name, language_name, keyword, competition, cpc, year, month, search_volume, date, create_date))
                print(ext_taskid, se, location_name, language_name, keyword, competition, cpc, type(year), month, search_volume, date, create_date)
        return result
    
    api_result = flatter_keywords_volume(api_result)

    from clickhouse_driver import Client
    ch_client = Client(host='clickhouse')
    ch_client.execute(
        'INSERT INTO seodata.keywords_volume (ext_taskid, se, location_name, language_name, keyword, competition, cpc, year, month, search_volume, date, create_date) VALUES',
        api_result
    )
    return {"response": response, "api_result": api_result}





