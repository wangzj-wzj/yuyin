#-*- coding: utf-8 -*-
import requests
import time
import hashlib
import base64

URL = "http://openapi.xfyun.cn/v2/aiui"
APPID = "5face08b"
API_KEY = "f17f89ebb39d57be688e54200b7fed88"
AUE = "raw"
AUTH_ID = "2894c985bf8b1111c6728db79d3479ae"
DATA_TYPE = "audio"
SAMPLE_RATE = "16000"
SCENE = "main"
RESULT_LEVEL = "complete"
LAT = "39.938838"
LNG = "116.368624"
#个性化参数，需转义
PERS_PARAM = "{\\\"auth_id\\\":\\\"2894c985bf8b1111c6728db79d3479ae\\\"}"
FILE_PATH = "/home/wangzj/WORK/yuyin/xunfei/luyin/voice/test_tianqi.pcm"


def buildHeader():
    curTime = str(int(time.time()))
    param = "{\"result_level\":\""+RESULT_LEVEL+"\",\"auth_id\":\""+AUTH_ID+"\",\"data_type\":\""+DATA_TYPE+"\",\"sample_rate\":\""+SAMPLE_RATE+"\",\"scene\":\""+SCENE+"\",\"lat\":\""+LAT+"\",\"lng\":\""+LNG+"\"}"
    #使用个性化参数时参数格式如下：
    #param = "{\"result_level\":\""+RESULT_LEVEL+"\",\"auth_id\":\""+AUTH_ID+"\",\"data_type\":\""+DATA_TYPE+"\",\"sample_rate\":\""+SAMPLE_RATE+"\",\"scene\":\""+SCENE+"\",\"lat\":\""+LAT+"\",\"lng\":\""+LNG+"\",\"pers_param\":\""+PERS_PARAM+"\"}"
    paramBase64 = base64.b64encode(param.encode('utf-8'))

    m2 = hashlib.md5()
    m2.update(API_KEY + curTime + str(paramBase64).encode('utf-8'))
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

r = requests.post(URL, headers=buildHeader(), data=readFile(FILE_PATH))
print(r.content)
