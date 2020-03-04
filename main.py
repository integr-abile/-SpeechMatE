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
curBurst = [] #il burst attuale sottoforma di array di token
lastAction = enums.Action.NESSUNA
prevLayerTriggerWords = [] #per ogni token controlla che quel token non appartenga a queste parole, se no vuol dire che il top layer deve terminare e l'n-1 layer deve passare di stato
lastTextSent = "" #tiene conto dell'ultimo testo inviato a texstudio e sulla base di questo valuta se fare replace o scrivere di seguito

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
        if isinstance(layerAnswer[1],dict): #vuol dire che c'è parte del burst che ha prodotto una foglia, mentre il resto è da mandare dentro \text{}. A seguito di un esplicito comando 'fine'
            txtToSend = layerAnswer[1]['tag']
            lastGoodIdx = layerAnswer[1]['idx']
            freeText = '\\text{{{0}}}'.format(curBurst[lastGoodIdx:])
            if isReplaceNeeded(txtToSend):
                keyboard.type('__rpl{}&'.format(txtToSend))
                app.logger.debug('txt for texstudio: {}'.format('__rpl{}&'.format(txtToSend)))
            else:
                keyboard.type(txtToSend)
                app.logger.debug('txt for texstudio: {}'.format(txtToSend))
            keyboard.type(freeText)
            app.logger.debug('txt for texstudio as plain text: {}'.format(freeText))
        else: #il messaggio di fine layer arriva con un testo semplice come payload
            txtToSend = layerAnswer[1]
            if isReplaceNeeded(txtToSend):
                keyboard.type('__rpl{}&'.format(txtToSend))
                app.logger.debug('txt for texstudio: {}'.format('__rpl{}&'.format(txtToSend)))
            else:
                keyboard.type(txtToSend)
                app.logger.debug('txt for texstudio: {}'.format(txtToSend))

def isReplaceNeeded(newText):
    """
    Considerando anche l'ultimo testo inviato a texstudio, valuta se il nuovo testo arrivato è assimilabile ad una specificazione del precedente
    o a un nuovo comando/testo
    """
    if newText == "":
        return True
    if newText[0] == '\\': #è un comando latex
        end = newText.find('{') #cerco il testo tra \ e la prima {
        if end == -1:
            end = len(newText) #se il comando latex non contiene una graffa considero tutto il comando finora dato
        cmdName = newText[:end]
        if cmdName == lastTextSent: #è lo stesso comando
            if len(newText) > len(lastTextSent):
                return True
            else: #è un altro comando che però è dello stesso tipo del precedente, ma essendo più corto sicuramente viene da una regola grammaticale che prima era già stata metchata
                return False
        else: #se è arrivato un altro comando rispetto al precedente
            return False
    else:
        return False


"""SERVER INTERFACE PART"""

@app.route('/mathtext',methods=['POST'])
def new_text():
    last_burst = request.json['text']
    if len(stack) == 0:
        stack.append(Layer())
    doc = nlp(last_burst)
    for idx,token in enumerate(doc):
        curBurst.append(token.text)
        if token.text in prevLayerTriggerWords: #se questo token fa sì di triggerare il layer precedente
            pass
            #rimuovere layer in cima e inoltare quel comando al nuovo top layer (che poi è il precedente)
        else:
            res = stack[-1].handleRawText((token.text,token.pos_),idx)
            time.sleep(3) #per debug. Per darmi tempo di switchare su texstudio
            manageLayerAnswer(res)
    return '',status.HTTP_200_OK



    