from model.module_answer_pool import ModuleAnswersPool
from model.enums import ModuleMsg
from typing import Callable
from util.util import checkAllArrayElementsEquals
from model.enums import NODE_TYPE
import pdb


class MathTopic:

    def __init__(self,answerPoolSetter,module_name):
        self._answerPoolSetter = answerPoolSetter
        self._g = None
        self._buffer = [] #tiene conto delle parole dette fino a che una e una sola regola non è stata metchata completamente
        self._outOfPlayFlag = False #tiene conto se in questo modulo esiste ancora la possibilità che una delle regole possa venire ancora metchata
        self.moduleName = module_name

#------------------SENDING MESSAGE TO LAYER------------------------------
#tutti i text indice 1, tutti next_rules_words indice 2, tutti grammar_name indice 3
    def sendLatexText(self,text,node_type_info={'leaf':False},next_rules_words={'next_rules_words':[]}):
        """node_type_info è un dizionario {'leaf':bool} (di default leaf:False) che specifica se la regola triggerata è una foglia oppure no"""
        self._answerPoolSetter((ModuleMsg.TEXT,text,next_rules_words,self.moduleName,node_type_info))

    def postNewLayerRequest(self,rulenameRequestingNewLayer,cursorOffset,tag,carryHomeLength,next_rules_words={'next_rules_words':[]}):
        self._answerPoolSetter((ModuleMsg.NEW_LAYER_REQUEST,None,next_rules_words,self.moduleName,rulenameRequestingNewLayer,cursorOffset,tag,carryHomeLength)) 
    
    def sendWaitRequest(self,next_rules_words={'next_rules_words':[]}):
        self._answerPoolSetter((ModuleMsg.WAIT,None,next_rules_words,self.moduleName))
    
    def sendNoMatchNotification(self):
        self._answerPoolSetter((ModuleMsg.NO_MATCH,None,None,self.moduleName))
    
    def sendMyselfDisableNotification(self):
        self._answerPoolSetter((ModuleMsg.OUT_OF_PLAY,None,None,self.moduleName))

#------------------------------TO OVERRIDE-----------------------------------
 
    def createLatexText(self,text,rule_name=None): #must override
        return None

    def updateStringFormat(self,text,rulename): #override if needed
        pass

    def getCursorOffsetForRulename(self,rulename,calledFromLayer=False): #override se non stiamo parlando di una foglia
        """True o False indica che dopo lo spostamento del cursore questa regola è giunta al capolinea e quindi chiede al layer di riabilitare tutte le regole"""
        return (0,False)

#-----------------------------------------------------------------------


    def getLatexAlternatives(self,last_token): #Chiamato su nuovo testo in input. Qua arriva token per token col suo POS

        """CHECK INPUT PRELIMINARE"""
        if self._outOfPlayFlag:
            print('{} è fuori dal gioco'.format(self.moduleName))
            self.sendMyselfDisableNotification()
            return

        print("MODULE {}: input info {}".format(self.moduleName,last_token))
        self._buffer.append(last_token[0]) #[0] è il testo, [1] il POS

        if last_token[0] not in self._nextRulesWords:
            self._outOfPlayFlag = True
            self.sendMyselfDisableNotification()
            return

        """Init response variables"""
        tags = []
        node_types = [] #tiene conto dei tipi delle regole metchate (e quindi anche di quate regole sono state metchate)
        next_rules_words = [] #tiene conto delle parole successive per triggerare nuove regole (utile nel caso di richiesta di nuovi layer)
        rulenameRequestingNewLayer = None #servirà per il calcolo dell'offset del cursore
        tagOfRulenameRequestingNewLayer = None #perchè tra tutti i tag (se esistono cmq ho fatto male la grammatica) questo deve avere la precedenza. Può anche non esistere
        carryHomeLength = -1 #se un comando specifica di quanto tornare indietro prima di far avanzare il cursore 

        for i in range(1,len(self._buffer)+1): #+1 perchè andrò indietro con gli indici
            matched_rules = self._g.find_matching_rules(' '.join(self._buffer[-i:])) #qua creo ad ogni iterazione stringhe sempre più lunghe partendo dal fondo
            print("matching rules: {}".format(matched_rules))
            for matched_rule in matched_rules: #per ogni regola metchata
                matched_rule.disable() #disabilitandola è come se la marcassi come visitata e il sistema non la metcha più
                # pdb.set_trace()
                if hasattr(matched_rule,'go_to_begin'):
                    carryHomeLength = matched_rule.go_to_begin
                tags.append([tag for tag in matched_rule.matched_tags if len(matched_rule.matched_tags)>0])
                node_types.append(matched_rule.node_type)
                [next_rules_words.append(trigger_word) for trigger_word in matched_rule.next_rules_trigger_words]
                if matched_rule.request_new_layer:
                    rulenameRequestingNewLayer = matched_rule.name
                    tagOfRulenameRequestingNewLayer = matched_rule.matched_tags[0] if len(matched_rule.matched_tags) > 0 else None
                    
        tags = [tag for lst in tags for tag in lst] #flatten
        # pdb.set_trace()
        # next_rules_words = [word for listOfWords in next_rules_words for word in listOfWords] #flatten.
        """Aggiorno stato"""
        self._nextRulesWords = next_rules_words if len(next_rules_words) > 0 else self._nextRulesWords 

        if rulenameRequestingNewLayer is not None: #se almeno una delle regole ha richiesto un nuovo layer, questa deve avere la priorità (si tratta anche di fare bene la grammatica)
            #trovo di quanto devo muovere il cursore rispetto a dov'è attualmente
            curOffset = self.getCursorOffsetForRulename(rulenameRequestingNewLayer)[0] #0 è l'offset. se richiedo il layer è ovvio che non è finita la regola
            self.postNewLayerRequest(rulenameRequestingNewLayer,curOffset,tagOfRulenameRequestingNewLayer,carryHomeLength,{'next_rules_words':next_rules_words})
        elif checkAllArrayElementsEquals(tags) and len(tags)>0: #se tutte le regole qua sono d'accordo su cosa scrivere in latex
            areAllMatchedRulesInternal = all(node_type == NODE_TYPE.INTERNO for node_type in node_types)
            # pdb.set_trace()
            self.sendLatexText(tags[0],{'leaf':not areAllMatchedRulesInternal},{'next_rules_words':next_rules_words}) #se c'è almeno una foglia tra quelle metchate notifico foglia così il layer se la può salvare
        elif len(node_types) == 0: #nessuna regola è stata metchata
            self.sendNoMatchNotification()
        else:
            self.sendWaitRequest({'next_rules_words':next_rules_words})
        

    
