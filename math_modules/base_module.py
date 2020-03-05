from model.module_answer_pool import ModuleAnswersPool
from model.enums import ModuleMsg
from typing import Callable
from util.util import checkAllArrayElementsEquals
from model.enums import NODE_TYPE


class MathTopic:

    def __init__(self,answerPoolSetter,module_name,num_max_entry_rules_tokens):
        self._answerPoolSetter = answerPoolSetter
        self._g = None
        self._buffer = [] #tiene conto delle parole dette fino a che una e una sola regola non è stata metchata completamente
        self._outOfPlayFlag = False #tiene conto se in questo modulo esiste ancora la possibilità che una delle regole possa venire ancora metchata
        self._moduleName = module_name
        self._numMaxEntryRulesTokens = num_max_entry_rules_tokens #dipendente dalla grammatica

    def sendLatexText(self,text,node_type_info={'leaf':False}):
        """node_type_info è un dizionario {'leaf':bool} (di default leaf:False) che specifica se la regola triggerata è una foglia oppure no"""
        self._answerPoolSetter((ModuleMsg.TEXT,text,node_type_info))

    def postNewLayerRequest(self,unlock_node_words={'layer_unlock_words':[]}):
        self._answerPoolSetter((ModuleMsg.NEW_LAYER_REQUEST,None,unlock_node_words))
    
    def sendWaitRequest(self):
        self._answerPoolSetter((ModuleMsg.WAIT,None,None))
    
    def sendNoMatchNotification(self):
        self._answerPoolSetter((ModuleMsg.NO_MATCH,None,None))
    
    def sendMyselfDisableNotification(self):
        self._answerPoolSetter((ModuleMsg.OUT_OF_PLAY,None,None))

    @staticmethod 
    def createLatexText(symbol):
        return None

    def getLatexAlternatives(self,last_token): #Chiamato su nuovo testo in input. Qua arriva token per token col suo POS

        if self._outOfPlayFlag:
            print('{} è fuori dal gioco'.format(self._moduleName))
            self.sendMyselfDisableNotification()
            return

        print("MODULE: input info {}".format(last_token))
        self._buffer.append(last_token[0]) #[0] è il testo, [1] il POS
        tags = []
        node_types = [] #tiene conto dei tipi delle regole metchate (e quindi anche di quate regole sono state metchate)
        unlock_layer_words = [] #tiene conto delle parole successive per triggerare nuove regole (utile nel caso di richiesta di nuovi layer)
        for i in range(1,len(self._buffer)+1): #+1 perchè andrò indietro con gli indici
            matched_rules = self._g.find_matching_rules(' '.join(self._buffer[-i:])) #qua creo ad ogni iterazione stringhe sempre più lunghe partendo dal fondo
            print("matching rules: {}".format(matched_rules))
            for matched_rule in matched_rules:
                matched_rule.disable() #disabilitandola è come se la marcassi come visitata e il sistema non la metcha più
                tags.append([tag for tag in matched_rule.matched_tags if len(matched_rule.matched_tags)>0])
                node_types.append(matched_rule.node_type)
                if matched_rule.request_new_layer:
                    [unlock_layer_words.append(trigger_word) for trigger_word in matched_rule.next_rules_trigger_words]

        tags = [tag for lst in tags for tag in lst] #flatten
        if len(unlock_layer_words) > 0: #se almeno una delle regole ha richiesto un nuovo layer, questa deve avere la priorità (si tratta anche di fare bene la grammatica)
            self.postNewLayerRequest({'layer_unlock_words':unlock_layer_words})
        elif checkAllArrayElementsEquals(tags) and len(tags)>0: #se tutte le regole qua sono d'accordo su cosa scrivere in latex
            areAllMatchedRulesInternal = all(node_type == NODE_TYPE.INTERNO for node_type in node_types)
            self.sendLatexText(self.createLatexText(tags[0]),{'leaf':not areAllMatchedRulesInternal}) #se c'è almeno una foglia tra quelle metchate notifico foglia così il layer se la può salvare
        elif len(node_types) == 0: #nessuna regola è stata metchata
            if len(self._buffer) >= self._numMaxEntryRulesTokens: #se non ho metchato niente adesso, non posso pensare che potrò metchare
                self.sendMyselfDisableNotification()
                self._outOfPlayFlag = True
            else: #se invece potrei ancora metchare qualcosa con i prossimi token. Sviluppo futuro potrebbe essere fare un'analisi linguistica delle parole di attivazione delle regole e non solo del conteggio
                self.sendNoMatchNotification()
        else:
            self.sendWaitRequest()
        

    
