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
from model.enums import Action
import pdb #debug

app = Flask(__name__)
CORS(app) #di default CORS *
nlp = it_core_news_sm.load()
keyboard = Controller()

#app state
stack = deque()
curBurst = [] #il burst attuale sottoforma di array di token
lastAction = {'action':Action.NESSUNA} #si riferisce alle azioni fatte nei confronti di texstudio. uso dict se non l'informazione non viene persistita tra richieste successive
prevLayerTriggerWords = {'words':[]} #per ogni token controlla che quel token non appartenga a queste parole, se no vuol dire che il top layer deve terminare e l'n-1 layer deve passare di stato
moduleAskingNewLayer = {'module_name':None} #per sapere a che grammatica reindirizzare il testo quando il top layer ha finito
ruleAskingNewLayer = {'rulename':None} #servirà al modulo per sapere come muovere il cursore di conseguenza. Da rispedire indietro quando il top layer ha finito
lastTextSent = {'text':''} #tiene conto dell'ultimo testo inviato a texstudio

def manageLayerAnswer(layerAnswer):
    """
    Punto nel quale si svolgono effettivamente le azioni comunicando anche con texstudio
    """
    print('Il server ha ricevuto {}'.format(layerAnswer))
    if layerAnswer[0] == LayerMsg.WAIT:
        pass

    elif layerAnswer[0] == LayerMsg.TEXT:
        txtToSend = layerAnswer[1]
        keyboard.type(txtToSend)
        app.logger.debug('txt for texstudio: {}'.format(txtToSend))
        """Aggiornamento stato"""
        lastTextSent['text'] = txtToSend
        lastAction['action'] = Action.DETTATURA

    elif layerAnswer[0] == LayerMsg.END_THIS_LAYER:
        print('finishing layer without text')
        allTextSentByTopLayer = stack[-1].allTextSent #prendo tutto quanto detto nel top-layer
        stack.pop() #fine layer
        if len(stack) > 0: #se quello che ho appena tolto non era l'unico layer
            eventualCursorMovement = stack[-1].updateGrammarStringFormat(allTextSentByTopLayer,moduleAskingNewLayer['module_name'],ruleAskingNewLayer['rulename'])
            # pdb.set_trace()
            if eventualCursorMovement is not None and eventualCursorMovement != 0:
                if eventualCursorMovement > 0:
                    keyboard.type('__mf{}'.format(eventualCursorMovement))
                else:
                    keyboard.type('__mb{}'.format(eventualCursorMovement))
        """Aggiornamento stato"""
        resetPrevLayerStatusVars()

    elif layerAnswer[0] == LayerMsg.END_THIS_LAYER_WITH_TEXT:
        if isinstance(layerAnswer[1],dict): #vuol dire che c'è parte del burst che ha prodotto una foglia, mentre il resto è da mandare dentro \text{}. A seguito di un esplicito comando 'fine'
            txtToSend = layerAnswer[1]['tag']
            lastGoodIdx = layerAnswer[1]['idx']
            freeText = '\\text{{{0}}}'.format(curBurst[lastGoodIdx:])
            keyboard.type(txtToSend)
            app.logger.debug('txt for texstudio: {}'.format(txtToSend))
            keyboard.type(freeText)
            app.logger.debug('txt for texstudio as plain text: {}'.format(freeText))
            """Aggiornamento stato"""
            lastTextSent['text'] = freeText
            lastAction['action'] = Action.DETTATURA
        else: #il messaggio di fine layer arriva con un testo semplice come payload
            txtToSend = layerAnswer[1]
            keyboard.type(txtToSend)
            app.logger.debug('txt for texstudio: {}'.format(txtToSend))
            """Aggiornamento stato"""
            lastTextSent['text'] = txtToSend
            lastAction['action'] = Action.DETTATURA
        allTextSentByTopLayer = stack[-1].allTextSent #prendo tutto quanto detto nel top-layer
        stack.pop() #fine layer
        if len(stack) > 0: #se quello che ho appena tolto non era l'unico layer
            eventualCursorMovement = stack[-1].updateGrammarStringFormat(allTextSentByTopLayer,moduleAskingNewLayer['module_name'],ruleAskingNewLayer['rulename'])
            if eventualCursorMovement is not None and eventualCursorMovement != 0:
                if eventualCursorMovement > 0:
                    keyboard.type('__mf{}'.format(eventualCursorMovement))
                else:
                    keyboard.type('__mb{}'.format(eventualCursorMovement))
        """Aggiornamento stato"""
        resetPrevLayerStatusVars()

    elif layerAnswer[0] == LayerMsg.NEW_LAYER_REQUEST:
        prevLayerTriggerWords['words'] = layerAnswer[1] #aggiorno le parole per risollevare il layer che sto portando in secondo posto
        moduleAskingNewLayer['module_name'] = layerAnswer[2]  
        ruleAskingNewLayer['rulename'] = layerAnswer[3] 
        cursorOffset = int(layerAnswer[4])
        # pdb.set_trace()
        tag = layerAnswer[5] #cosa scrivere prima di spostare il cursore
        keyboard.type(tag)
        keyboard.type('__mb{}'.format(len(tag))) #RITORNO A INIZIO COMANDO (perchè l'offset lo do rispetto a quello)
        if cursorOffset != 0: #può essere anche negativo se devo tornare indietro
            if cursorOffset > 0:
                #dico a texstudio di andare avanti col cursore
                keyboard.type('__mf{}'.format(cursorOffset))
            else: #strettamente minore di 0
                #dico a texstudio di andare indietro col cursore
                keyboard.type('__mb{}'.format(cursorOffset))
        stack.append(Layer())
        """Aggiornamento stato"""
        lastTextSent['text'] = tag if tag != None else lastTextSent['text']
        lastAction['action'] = Action.DETTATURA

"""SERVER INTERFACE API"""

@app.route('/mathtext',methods=['POST'])
def new_text():
    last_burst = request.json['text']
    curBurst = []
    doc = nlp(last_burst)
    num_burst_tokens = len(doc)

    newLayerIfNeeded()
    
    for idx,token in enumerate(doc):
        curBurst.append(token.text)
        if token.text in prevLayerTriggerWords['words']: #se questo token fa sì di triggerare il layer precedente
            allTextSentByTopLayer = stack[-1].allTextSent #prendo tutto quanto detto nel top-layer
            stack.pop() #fine layer
            if len(stack) > 0: #se quello che ho appena tolto non era l'unico layer
                eventualCursorMovement = stack[-1].updateGrammarStringFormat(allTextSentByTopLayer,moduleAskingNewLayer['module_name'],ruleAskingNewLayer['rulename'])
                if eventualCursorMovement is not None and eventualCursorMovement != 0:
                    if eventualCursorMovement > 0:
                        keyboard.type('__mf{}'.format(eventualCursorMovement))
                    else:
                        keyboard.type('__mb{}'.format(eventualCursorMovement))
            """Aggiornamento stato"""
            resetPrevLayerStatusVars()

        else: #questo token mi fa restare su questo layer
            newLayerIfNeeded()
            res = stack[-1].handleRawText((token.text,token.pos_),idx,num_burst_tokens)
            time.sleep(2) #per debug. Per darmi tempo di switchare su texstudio
            manageLayerAnswer(res)
    return '',status.HTTP_200_OK

"""UTILITY METHODS"""

def newLayerIfNeeded():
    """Crea un nuovo layer se lo stack è vuoto"""
    if len(stack) == 0:
        stack.append(Layer())

def resetPrevLayerStatusVars():
    prevLayerTriggerWords['words'] = []
    ruleAskingNewLayer['rulename'] = None
    moduleAskingNewLayer['module_name'] = None



    