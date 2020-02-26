from flask import Flask, escape, request, session
from flask_api import status
from flask_cors import CORS
from pynput.keyboard import Key,Controller
import time
import sys
import notificationcenter
import spacy
import it_core_news_sm
from queue import LifoQueue
from math_modules import basic_symbols, algebra, analysis, trigonometry
from model import enums


#codice eseguito all'inizio
app = Flask(__name__)
app.secret_key = "1dhsjhjsdkbsjahsj"
CORS(app) #di default CORS *
nlp = it_core_news_sm.load()
keyboard = Controller()
#app state
stack = LifoQueue()
curBurst = ""
lastAction = enums.Action.NESSUNA


@app.route('/mathtext',methods=['POST'])
def new_text():
    last_burst = request.json['text']
    math_module = basic_symbols.Per()
    doc = nlp(last_burst)
    toSay = '{}'.format(request.json['text'].lower().strip()) 
    app.logger.debug(toSay)
    keyboard.type(toSay)
    return '',status.HTTP_200_OK
    