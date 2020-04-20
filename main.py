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
from model.enums import LayerMsg,EditMsg,Action
from token_pre_processor import TokenPreProcessor
from edit_modules.edit_util import convertCommandsToTree,convertCorrspondencesToString
from edit_modules.edit_buffer import EditBuffer
import json
import re
import pdb #debug
import copy

app = Flask(__name__)
CORS(app) #di default CORS *
nlp = it_core_news_sm.load()
keyboard = Controller()


#app state for math
curBurst = {'tokens':[]} #il burst attuale sottoforma di array di token
lastAction = {'action':Action.NESSUNA} #si riferisce alle azioni fatte nei confronti di texstudio. uso dict se non l'informazione non viene persistita tra richieste successive
numBurstTokens = {'length':-1}
tokenPreProcessor = TokenPreProcessor()
layer = Layer() #non lo metto nello stato perchè da problemi di concorrenza. Mi gestisco il restore dello stato all'interno del layer stesso

#dobbiamo gestire il layer a parte dentro se stesso perchè la libreria copy non supporta
oldState = {'stack':None,
            'prevLayerTriggerWords':[], #per ogni token controlla che quel token non appartenga a queste parole, se no vuol dire che il top layer deve terminare e l'n-1 layer deve passare di stato
            'moduleAskingNewLayer':None, #per sapere a che grammatica reindirizzare il testo quando il top layer ha finito
            'ruleAskingNewLayer':None, #servirà al modulo per sapere come muovere il cursore di conseguenza. Da rispedire indietro quando il top layer ha finito
            'lastSentCommands':[]  #tiene conto delle ultime istruzioni inviate a texstudio dall'ultimo messaggio ricevuto          
            }
#dobbiamo gestire il layer a parte dentro se stesso perchè la libreria copy non supporta
curState = {'stack':deque(),
            'prevLayerTriggerWords':[],
            'moduleAskingNewLayer':None,
            'ruleAskingNewLayer':None,
            'lastSentCommands':[]            
            }


def restorePreviousState():#undo
    # pdb.set_trace()
    print('ripristino stato precedente....')
    curState = copy.deepcopy(oldState)
    #restore del layer
    wordsSinceLastLayerInit = layer.reset()
    # pdb.set_trace()
    for pastInfo in wordsSinceLastLayerInit[:-2]:
        res = layer.handleRawText(pastInfo[0],pastInfo[1],pastInfo[2])
        manageLayerAnswer(res,ignore_answers=True)






#app state for edit
with open('./edit_modules/json/commands.json') as commands_json:
    editGraph = convertCommandsToTree(json.load(commands_json))
editStateManager = EditBuffer(editGraph)

with open('./edit_modules/json/correspondences.json') as correspondences_json: #comandi e suoi inversi
    correspondencesDict = json.load(correspondences_json)

######################## MANAGE ANSWERS ############################################

def manageLayerAnswer(layerAnswer,ignore_answers=False):
    """
    Punto nel quale si svolgono effettivamente le azioni comunicando anche con texstudio
    """
    if ignore_answers == True:
        return
    
    print('Il server ha ricevuto {}'.format(layerAnswer))
    if layerAnswer[0] == LayerMsg.WAIT:
        pass

    elif layerAnswer[0] == LayerMsg.TEXT:
        
        curState['lastSentCommands'] = [] #reset
        txtToSend = layerAnswer[1] if layerAnswer[1] != None else ""
        keyboard.type(txtToSend)
        curState['lastSentCommands'].append(txtToSend)
        eventualEndCursorMovement = int(layerAnswer[2])
        if eventualEndCursorMovement != 0:
            if eventualEndCursorMovement > 0:
                pressSpaceTimes(eventualEndCursorMovement)
                curState['lastSentCommands'].append("avanti {}".format(eventualEndCursorMovement))
            else:
                muoviCursoreIndietroDi(abs(eventualEndCursorMovement))
                curState['lastSentCommands'].append("indietro {}".format(eventualEndCursorMovement))
        #update state
        app.logger.debug('txt for texstudio: {}'.format(txtToSend))

    elif layerAnswer[0] == LayerMsg.END_THIS_LAYER:
        print('finishing layer without text')

        if len(curState['stack']) > 0: #se quello che ho appena tolto non era l'unico layer
            res = layer.updateGrammarStringFormat("",curState['stack'][-1]['grammarName'],curState['stack'][-1]['ruleName'])
            eventualCursorMovement = res[0] #dato che è un end layer mi interessa solo di chiuderlo muovendo il cursore xkè comunque una end rule non ci sarà
            # pdb.set_trace()
            if eventualCursorMovement is not None and eventualCursorMovement != 0:
                if eventualCursorMovement > 0:
                    keyboard.type('__mf{}'.format(eventualCursorMovement))
                    curState['lastSentCommands'] = ["avanti {}".format(eventualCursorMovement)]
                else:
                    keyboard.type('__mb{}'.format(eventualCursorMovement))
                    curState['lastSentCommands'] = ["indietro {}".format(eventualCursorMovement)]
        curState['stack'].pop() #fine layer

    elif layerAnswer[0] == LayerMsg.END_THIS_LAYER_WITH_TEXT:
        pass

    elif layerAnswer[0] == LayerMsg.NEW_LAYER_REQUEST:
        
        curState['prevLayerTriggerWords'] = layerAnswer[1] #aggiorno le parole per risollevare il layer che sto portando in secondo posto
        curState['moduleAskingNewLayer'] = layerAnswer[2]  
        curState['ruleAskingNewLayer'] = layerAnswer[3] 
        curState['stack'].append({'ruleName':curState['ruleAskingNewLayer'],'grammarName':curState['moduleAskingNewLayer'],'triggerWords':curState['prevLayerTriggerWords']})
        cursorOffset = int(layerAnswer[4])
        curState['lastSentCommands'] = [] #reset state
        
        tag = layerAnswer[5] #cosa scrivere prima di spostare il cursore
        carryHomeLength = layerAnswer[6] #se != None indica che devo muovere il cursore indietro di una certa quantità prima di applicare cursorOffset
        if tag is not None:
            keyboard.type(tag)
            curState['lastSentCommands'].append(tag)
            muoviCursoreIndietroDi(len(tag)) #RITORNO A INIZIO COMANDO (perchè l'offset lo do rispetto a quello)
            curState['lastSentCommands'].append("indietro {}".format(len(tag)))
        else:
            if carryHomeLength is not None:
                carryHomeLength = int(carryHomeLength)
                if carryHomeLength > 0:
                    muoviCursoreIndietroDi(carryHomeLength)
                    curState['lastSentCommands'].append("indietro {}".format(carryHomeLength))
                else: #se carry home length è negativo
                    muoviCursoreAvantiDi(abs(carryHomeLength))
                    curState['lastSentCommands'].append("avanti {}".format(abs(carryHomeLength)))
        if cursorOffset > 0:
            #dico a texstudio di andare avanti col cursore
            muoviCursoreAvantiDi(cursorOffset)
            curState['lastSentCommands'].append("avanti {}".format(cursorOffset))
        else: #strettamente minore di 0
            #dico a texstudio di andare indietro col cursore
            muoviCursoreIndietroDi(abs(cursorOffset))
            curState['lastSentCommands'].append("indietro {}".format(abs(cursorOffset)))

    elif layerAnswer[0] == LayerMsg.REWIND: #il layer sta chiedendo al srv di risomministrargli il burst partendo da un certo punto
        #faccio da server dall'index indicato fino a dove è arrivato al momento il burst. Poi faccio riprendere normalmente il server
        curState['lastSentCommands'] = []
        keyboard.type(layerAnswer[2]) #[2] è il tag della farthes leaf
        eventualEndCursorMovement = int(layerAnswer[3])
        if eventualEndCursorMovement != 0:
            if eventualEndCursorMovement > 0:
                pressSpaceTimes(eventualEndCursorMovement)
                curState['lastSentCommands'].append("space {}".format(eventualCursorMovement))
            else:
                muoviCursoreIndietroDi(abs(eventualEndCursorMovement))
                curState['lastSentCommands'].append("indietro {}".format(abs(eventualCursorMovement)))
        # salvaTex()
        idx_start = layerAnswer[1]
        for i in range(idx_start,len(curBurst['tokens'])): #non vado oltre dove sono già arrivato
            res = layer.handleRawText((curBurst['tokens'][i],'NA'),i,numBurstTokens['length'])
            #time.sleep(2) #per debug. Per darmi tempo di switchare su texstudio
            manageLayerAnswer(res)
    elif layerAnswer[0] == EditMsg.COMMAND: #annulla o ripristina
        executeEditCommand(layerAnswer[1])


def manageEditAnswer(editAnswer,curToken,isLastToken):
    print('EDIT ricevuto {}'.format(editAnswer))
    if editAnswer[0] == EditMsg.RETRY:
        if editAnswer[1] != "":
            executeEditCommand(editAnswer[1])
        res = editStateManager.newToken(curToken,isLastToken)    
        manageEditAnswer(res,curToken,isLastToken)
    elif editAnswer[0] == EditMsg.NEXT_TOKEN:
        pass
    elif editAnswer[0] == EditMsg.WAIT:
        pass
    elif editAnswer[0] == EditMsg.COMMAND:
        executeEditCommand(editAnswer[1])


def executeEditCommand(cmdStr):
    time.sleep(2)
    print(cmdStr)
    #faccio passare tutti i comandi in commands.json e li gestisco in stile regex
    avanti_n_pattern = re.compile("avanti [0-9]+")
    indietro_n_pattern = re.compile("indietro [0-9]+")
    space_n_pattern = re.compile("space [0-9]+")
    backspace_n_pattern = re.compile("backspace [0-9]+")
    if avanti_n_pattern.match(cmdStr):
        numChar = cmdStr.split()[1]
        muoviCursoreAvantiDi(int(numChar))
    elif cmdStr == "avanti":
        muoviCursoreAvantiDi(1)
    elif indietro_n_pattern.match(cmdStr):
        numChar = cmdStr.split()[1]
        muoviCursoreIndietroDi(int(numChar))
    elif cmdStr == "indietro":
        muoviCursoreIndietroDi(1)
    elif cmdStr == "corrispondente":
        keyboard.type("__corr")
    elif cmdStr == "cancella":
        pressBackspace(1)
    elif space_n_pattern.match(cmdStr):
        numChar = cmdStr.split()[1]
        pressSpaceTimes(int(numChar))
    elif backspace_n_pattern.match(cmdStr):
        numChar = cmdStr.split()[1]
        pressBackspace(int(numChar))
    elif cmdStr == "annulla":
        inverseOrderLastCmds = list(reversed(curState['lastSentCommands']))
        inverseCmds = []
        for cmd in inverseOrderLastCmds:
            initialPartOfCmd = cmd.split()[0]
            if initialPartOfCmd in correspondencesDict.keys() and correspondencesDict[initialPartOfCmd] != None: #se esiste l'inverso
                explodedCmd = cmd.split()
                if len(explodedCmd) > 1:
                    inverseCmds.append('{} {}'.format(correspondencesDict[initialPartOfCmd],explodedCmd[1]))
                else:
                    inverseCmds.append(correspondencesDict[initialPartOfCmd])
            else: #non esiste l'inverso quindi devo cancellare parte di ciò che è scritto
                inverseCmds.append("backspace {}".format(len(initialPartOfCmd))) #iniziale e l'unica perchè è un testo latex
        if len(inverseCmds) > 0: #se ci sono testi da cancellare
            sendInverseCmds(inverseCmds)
            restorePreviousState()


def sendInverseCmds(inverseCmds):
    for inverseCmd in inverseCmds:
        executeEditCommand(inverseCmd)



############################################## SERVER INTERFACE #######################################
"""SERVER INTERFACE API"""

@app.route('/editText',methods=['POST'])
def new_edit_text():
    last_burst = request.json['text']
    #qua non è come la matematica. Finito il burst si resetta lo stato perchè assumo che un comando di editing venga detto tutto di un fiato
    burstTokens = last_burst.split()
    for idx,token in enumerate(burstTokens):
        res = editStateManager.newToken(token,idx==len(burstTokens)-1)
        manageEditAnswer(res,token,idx==len(burstTokens)-1)
    return '',status.HTTP_200_OK





@app.route('/mathtext',methods=['POST'])
def new_text():
    last_burst = request.json['text']
    curBurst['tokens'] = []
    doc = nlp(last_burst)
    expandedDoc = tokenPreProcessor.expandBurstIfNeeded(doc)
    numBurstTokens['length'] = len(expandedDoc)
    
    for idx,token in enumerate(expandedDoc):
        tokenText = token['token']
        tokenPos = token['pos']
        
        print('layer count: {}'.format(len(curState['stack'])))

        curBurst['tokens'].append(tokenText)
        # pdb.set_trace()
        #potremmo salvarlo direttamente qua tutto lo stato...
        if tokenText != "annulla":
            # pdb.set_trace()
            oldState = copy.deepcopy(curState)
        
        if len(curState['stack'])>0:
            print('MAIN: prev layer trigger WORDS {}'.format(curState['stack'][-1]['triggerWords']))
            if tokenText in curState['stack'][-1]['triggerWords']: #se questo token fa sì di triggerare il layer precedente.          
                # pdb.set_trace()
                res = layer.updateGrammarStringFormat("",curState['stack'][-1]['grammarName'],curState['stack'][-1]['ruleName'])
                eventualCursorMovement = res[0]
                nextRule = res[1]
                # pdb.set_trace()
                if nextRule[0] != LayerMsg.NEW_LAYER_REQUEST: #altrimenti lo spostamento lo gestisco già in manageLayerAnswer
                    if eventualCursorMovement is not None and eventualCursorMovement != 0:
                        if eventualCursorMovement > 0:
                            #time.sleep(1)
                            keyboard.type('__mf{}'.format(eventualCursorMovement))
                        else:
                            #time.sleep(1)
                            keyboard.type('__mb{}'.format(eventualCursorMovement)) 
                curState['stack'].pop()
                manageLayerAnswer(nextRule)
            else:
                res = layer.handleRawText((tokenText,tokenPos),idx,numBurstTokens['length'])
                #time.sleep(2) #per debug. Per darmi tempo di switchare su texstudio
                manageLayerAnswer(res)
        else:
            res = layer.handleRawText((tokenText,tokenPos),idx,numBurstTokens['length'])
            # pdb.set_trace()
            time.sleep(2) #per debug. Per darmi tempo di switchare su texstudio
            manageLayerAnswer(res)
    return '',status.HTTP_200_OK

"""UTILITY METHODS"""

def muoviCursoreAvantiDi(num_caratteri):
    if num_caratteri == 0:
        return
    if num_caratteri > 9:
        tmp_cnt = abs(num_caratteri)
        while tmp_cnt > 9:
            #time.sleep(1)
            keyboard.type('__mf9')
            tmp_cnt -= 9
        #time.sleep(1)
        keyboard.type('__mf{}'.format(tmp_cnt))
    else:
        #time.sleep(1)
        keyboard.type('__mf{}'.format(abs(num_caratteri)))

def pressSpaceTimes(times):
    for i in range(0,times):
        #time.sleep(1)
        keyboard.press(Key.space)

def pressBackspace(times):
    for i in range(0,times):
        keyboard.press(Key.backspace)

def muoviCursoreIndietroDi(num_caratteri):
    if num_caratteri == 0:
        return
    if num_caratteri > 9:
        tmp_cnt = abs(num_caratteri)
        while tmp_cnt > 9:
            #time.sleep(1)
            keyboard.type('__mb9')
            tmp_cnt -= 9
        #time.sleep(1)
        keyboard.type('__mb{}'.format(tmp_cnt))
    else:
        #time.sleep(1)
        keyboard.type('__mb{}'.format(abs(num_caratteri)))




    