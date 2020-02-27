from flask import Flask, escape, request, session
from flask_api import status
from flask_cors import CORS
from pynput.keyboard import Key,Controller
import time
import sys
from notificationcenter import *
import spacy
import it_core_news_sm
from queue import LifoQueue
from math_modules import basic_symbols, algebra, analysis, trigonometry
from model import enums

#notification cbks
def onTextToSendToTexstudio(sender,notification_name,txtToSend):
    print("received {}".format(txtToSend))
    app.logger.debug(txtToSend)
    time.sleep(3)
    keyboard.type(txtToSend)

app = Flask(__name__)
# app.secret_key = "1dhsjhjsdkbsjahsj" # se volessi usare le sessioni....
CORS(app) #di default CORS *
nlp = it_core_news_sm.load()
keyboard = Controller()
notificationCenter = NotificationCenter()
observer_layers = notificationCenter.add_observer(with_block=onTextToSendToTexstudio, for_name="txt4texstudio")
#app state
stack = LifoQueue()
curBurst = ""
lastAction = enums.Action.NESSUNA



@app.route('/mathtext',methods=['POST'])
def new_text():
    last_burst = request.json['text']
    math_module = basic_symbols.Per()
    doc = nlp(last_burst)
    for token in doc:
        notificationCenter.post_notification(sender=None,with_name="new_input",with_info=token.text)
    return '',status.HTTP_200_OK
    