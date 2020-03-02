from flask import Flask, escape, request, session
from flask_api import status
from flask_cors import CORS
from pynput.keyboard import Key,Controller
import time
import sys
import spacy
import it_core_news_sm
from collections import deque #è una coda iterabile che può fare anche da stack. Di default append() opera left-to-right. sul get devo prendere il rightmost [-1]
from model import enums
from model.layer import Layer
from model.enums import LayerMsg

app = Flask(__name__)
CORS(app) #di default CORS *
nlp = it_core_news_sm.load()
keyboard = Controller()

#app state
stack = deque()
curBurst = ""
lastAction = enums.Action.NESSUNA
prevLayerTriggerWords = [] #per ogni token controlla che quel token non appartenga a queste parole, se no vuol dire che il top layer deve terminare e l'n-1 layer deve passare di stato

def manageLayerAnswer(layerAnswer):
    """
    Punto nel quale si svolgono effettivamente le azioni comunicando anche con texstudio
    """
    print('Il server ha ricevuto {}'.format(layerAnswer))
    if layerAnswer[0] == LayerMsg.WAIT:
        pass
    elif layerAnswer[0] == LayerMsg.TEXT:
        pass
    elif layerAnswer[0] == LayerMsg.END_THIS_LAYER:
        pass
    elif layerAnswer[0] == LayerMsg.END_THIS_LAYER_WITH_TEXT:
        pass

@app.route('/mathtext',methods=['POST'])
def new_text():
    last_burst = request.json['text']
    if len(stack) == 0:
        stack.append(Layer())
    doc = nlp(last_burst)
    for idx,token in enumerate(doc):
        if token.text in prevLayerTriggerWords: #se questo token fa sì di triggerare il layer precedente
            pass
            #rimuovere layer in cima e inoltare quel comando al nuovo top layer (che poi è il precedente)
        else:
            res = stack[-1].handleRawText((token.text,token.pos_),idx)
            manageLayerAnswer(res)
    return '',status.HTTP_200_OK



    