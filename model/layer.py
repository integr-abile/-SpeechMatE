from math_modules import algebra,analysis,basic_symbols,trigonometry #genereremo dinamicamente i testi di questi import
import os
from model.enums import LayerMsg
from model.enums import ModuleMsg
from model.module_answer_pool import ModuleAnswersPool
import concurrent.futures
from typing import Tuple
from util.util import checkAllArrayElementsEquals


class Layer:
    
    def handleRawText(self,text_pos,idx):
        """Chiamata token per token e token per token deve rispondere. idx è l'indice di quel token nel burst"""
        print("LAYER: ricevuto input dal server {}".format(text_pos))

        if text_pos[0] == 'fine':
            if len(self._leafRuleMatched) > 0: #se ho metchato delle foglie nel frattempo
                farthest_leaf = sorted(self._leafRuleMatched,key=lambda rule:rule['idx'],reverse=True)[0] #prendo quella che ho metchato più in là nel burst
                return (LayerMsg.END_THIS_LAYER_WITH_TEXT,farthest_leaf) #farthest_leaf dict {'tag':'...','idx':3}. Gli passo anche l'idx perchè almeno sa che la parte restante del testo è free text
            else: #nessuna regola foglia è stata finora metchata
                return (LayerMsg.END_THIS_LAYER,None)

        #inoltro ai moduli con la creazione dei thread e rispondo solo quando hanno finito tutti (ThreadPoolExecutor). Ognuno popola la struttura dati condivisa
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self._allGrammars)) as executor:
            for grammar in self._allGrammars:
                executor.submit(grammar.getLatexAlternatives,text_pos)

        #guardo la struttura dati condivisa per fare le mie valutazioni
        print("LAYER: ora che hanno finito tutti i thread guardo cosa mi hanno risposto")
        answers = []
        while self._answersPool.empty() is False:
            msg = self._answersPool.popMessage()
            if msg[2] is not None and 'leaf' in msg[2]: #x es in NEW_LAYER_REQUEST non c'è
                if msg[2]['leaf'] == True:
                    self._leafRuleMatched.append({'tag':msg[1],'idx':idx})
            answers.append(msg)
        
        # print(answers)
        if all([elem[0] != ModuleMsg.NEW_LAYER_REQUEST for elem in answers]): #se non c'è nessuna richiesta di nuovo layer in nessuna delle regole metchate
            if all([elem[0] != ModuleMsg.WAIT for elem in answers]): #se c'è coerenza tra le regole metchate in ogni modulo:
                if all(elem[0] == ModuleMsg.NO_MATCH for elem in answers): #se non è stata metchata nessuna regola
                    return (LayerMsg.WAIT,None)
                else:
                    #controllo la coerenza tra moduli
                    candidate_transcription = list(map(lambda answer:answer[1],answers))
                    print('candidate transcriptions: {}'.format(candidate_transcription))
                    if checkAllArrayElementsEquals(candidate_transcription): #se anche tra moduli c'è coerenza in merito a cosa trascrivere
                        if all([elem[2]['leaf'] == True for elem in answers]): #se tutte le risposte arrivano da foglie allora non esiste più nessuna regola triggerabile quindi finisco il layer
                            return (LayerMsg.END_THIS_LAYER_WITH_TEXT,candidate_transcription[0])
                        else:
                            return (LayerMsg.TEXT,candidate_transcription[0])
                    else: #se tra moduli trascriverebbero cose diverse
                        return (LayerMsg.WAIT,None)
            else: #ci sono opinioni discordanti rispetto a quello che si dovrebbe scrivere in latex tra le regole metchate nei vari moduli
                return (LayerMsg.WAIT,None)
        else: #c'è almeno un match che richiede di iniziare un nuovo layer, quindi gli dò priorità
            #devo dirlo al server dicendogli anche che parole servono per sbloccarmi
            allTriggerWords = [elem[2]['layer_unlock_words'] for elem in answers if elem[0] == ModuleMsg.NEW_LAYER_REQUEST]
            allTriggerWords = [triggerWord for triggerWords in allTriggerWords for triggerWord in triggerWords] #flatten
            return (LayerMsg.NEW_LAYER_REQUEST,allTriggerWords)
            
        return (LayerMsg.TEXT,"shouldn't happened")

    
    def __init__(self):
        self._answersPool = ModuleAnswersPool()
        self._allGrammars = []
        for module in [algebra,analysis,basic_symbols,trigonometry]: #genereremo dinamicamente questo sorgente in fase di installazione..... perchè non si riesce ad iterare sui moduli
            self._allGrammars.append(module.generateGrammars(self._answersPool.addMessage))
        self._allGrammars = [grammar for lst in self._allGrammars for grammar in lst] #flatten
        self._leafRuleMatched = [] #tiene conto dei comandi foglia metchati che però non erano univoci e che quindi sono rimasti qui bufferizzati {'tag':'...','pos':3}
        
