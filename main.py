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
from model import enums
from model.enums import NotificationName
from model.layer import Layer

#notification cbks
def onTextToSendToTexstudio(sender,notification_name,txtToSend):
    print("received {}".format(txtToSend))
    app.logger.debug('to texstudio: '+txtToSend)
    keyboard.type(txtToSend)

def onEndTopLayer(sender,notification_name,info):
    """info se contiene del testo, questo dev'essere redirezionato a texstudio perchè significa che il layer ha ricevuto solo riposte da tutte foglie
    e quindi è automatico che debba finire dopo questo inoltro (perchè non c'è più nessuna grammatica che può essere attivata)"""
    print("end top layer command")
    if info is not None:
        pass
    stack.get() #rimuovo top layer dalla pila

def onNewLayerRequest(sender,notification_name,info):
    print("new layer request")
    stack.put(Layer())
    


app = Flask(__name__)
CORS(app) #di default CORS *
nlp = it_core_news_sm.load()
keyboard = Controller()
#notifiche
notificationCenter = NotificationCenter()
observer_layers = notificationCenter.add_observer(with_block=onTextToSendToTexstudio, for_name=NotificationName.TXT_FOR_TEXSTUDIO_FOR_SRV.name)
observer_end_layer = notificationCenter.add_observer(with_block=onEndTopLayer,for_name=NotificationName.END_LAYER.name)
observer_layer_request = notificationCenter.add_observer(with_block=onNewLayerRequest,for_name=NotificationName.NEW_LAYER_REQUEST.name)
#app state
stack = LifoQueue()
curBurst = ""
lastAction = enums.Action.NESSUNA



@app.route('/mathtext',methods=['POST'])
def new_text():
    last_burst = request.json['text']
    if stack.empty():
        stack.put(Layer())
    doc = nlp(last_burst)
    for token in doc:
        notificationCenter.post_notification(sender=None,with_name=NotificationName.NEW_INPUT.name,with_info=(token.text,token.pos_))
    return '',status.HTTP_200_OK
    