# -*- coding:utf-8 -*-
#
#   author: iflytek
#
#  本demo测试时运行的环境为：Windows + Python3.7
#  本demo测试成功运行时所安装的第三方库及其版本如下：
#   cffi==1.12.3
#   gevent==1.4.0
#   greenlet==0.4.15
#   pycparser==2.19
#   six==1.12.0
#   websocket==0.2.1
#   websocket-client==0.56.0
#   合成小语种需要传输小语种文本、使用小语种发音人vcn、tte=unicode以及修改文本编码方式
#  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import datetime
import hashlib
import base64
import hmac
import json
import ssl
import websocket
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
from time import mktime
import _thread as thread
import os


APPID = 'b521e83e'
APISecret = 'NjYwNzMzOGM4ZDZkY2JkNzhlYWU3ZTgy'
APIKey = '840e23ea367d8c07e8e838a82acfe302'

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


def tts_iflytek(text, mp3_path='./iflytest_test.mp3', voice='xiaoyan', speed=60):
    now = datetime.datetime.now()
    websocket.enableTrace(False)
    wsUrl = create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_close=on_close)
    ws.on_open = on_open
    ws.text = text
    ws.voice = voice
    ws.speed = speed
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    time_cost = (datetime.datetime.now() - now).total_seconds()
    return time_cost


def create_url():
    url = 'wss://tts-api.xfyun.cn/v2/tts'
    # 生成RFC1123格式的时间戳
    now = datetime.datetime.now()
    date = format_date_time(mktime(now.timetuple()))

    # 拼接字符串
    signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
    signature_origin += "date: " + date + "\n"
    signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
    # 进行hmac-sha256进行加密
    signature_sha = hmac.new(APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        APIKey, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    # 将请求的鉴权参数组合为字典
    v = {
        "authorization": authorization,
        "date": date,
        "host": "ws-api.xfyun.cn"
    }
    # 拼接鉴权参数，生成url
    url = url + '?' + urlencode(v)
    # print("date: ",date)
    # print("v: ",v)
    # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
    # print('websocket url :', url)
    return url


def on_message(ws, message):
    try:
        message = json.loads(message)
        code = message["code"]
        sid = message["sid"]
        audio = message["data"]["audio"]
        audio = base64.b64decode(audio)
        status = message["data"]["status"]
        if status == 2:
            # print("ws is closed")
            ws.close()
        if code != 0:
            errMsg = message["message"]
            print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
        else:
            with open(ws.mp3_path, 'ab') as f:
                f.write(audio)

    except Exception as e:
        print("receive msg,but parse exception:", e)


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws):
    print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    # print("Opened connection")
    def run():
        d = {
            "common": {
                "app_id": APPID
            },
            "business": {
                "aue": "lame",
                "sfl": 1,
                "auf": "audio/L16;rate=16000",
                "vcn": ws.voice,
                "tte": "utf8",
                "speed": ws.speed
            },
            "data": {
                "status": 2,
                "text": str(base64.b64encode(ws.text.encode('utf-8')), "UTF8")},
             }
        d = json.dumps(d)
        ws.send(d)
        if os.path.exists(ws.mp3_path):
            os.remove(ws.mp3_path)

    thread.start_new_thread(run, ())

