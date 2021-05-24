#-*- coding: utf-8 -*-
import requests
import time
import hashlib
import base64
import json
import websocket
import datetime
import hmac
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os,sys
import pyaudio
import wave
import rec



URL = "http://openapi.xfyun.cn/v2/aiui"
APPID = "5face08b"
API_KEY = "f17f89ebb39d57be688e54200b7fed88"
APISecret='a0be6d078406862212401a7df9eb9e41'
AUE = "raw"
AUTH_ID = "2aff08b7ac792f78ebd0b2d1a77bb434"
#AUTH_ID = "2894c985bf8b1111c6728db79d3479ae"
DATA_TYPE = "audio"  
SAMPLE_RATE = "16000"
SCENE = "main_box"
RESULT_LEVEL = "plain"
LAT = "39.938838"
LNG = "116.368624"
#个性化参数，需转义
PERS_PARAM = "{\\\"auth_id\\\":\\\"2aff08b7ac792f78ebd0b2d1a77bb434\\\"}"
#FILE_PATH = "/home/wangzj/WORK/yuyin/xunfei/luyin/voice/test_tianqi.pcm"



def buildHeader():
    curTime = str(int(time.time()))
    param = "{\"result_level\":\""+RESULT_LEVEL+"\",\"auth_id\":\""+AUTH_ID+"\",\"data_type\":\""+DATA_TYPE+"\",\"sample_rate\":\""+SAMPLE_RATE+"\",\"scene\":\""+SCENE+"\",\"lat\":\""+LAT+"\",\"lng\":\""+LNG+"\"}"
    #使用个性化参数时参数格式如下：
    #param = "{\"result_level\":\""+RESULT_LEVEL+"\",\"auth_id\":\""+AUTH_ID+"\",\"data_type\":\""+DATA_TYPE+"\",\"sample_rate\":\""+SAMPLE_RATE+"\",\"scene\":\""+SCENE+"\",\"lat\":\""+LAT+"\",\"lng\":\""+LNG+"\",\"pers_param\":\""+PERS_PARAM+"\"}"
    paramBase64 = base64.b64encode(param.encode())

    m2 = hashlib.md5()
    m2.update((API_KEY + curTime + paramBase64.decode()).encode("utf8"))
    checkSum = m2.hexdigest()

    header = {
        'X-CurTime': curTime,
        'X-Param': paramBase64,
        'X-Appid': APPID,
        'X-CheckSum': checkSum,
    }
    return header

def readFile(filePath):
    binfile = open(filePath, 'rb')
    data = binfile.read()
    return data
    
def nlp(FILE_PATH):
    r = requests.post(URL, headers=buildHeader(), data=readFile(FILE_PATH))
    resu = json.loads(r.content)
    yuyin = resu["data"][0]["text"]
    print('\033[31m我说：%s' %yuyin) #语音识别
    #print(resu['data'][1]['intent']['answer']['text']) #程序回答
    #print("小氢同学说: " + resu['data'][1]['intent']['answer']['text'])
    return(resu)

#########################################  tts

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.Text = Text

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"aue": "lame", "sfl":1, "auf": "audio/L16;rate=16000", "vcn": "xiaoyan", "tte": "utf8", "ttp":"cssml"}
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}
        #lame：mp3 (当aue:lame时需传参sfl:1)
        #使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        #self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")}

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
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
        message =json.loads(message)
        code = message["code"]
        sid = message["sid"]
        audio = message["data"]["audio"]
        audio = base64.b64decode(audio)
        status = message["data"]["status"]
        #print(message)
        if status == 2:
            #print("ws is closed")
            ws.close()
        if code != 0:
            errMsg = message["message"]
            #print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
        else:

            with open('./audio.mp3', 'ab') as f:
                f.write(audio)

    except Exception as e:
        print("receive msg,but parse exception:", e)



# 收到websocket错误的处理
def on_error(ws, error):
    print()
#    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws):
    print()
#    print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    def run(*args):
        d = {"common": wsParam.CommonArgs,
             "business": wsParam.BusinessArgs,
             "data": wsParam.Data,
             }
        d = json.dumps(d)
        #print("------>开始发送文本数据")
        ws.send(d)
        if os.path.exists('./audio.mp3'):
            os.remove('./audio.mp3')

    thread.start_new_thread(run, ())
   

#############################################
def play():
    os.system('sox audio.mp3 audio.wav')
    wf = wave.open('audio.wav', 'rb')
    p = pyaudio.PyAudio()

    def callback(in_data, frame_count, time_info, status):
        data = wf.readframes(frame_count)
        return (data, pyaudio.paContinue)

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    stream_callback=callback)

    stream.start_stream()
    while stream.is_active():
        time.sleep(0.1)

    stream.stop_stream()
    stream.close()
    wf.close()
    p.terminate()

if __name__ == "__main__":
    os.close(sys.stderr.fileno())
    while(True):
        #os.close(sys.stderr.fileno())
        rec.recording('record.mp3')
        os.system("ffmpeg -y  -i %s  -acodec pcm_s16le -f s16le  %s -loglevel quiet"%("record.mp3","record.pcm"))
        res = nlp("record.pcm")
        resp = res['data'][1]['intent']['answer']['text']
        resp2 = res['data'][1]['intent']['answer']['text']+'<break time=\"1000ms\"/>'
        wsParam = Ws_Param(APPID= '5face08b', APISecret= 'a0be6d078406862212401a7df9eb9e41',APIKey='26effe53e4f69220e1e8d7e20ef11449',Text=resp2)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.on_open = on_open
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        print('\033[34m小氢同学说：%s'%resp)
        play()
        time.sleep(1)
	
	
	
