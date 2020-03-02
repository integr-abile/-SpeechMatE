from math_modules.base_module import MathTopic
from jsgf import PublicRule, Literal, Grammar, AlternativeSet
from model.enums import NODE_TYPE
import os
from util.util import checkAllArrayElementsEquals


class Per(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter)
        self._name = os.path.basename(__file__)
        self._g = self.createGrammar()
        self._buffer = [] #tiene conto delle parole dette fino a che una e una sola regola non è stata metchata completamente
        self._matched_leafs_tag = [] #tiene conto delle foglie che sono state metchate, ma non inoltrate a causa di regole in conflitto per cui è stata necessaria una wait

    @staticmethod #mi permette di non mettere il self tra parentesi perchè non è un metodo di istanza
    def createGrammar():
        short_rule = Literal("per") #sto definendo un'expansion, non è una regola!!
        short_rule.tag = "\cdot" #il contributo di questa regola per il latex finale
        long_rule = Literal("moltiplicato per") #expansion
        long_rule.tag = "\cdot"
        multiplication_rule = PublicRule("multiplication",AlternativeSet(short_rule,long_rule)) #rule
        #setattr section
        setattr(multiplication_rule,'node_type',NODE_TYPE.FOGLIA) #aggiungiamo un attributo type direttamente sull'oggetto PublicRule per connotarlo come nodo o attributo
        setattr(multiplication_rule,'request_new_layer',False) #tiene conto del fatto che il match di questa regola possa richiedere la creazione di un nuovo layer
        setattr(multiplication_rule,'next_rules_trigger_words',None) #tiene conto del grafo della grammatica. Diverso da None solo quando 'request_new_layer':True
        #grammar creation section
        g = Grammar()
        g.add_rule(multiplication_rule)

        return g
    
    @staticmethod 
    def createLatexText(symbol):
        return '{}'.format(symbol)

    #TODO: vedere se questa funzione la posso portare a livello di base_module
    def getLatexAlternatives(self,last_token): #Chiamato su nuovo testo in input. Qua arriva token per token col suo POS
        print("MODULE: input info {}".format(last_token))
        self._buffer.append(last_token[0]) #[0] è il testo, [1] il POS
        tags = []
        node_types = [] #tiene conto die tipi delle regole metchate (e quindi anche di quate regole sono state metchate)
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
            self.sendNoMatchNotification()
        else:
            self.sendWaitRequest()



#module level functions
# def checkAllArrayElementsEquals(lst):
#     return lst[1:] == lst[:-1]

#funzione generatrice. Si chiamerà così in tutti i moduli per convenzione
def generateGrammars(answerPoolSetter):
    grammars = [Per(answerPoolSetter)] #e a seguire nell'array creo un'istanza per classe nel modulo
    return grammars


