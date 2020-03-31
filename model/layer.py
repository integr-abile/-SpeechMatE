from math_modules import algebra,analysis,basic_symbols,trigonometry,letters #genereremo dinamicamente i testi di questi import
import os
from model.enums import LayerMsg
from model.enums import ModuleMsg
from model.rule_touched_layer import RuleTouchedLayer
from model.module_answer_pool import ModuleAnswersPool
import concurrent.futures
from typing import Tuple
from util.util import checkAllArrayElementsEquals
from jsgf import PublicRule
import pdb



class Layer:

    def __init__(self):
        self.initAll()
        

    def initAll(self):
        self._answersPool = ModuleAnswersPool()
        self._allGrammars = []
        allNextRulesWords = [] #sarà una lista di dictionaryes contenente un dictionary per ogni grammatica (classe)
        self._allNextRuleWordsDict = {} #sarà il merge dei dictionaries di allNextRuleWords
        for module in [algebra,analysis,basic_symbols,trigonometry,letters]: #genereremo dinamicamente questo sorgente in fase di installazione..... perchè non si riesce ad iterare sui moduli
            moduleGrammar = module.generateGrammars(self._answersPool.addMessage)
            self._allGrammars.append(moduleGrammar[0]) #[0] è la grammatica vera e propria
            allNextRulesWords.append(moduleGrammar[1]) #[1] sono i dictionaries delle varie grammatiche
        self._allGrammars = [grammar for lst in self._allGrammars for grammar in lst] #flatten
        for nextRuleWordsDict in allNextRulesWords:
            self._allNextRuleWordsDict = {**self._allNextRuleWordsDict,**nextRuleWordsDict} #merge dictionaries
        self._leafRuleMatched = [] #tiene conto dei comandi foglia metchati che però non erano univoci e che quindi sono rimasti qui bufferizzati {'tag':'...','pos':3}
        self.allTextSent = '' #tiene conto di tutto ciò che è stato scritto da questo layer
        self._lastMsgTypeSent = None
        self._waitingGrammars = set() #grammatiche non out of play che hanno ritornato dal module un NoMatch o un Wait

    def handleRawText(self,text_pos,idx,num_burst_tokens):
        """Chiamata token per token e token per token deve rispondere. idx è l'indice di quel token nel burst"""
        print("LAYER: ricevuto input dal server {}".format(text_pos))

    #------------------------ CONTROLLI PRELIMINARI ---------------------------------------------

        if text_pos[0] == 'fine':
            # pdb.set_trace()
            if len(self._leafRuleMatched) > 0: #se ho metchato delle foglie nel frattempo
                farthest_leaf = sorted(self._leafRuleMatched,key=lambda rule:rule['idx'],reverse=True)[0] #prendo quella che ho metchato più in là nel burst
                self.allTextSent +='{}'.format(farthest_leaf)
                self.initAll()
                self._lastMsgTypeSent = LayerMsg.TEXT
                return (LayerMsg.TEXT,farthest_leaf,0) #farthest_leaf dict {'tag':'...','idx':3}. Gli passo anche l'idx perchè almeno sa che la parte restante del testo è free text
            else: #nessuna regola foglia è stata finora metchata
                self.initAll()
                self._lastMsgTypeSent = LayerMsg.END_THIS_LAYER
                return (LayerMsg.END_THIS_LAYER,None)


         #controllo parole di trigger, altrimenti redirect back come TEXT al server
        print("LAYER: next words list {}".format(self.nextWordsDictToList()))
        print("LAYER: Waiting grammars {}".format(self._waitingGrammars))
        if text_pos[0] not in self.nextWordsDictToList():
            return self.manageRewind(text_pos)
        
        #test token wrt regole che al giro prima mi hanno chiesto di aspettare. Se appartiene ad esse faccio passare, altrimenti REWIND con reset all
        if self._lastMsgTypeSent == LayerMsg.WAIT:
            # pdb.set_trace()
            rulesTouched = RuleTouchedLayer().checkRuleReached(text_pos)
            # pdb.set_trace()
            if len(self._waitingGrammars.intersection(rulesTouched)) == 0: #se il nuovo token non c'entra nulla con le regole in attesa
                return self.manageRewind(text_pos)
            


        
    
    #-------------------------- MATCHING RULES ------------------------------------------
        
        #inoltro ai moduli con la creazione dei thread e rispondo solo quando hanno finito tutti (ThreadPoolExecutor). Ognuno popola la struttura dati condivisa
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self._allGrammars)) as executor:
            for grammar in self._allGrammars:
                executor.submit(grammar.getLatexAlternatives,text_pos)

    #---------------------------------------- MANAGE MODULES ANSWERS ---------------------------------------------------------
        #guardo la struttura dati condivisa per fare le mie valutazioni
        print("LAYER: ora che HANNO FINITO TUTTI I THREAD guardo cosa mi hanno risposto")
        answers = []
        while self._answersPool.empty() is False:
            msg = self._answersPool.popMessage()
            if msg[0]==ModuleMsg.TEXT:
                if msg[4]['leaf'] == True:
                    self._leafRuleMatched.append({'tag':msg[1],'idx':idx}) #[1] è l'indice nel quale c'è l'effettivo testo in latex
            answers.append(msg)
        
        print('answers: {}'.format(answers))
        if all([elem[0] != ModuleMsg.NEW_LAYER_REQUEST for elem in answers]): #se non c'è nessuna richiesta di nuovo layer in nessuna delle regole metchate
            if all([elem[0] != ModuleMsg.WAIT for elem in answers]): #se c'è coerenza tra le regole metchate in ogni modulo:
                if all(elem[0] == ModuleMsg.NO_MATCH for elem in answers): #se non è stata metchata nessuna regola 
                    self._lastMsgTypeSent = LayerMsg.WAIT
                    #(non aggiorniamo nextRuleWordDict perchè non abbiamo metchato nessuna regola)
                    for answer in answers:
                        grammarName = answer[3]
                        self._waitingGrammars.add(grammarName)
                    return (LayerMsg.WAIT,None)
                else: #ci sono alcuni non match o alcune rinunce permanenti e alcuni contributi latex, oppure tutti contributi testo.
                    #controllo la coerenza tra moduli
                    relevant_answers = list(filter(lambda answer:answer[0]!=ModuleMsg.OUT_OF_PLAY,answers)) #filtro solo le risposte dei moduli CHE HANNO ANCORA DA DIRMI QUALCOSA
                    candidate_transcription = list(map(lambda answer:answer[1],relevant_answers)) #estraggo solo il contributo latex di ognuna (TEXT e NO_MATCH)
                    print('candidate transcriptions: {}'.format(candidate_transcription))
                    # pdb.set_trace()
                    if checkAllArrayElementsEquals(candidate_transcription): #se anche tra moduli c'è coerenza in merito a cosa trascrivere
                        if all(elem[1]==None for elem in relevant_answers): #se tutti i moduli mi stanno dicendo che non hanno metchato niente o sono con testi vuoti, ma comunque non sono out-of-play
                            for answer in relevant_answers:
                                grammarName = answer[3]
                                self._waitingGrammars.add(grammarName)
                                if answer[0] == ModuleMsg.TEXT: #se ho questo tipo di messaggio vuol dire che c'è stata comunque una regola metchata e quindi devo aggiornare le trigger words se non è stata metchata una foglia per cui le trigger words non hanno senso
                                    if answer[4]['leaf'] == False:
                                        self._allNextRuleWordsDict[grammarName] = answer[2]['next_rules_words']
                            self._lastMsgTypeSent = LayerMsg.WAIT
                            return (LayerMsg.WAIT,None)
                        else: #se qualche testo latex sensato è rimasto nei match mescolato a qualche no_match
                            if all([elem[0] == ModuleMsg.TEXT for elem in relevant_answers]): #se le risposte sono tutte testo
                                if all([elem[4]['leaf'] == True for elem in relevant_answers]):
                                    self.allTextSent +='{}'.format(candidate_transcription[0]) #posso prendere [0] perchè tanto sono tutti uguali
                                    #non aggiorno lo stato perchè tanto adesso finirà il layer
                                    eventualLeafEndCursorMovement = [elem[5] for elem in relevant_answers][0]
                                    self.initAll()
                                    self._lastMsgTypeSent = LayerMsg.TEXT
                                    return (LayerMsg.TEXT,candidate_transcription[0],eventualLeafEndCursorMovement)
                                else: #non sono tutte foglie
                                    self.allTextSent +='{}'.format(candidate_transcription[0])
                                    #aggiorno lo stato delle trigger words
                                    for answer in relevant_answers:
                                        grammarName = answer[3]
                                        # self._waitingGrammars.add(grammarName)
                                        # pdb.set_trace()
                                        if answer[4]['leaf'] == False:
                                            self._allNextRuleWordsDict[grammarName] = answer[2]['next_rules_words']
                                    eventualLeafEndCursorMovement = [elem[5] for elem in relevant_answers][0]
                                    self._lastMsgTypeSent = LayerMsg.TEXT
                                    return (LayerMsg.TEXT,candidate_transcription[0],eventualLeafEndCursorMovement)
                            else: #effettivamente c'è ancora qualche messaggio NO_MATCH
                                #salvo lo stato delle grammatiche che hanno metchato e ritorno wait
                                for answer in relevant_answers:
                                    grammarName = answer[3]
                                    if answer[0] == ModuleMsg.TEXT: #se ho questo tipo di messaggio vuol dire che c'è stata comunque una regola metchata e quindi devo aggiornare le trigger words
                                        if answer[4]['leaf'] == False:
                                            self._allNextRuleWordsDict[grammarName] = answer[2]['next_rules_words']
                                    else:
                                        self._waitingGrammars.add(grammarName)
                                self._lastMsgTypeSent = LayerMsg.WAIT
                                return (LayerMsg.WAIT,None)
                    else: #se tra moduli trascriverebbero cose diverse, oppure altri metchano regole, altri no 
                        if idx == num_burst_tokens-1: #il server mi ha mandando l'ultimo token del burst
                            candidatesDesWithoutNone = [elem for elem in candidate_transcription if elem is not None]
                            #filtro dalle answer quelle che non hanno metchato niente
                            answersWithoutNoMatch = [elem for elem in relevant_answers if elem[0] != ModuleMsg.NO_MATCH and elem[1] is not None] #rimangono solo le risposte con TEXT
                            print('candidate transcriptions WITHOUT NONE: {}'.format(candidatesDesWithoutNone))
                            if checkAllArrayElementsEquals(candidatesDesWithoutNone):
                                if all(elem[4]['leaf'] == True for elem in answersWithoutNoMatch):
                                    self.allTextSent +='{}'.format(candidatesDesWithoutNone[0])
                                    eventualLeafEndCursorMovement = [elem[5] for elem in answersWithoutNoMatch][0]
                                    self.initAll()
                                    self._lastMsgTypeSent = LayerMsg.TEXT
                                    return (LayerMsg.TEXT,candidatesDesWithoutNone[0],eventualLeafEndCursorMovement)
                                else:
                                    self.allTextSent +='{}'.format(candidatesDesWithoutNone[0])
                                    eventualLeafEndCursorMovement = [elem[5] for elem in answersWithoutNoMatch][0]
                                    self._lastMsgTypeSent = LayerMsg.TEXT
                                    return (LayerMsg.TEXT,candidatesDesWithoutNone[0],eventualLeafEndCursorMovement)
                            else: #se anche nell'ultimo token non c'è coerenza in quello che scriverei
                                for answer in answersWithoutNoMatch:
                                    grammarName = answer[3]
                                    self._waitingGrammars.add(grammarName)
                                    if answer[4]['leaf'] == False:
                                        self._allNextRuleWordsDict[grammarName] = answer[2]['next_rules_words']
                                self._lastMsgTypeSent = LayerMsg.WAIT
                                return (LayerMsg.WAIT,None)
                        else: #non sono ancora arrivato all'ultimo token del burst
                            #salvo lo stato delle grammatiche che hanno metchato e ritorno wait
                            for answer in relevant_answers:
                                grammarName = answer[3]
                                if answer[0] == ModuleMsg.TEXT: #se ho questo tipo di messaggio vuol dire che c'è stata comunque una regola metchata e quindi devo aggiornare le trigger words
                                    if answer[4]['leaf'] == False:
                                        self._allNextRuleWordsDict[grammarName] = answer[2]['next_rules_words']
                                else:
                                    self._waitingGrammars.add(grammarName)
                            self._lastMsgTypeSent = LayerMsg.WAIT
                            return (LayerMsg.WAIT,None)
            else: #C'è qualche WAIT. ci sono opinioni discordanti rispetto a quello che si dovrebbe scrivere in latex tra le regole metchate nei vari moduli
                self._lastMsgTypeSent = LayerMsg.WAIT
                for answer in answers:
                    if answer[0] == ModuleMsg.WAIT:
                        grammarName = answer[3]
                        self._waitingGrammars.add(grammarName)
                        self._allNextRuleWordsDict[grammarName] = answer[2]['next_rules_words']
                return (LayerMsg.WAIT,None)
        else: #c'è almeno un match che richiede di INIZIARE UN NUOVO LAYER, quindi gli dò priorità
            #devo dirlo al server dicendogli anche che parole servono per sbloccarmi
            # pdb.set_trace()
            allTriggerWords = [elem[2]['next_rules_words'] for elem in answers if elem[0] == ModuleMsg.NEW_LAYER_REQUEST][0]
            grammarName = [elem[3] for elem in answers if elem[0] == ModuleMsg.NEW_LAYER_REQUEST][0]
            rulenameRequestingNewLayer = [elem[4] for elem in answers if elem[0] == ModuleMsg.NEW_LAYER_REQUEST][0] 
            cursorOffset = [elem[5] for elem in answers if elem[0] == ModuleMsg.NEW_LAYER_REQUEST][0]
            tag = [elem[6] for elem in answers if elem[0] == ModuleMsg.NEW_LAYER_REQUEST][0]
            carryHomeLength = [elem[7] for elem in answers if elem[0] == ModuleMsg.NEW_LAYER_REQUEST][0] if [elem[7] for elem in answers if elem[0] == ModuleMsg.NEW_LAYER_REQUEST][0] != -1 else None
            self._lastMsgTypeSent = LayerMsg.NEW_LAYER_REQUEST
            # pdb.set_trace()
            self._allNextRuleWordsDict[grammarName] = allTriggerWords
            self._waitingGrammars.add(grammarName)
            #faccio arrivare al server le allTriggerWords perchè deve potermi riattivare con queste parole e il controllo lo farà lui
            self.initAll()
            return (LayerMsg.NEW_LAYER_REQUEST,allTriggerWords,grammarName,rulenameRequestingNewLayer,cursorOffset,tag,carryHomeLength)
            
        self._lastMsgTypeSent = LayerMsg.TEXT
        return (LayerMsg.TEXT,"shouldn't happened",0)


    def redirectRuleToSrv(self,rule, grammar_name, cursor_offset):
        if rule is None:
            return (LayerMsg.WAIT,None)
        if rule.request_new_layer:
            allTriggerWords = rule.next_rules_trigger_words
            grammarName = grammar_name
            rulenameRequestingNewLayer = rule.name
            cursorOffset = cursor_offset
            tag = rule.tags[0] if len(rule.tags) > 0 else None
            carryHomeLength = rule.go_to_begin if hasattr(rule,'go_to_begin') else None
            self._lastMsgTypeSent = LayerMsg.NEW_LAYER_REQUEST
            self.initAll()
            return (LayerMsg.NEW_LAYER_REQUEST,allTriggerWords,grammarName,rulenameRequestingNewLayer,cursorOffset,tag,carryHomeLength)
        else:
            eventualCursorMovement = rule.leaf_end_cursor_movement if hasattr(rule,'leaf_end_cursor_movement') else 0
            return (LayerMsg.TEXT,rule.tags[0] if len(rule.tags) > 0 else None,eventualCursorMovement)




    def updateGrammarStringFormat(self,text,grammarName,rulename):
        """
        Canale di comunicazione server->module
        Da rulename è possibile risalire alla regola che ha richiesto un nuovo layer, perciò si può sapere dove 
        andrebbe a scrivere (logica di controllo nel codice del modulo). text è il testo da mettere in quello spazio
        """
        # pdb.set_trace()
        print('update string format layer prev con {}'.format(text))
        for grammar in self._allGrammars: #grammar è tipo Per, Piu
            if grammar.moduleName == grammarName: #grammar match
                #recupero la regola con le parole di attivazione che metchano lstOfTriggeringWords
                for grammar_rule in grammar._g.rules: 
                    # pdb.set_trace()
                    if grammar_rule.name == rulename: #rule match
                        grammar.updateStringFormat(text,grammar_rule.name)
                        print('ottenendo offset...')
                        res = grammar.getCursorOffsetForRulename(grammar_rule.name,True)
                        # pdb.set_trace()
                        cursorOffset = res[0]
                        isEndingRule = res[1]
                        nextRule = res[2]
                        if isEndingRule: #resetto tutte le grammatiche
                            self.initAll()
                        return (cursorOffset,self.redirectRuleToSrv(nextRule,grammarName,cursorOffset))
                        

    #-------------------- UTILITY ---------------------------
    def nextWordsDictToList(self):
        triggeringWords = []
        # pdb.set_trace()
        for grammarName in self._allNextRuleWordsDict:
            triggeringWords += self._allNextRuleWordsDict[grammarName]
        unique_list = list(set(triggeringWords))
        return unique_list


    def wordsOfWaitingGrammars(self):
        triggeringWords = []
        # pdb.set_trace()
        for grammarName in self._allNextRuleWordsDict:
            if grammarName in self._waitingGrammars:
                triggeringWords += self._allNextRuleWordsDict[grammarName]
        unique_list = list(set(triggeringWords))
        return unique_list


    def manageRewind(self,text_pos):
        last_words_to_say = ''
        if len(self._leafRuleMatched) > 0:
            # pdb.set_trace()
            farthest_leaf = sorted(self._leafRuleMatched,key=lambda rule:rule['idx'],reverse=True)[0] #prendo quella che ho metchato più in là nel burst
            farthest_leaf_index = farthest_leaf['idx']
            farthest_leaf_tag = farthest_leaf['tag']
            self.initAll()
            return(LayerMsg.REWIND,farthest_leaf_index+1,farthest_leaf_tag)
        else:
            #redirect back
            self._lastMsgTypeSent = LayerMsg.TEXT
            self.allTextSent += '{}'.format(text_pos[0])
            last_words_to_say += '{}'.format(text_pos[0])
            self.initAll() #resetto perchè ora un comando (anche se non compariva nella grammatica, è stato dato.. che sia un numero o un monomio)
            return (LayerMsg.TEXT,last_words_to_say,0)


        
