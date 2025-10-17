import datetime
import requests
import json
import time

API_KEY = "dYk7FJNWjhBegwj1JkmHH04i"
SECRET_KEY = "Gf5tOO8FlsYVbDO5z6eR5FhCLLeygMDb"
CUID = 'mnuMhndv9ACcbye1cuSxae0pjS8r8tpp'


def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


def tts_baidu(text, mp3_path='./baidu_test.mp3', voice=0, speed=5, how='short'):
    if how == 'short':
        return tts_baidu_short(text, mp3_path, voice, speed)
    elif how == 'long':
        return tts_baidu_long(text, mp3_path, voice, speed)
    else:
        return Exception('Invalid How')


def tts_baidu_short(text, mp3_path='./baidu_test.mp3', voice=0, speed=5):
    now = datetime.datetime.now()
    res_url = f'https://tsn.baidu.com/text2audio?tex={text}&tok={get_access_token()}&cuid={CUID}&ctp=1&lan=zh&spd={speed}&pit=5&vol=0&per={voice}&aue=3'
    doc = requests.get(res_url)
    with open(mp3_path, 'wb') as f:
        f.write(doc.content)
    time_cost = (datetime.datetime.now() - now).total_seconds()
    return time_cost


def tts_baidu_long(text, mp3_path='./baidu_test.mp3', voice=0, speed=5):
    task_id = tts_baidu_long_create(text, voice, speed)
    now = datetime.datetime.now()
    fini = False
    while not fini:
        try:
            task_url = tts_baidu_long_query(task_id)
            doc = requests.get(task_url)
            with open(mp3_path, 'wb') as f:
                f.write(doc.content)
            time_cost = (datetime.datetime.now() - now).total_seconds()
            return time_cost
        except:
            time.sleep(0.2)
            pass


def tts_baidu_long_create(text, voice=0, speed=5):
    # 基础音库：度小宇=1，度小美=0，度逍遥（基础）=3，度丫丫=4，精品音库：度逍遥（精品）=5003，度小鹿=5118，度博文=106，度小童=110，度小萌=111，度米朵=103，度小娇=5

    url_create = "https://aip.baidubce.com/rpc/2.0/tts/v1/create?access_token=" + get_access_token()
    payload = json.dumps({
        "text": text,
        "format": "mp3-16k",
        "voice": voice,
        "lang": "zh",
        "speed": speed,
        "pitch": 5,
        "volume": 5,
        "enable_subtitle": 0
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url_create, headers=headers, data=payload)
    return json.loads(response._content)['task_id']


def tts_baidu_long_query(task_id):
    url_query = "https://aip.baidubce.com/rpc/2.0/tts/v1/query?access_token=" + get_access_token()
    payload = json.dumps({
        "task_ids": [task_id]
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url_query, headers=headers, data=payload)
    res_url = json.loads(response._content)['tasks_info'][0]['task_result']['speech_url']
    return res_url
