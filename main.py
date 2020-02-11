from flask import Flask, escape, request
from flask_api import status
from flask_cors import CORS
from pynput.keyboard import Key,Controller
import time
import sys

app = Flask(__name__)
CORS(app) #di default CORS *

@app.route('/text',methods=['POST'])
def new_text():
    app.logger.debug(request.json['text'])
    keyboard = Controller()
    toSay = '{}'.format(request.json['text'].lower().strip()) 
    app.logger.debug(toSay)
    keyboard.type(toSay)
    return '',status.HTTP_200_OK
    