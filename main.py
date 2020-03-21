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
import json
import pdb #debug

app = Flask(__name__)
CORS(app) #di default CORS *
nlp = it_core_news_sm.load()
keyboard = Controller()
with open('./util/word2num.json') as word2num_json:
    word2numDict = json.load(word2num_json)

#app state
stack = deque()
curBurst = {'tokens':[]} #il burst attuale sottoforma di array di token
lastAction = {'action':Action.NESSUNA} #si riferisce alle azioni fatte nei confronti di texstudio. uso dict se non l'informazione non viene persistita tra richieste successive
prevLayerTriggerWords = {'words':[]} #per ogni token controlla che quel token non appartenga a queste parole, se no vuol dire che il top layer deve terminare e l'n-1 layer deve passare di stato
moduleAskingNewLayer = {'module_name':None} #per sapere a che grammatica reindirizzare il testo quando il top layer ha finito
ruleAskingNewLayer = {'rulename':None} #servirà al modulo per sapere come muovere il cursore di conseguenza. Da rispedire indietro quando il top layer ha finito
lastTextSent = {'text':''} #tiene conto dell'ultimo testo inviato a texstudio
numBurstTokens = {'length':-1}

layer = Layer()

def manageLayerAnswer(layerAnswer):
    """
    Punto nel quale si svolgono effettivamente le azioni comunicando anche con texstudio
    """
    print('Il server ha ricevuto {}'.format(layerAnswer))
    if layerAnswer[0] == LayerMsg.WAIT:
        pass

    elif layerAnswer[0] == LayerMsg.TEXT:
        txtToSend = layerAnswer[1] if layerAnswer[1] != None else ""
        keyboard.type(txtToSend)
        app.logger.debug('txt for texstudio: {}'.format(txtToSend))
        """Aggiornamento stato"""
        lastTextSent['text'] = txtToSend
        lastAction['action'] = Action.DETTATURA

    elif layerAnswer[0] == LayerMsg.END_THIS_LAYER:
        print('finishing layer without text')
        # allTextSentByTopLayer = stack[-1].allTextSent #prendo tutto quanto detto nel top-layer
        # pdb.set_trace()
        if len(stack) > 0: #se quello che ho appena tolto non era l'unico layer
            res = layer.updateGrammarStringFormat("",stack[-1]['grammarName'],stack[-1]['ruleName'])
            eventualCursorMovement = res[0] #dato che è un end layer mi interessa solo di chiuderlo muovendo il cursore xkè comunque una end rule non ci sarà
            # pdb.set_trace()
            if eventualCursorMovement is not None and eventualCursorMovement != 0:
                if eventualCursorMovement > 0:
                    keyboard.type('__mf{}'.format(eventualCursorMovement))
                else:
                    keyboard.type('__mb{}'.format(eventualCursorMovement))
        # """Aggiornamento stato"""
        stack.pop() #fine layer
        # resetPrevLayerStatusVars()

    elif layerAnswer[0] == LayerMsg.END_THIS_LAYER_WITH_TEXT:
        pass
        # if isinstance(layerAnswer[1],dict): #vuol dire che c'è parte del burst che ha prodotto una foglia, mentre il resto è da mandare dentro \text{}. A seguito di un esplicito comando 'fine'
        #     txtToSend = layerAnswer[1]['tag']
        #     lastGoodIdx = layerAnswer[1]['idx']
        #     freeText = '\\text{{{0}}}'.format(curBurst['tokens'][lastGoodIdx:])
        #     keyboard.type(txtToSend)
        #     app.logger.debug('txt for texstudio: {}'.format(txtToSend))
        #     keyboard.type(freeText)
        #     app.logger.debug('txt for texstudio as plain text: {}'.format(freeText))
        #     """Aggiornamento stato"""
        #     lastTextSent['text'] = freeText
        #     lastAction['action'] = Action.DETTATURA
        # else: #il messaggio di fine layer arriva con un testo semplice come payload
        #     txtToSend = layerAnswer[1]
        #     keyboard.type(txtToSend)
        #     app.logger.debug('txt for texstudio: {}'.format(txtToSend))
        #     """Aggiornamento stato"""
        #     lastTextSent['text'] = txtToSend
        #     lastAction['action'] = Action.DETTATURA
        # allTextSentByTopLayer = stack[-1].allTextSent #prendo tutto quanto detto nel top-layer
        # stack.pop() #fine layer
        # if len(stack) > 0: #se quello che ho appena tolto non era l'unico layer
        #     eventualCursorMovement = stack[-1].updateGrammarStringFormat(allTextSentByTopLayer,moduleAskingNewLayer['module_name'],ruleAskingNewLayer['rulename'])
        #     if eventualCursorMovement is not None and eventualCursorMovement != 0:
        #         if eventualCursorMovement > 0:
        #             keyboard.type('__mf{}'.format(eventualCursorMovement))
        #         else:
        #             keyboard.type('__mb{}'.format(eventualCursorMovement))
        # """Aggiornamento stato"""
        # resetPrevLayerStatusVars()

    elif layerAnswer[0] == LayerMsg.NEW_LAYER_REQUEST:
        # pdb.set_trace()
        prevLayerTriggerWords['words'] = layerAnswer[1] #aggiorno le parole per risollevare il layer che sto portando in secondo posto
        moduleAskingNewLayer['module_name'] = layerAnswer[2]  
        ruleAskingNewLayer['rulename'] = layerAnswer[3] 
        stack.append({'ruleName':ruleAskingNewLayer['rulename'],'grammarName':moduleAskingNewLayer['module_name'],'triggerWords':prevLayerTriggerWords['words']})
        cursorOffset = int(layerAnswer[4])
        # pdb.set_trace()
        tag = layerAnswer[5] #cosa scrivere prima di spostare il cursore
        carryHomeLength = layerAnswer[6] #se != None indica che devo muovere il cursore indietro di una certa quantità prima di applicare cursorOffset
        if tag is not None:
            keyboard.type(tag)
            keyboard.type('__mb{}'.format(len(tag))) #RITORNO A INIZIO COMANDO (perchè l'offset lo do rispetto a quello)
        else:
            if carryHomeLength is not None:
                carryHomeLength = int(carryHomeLength)
                if carryHomeLength > 0:
                    keyboard.type('__mb{}'.format(carryHomeLength))
                else:
                    keyboard.type('__mf{}'.format(carryHomeLength))
        # pdb.set_trace()
        if cursorOffset != 0: #può essere anche negativo se devo tornare indietro
            if cursorOffset > 0:
                #dico a texstudio di andare avanti col cursore
                keyboard.type('__mf{}'.format(cursorOffset))
            else: #strettamente minore di 0
                #dico a texstudio di andare indietro col cursore
                keyboard.type('__mb{}'.format(cursorOffset))
        # stack.append(Layer())
        """Aggiornamento stato"""
        lastTextSent['text'] = tag if tag != None else lastTextSent['text']
        lastAction['action'] = Action.DETTATURA
    elif layerAnswer[0] == LayerMsg.REWIND: #il layer sta chiedendo al srv di risomministrargli il burst partendo da un certo punto
        #faccio da server dall'index indicato fino a dove è arrivato al momento il burst. Poi faccio riprendere normalmente il server
        # pdb.set_trace()
        keyboard.type(layerAnswer[2]) #[2] è il tag della farthes leaf
        idx_start = layerAnswer[1]
        for i in range(idx_start,len(curBurst['tokens'])): #non vado oltre dove sono già arrivato
            # newLayerIfNeeded()
            res = layer.handleRawText((curBurst['tokens'][i],'NA'),i,numBurstTokens['length'])
            time.sleep(2) #per debug. Per darmi tempo di switchare su texstudio
            manageLayerAnswer(res)


"""SERVER INTERFACE API"""

@app.route('/mathtext',methods=['POST'])
def new_text():
    last_burst = request.json['text']
    curBurst['tokens'] = []
    doc = nlp(last_burst)
    numBurstTokens['length'] = len(doc)

    # newLayerIfNeeded()
    
    for idx,token in enumerate(doc):
        tokenText = ''
        tokenPos = ''
        if token.text in word2numDict.keys():
            tokenText = word2numDict[token.text]
            tokenPos = 'NUM'
        else:
            tokenText = token.text
            tokenPos = token.pos_

        print('layer count: {}'.format(len(stack)))

        curBurst['tokens'].append(tokenText)
        # pdb.set_trace()
        
        if len(stack)>0:
            print('MAIN: prev layer trigger WORDS {}'.format(stack[-1]['triggerWords']))
            if tokenText in stack[-1]['triggerWords']: #se questo token fa sì di triggerare il layer precedente.          
                # pdb.set_trace()
                res = layer.updateGrammarStringFormat("",stack[-1]['grammarName'],stack[-1]['ruleName'])
                eventualCursorMovement = res[0]
                nextRule = res[1]
                # pdb.set_trace()
                if nextRule[0] != LayerMsg.NEW_LAYER_REQUEST: #altrimenti lo spostamento lo gestisco già in manageLayerAnswer
                    if eventualCursorMovement is not None and eventualCursorMovement != 0:
                        if eventualCursorMovement > 0:
                            time.sleep(1)
                            keyboard.type('__mf{}'.format(eventualCursorMovement))
                        else:
                            time.sleep(1)
                            keyboard.type('__mb{}'.format(eventualCursorMovement)) 
                stack.pop()
                manageLayerAnswer(nextRule)
            else:
                res = layer.handleRawText((tokenText,tokenPos),idx,numBurstTokens['length'])
                time.sleep(2) #per debug. Per darmi tempo di switchare su texstudio
                manageLayerAnswer(res)
        else:
            # else: #questo token mi fa restare su questo layer
            # newLayerIfNeeded()
            res = layer.handleRawText((tokenText,tokenPos),idx,numBurstTokens['length'])
            time.sleep(2) #per debug. Per darmi tempo di switchare su texstudio
            manageLayerAnswer(res)
    return '',status.HTTP_200_OK

"""UTILITY METHODS"""
    

def resetPrevLayerStatusVars():
    prevLayerTriggerWords['words'] = []
    ruleAskingNewLayer['rulename'] = None
    moduleAskingNewLayer['module_name'] = None



    