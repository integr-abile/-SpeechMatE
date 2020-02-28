from math_modules.base_module import MathTopic
from jsgf import PublicRule, Literal, Grammar, AlternativeSet
from model.enums import NODE_TYPE
import os

class Per(MathTopic):
    def __init__(self):
        super().__init__()
        self._name = os.path.basename(__file__)
        self._g = self.createGrammar()
        self._buffer = [] #tiene conto delle parole dette fino a che una regola non è stata metchata completamente

    @staticmethod #mi permette di non mettere il self tra parentesi perchè non è un metodo di istanza
    def createGrammar():
        short_rule = Literal("per") #expansion
        short_rule.tag = "\cdot" #il contributo di questa regola per il latex finale
        long_rule = Literal("moltiplicato per") #expansion
        long_rule.tag = "\cdot"
        multiplication_rule = PublicRule("multiplication",AlternativeSet(short_rule,long_rule)) #rule
        setattr(multiplication_rule,'type',NODE_TYPE.FOGLIA.name) #aggiungiamo un attributo type direttamente sull'oggetto PublicRule per connotarlo come nodo o attributo
        g = Grammar()
        g.add_rule(multiplication_rule)

        return g
    
    @staticmethod 
    def createLatexText(symbol):
        return '{}'.format(symbol)

    
    def onInput(self,sender,notification_name,last_token): #Chiamato su nuovo testo in input. Qua arriva token per token col suo POS
        print("notification info {}".format(last_token))
        self._buffer.append(last_token[0]) #[0] è il testo
        tags = []
        for i in range(1,len(self._buffer)):
            matched_rules = self._g.find_matching_rules(' '.join(self._buffer[-i:])) #qua creo ad ogni iterazione stringhe sempre più lunghe
            for matched_rule in matched_rules:
                matched_rule.disable() #disabilitandola è come se la marcassi come visitata
                tags.append([tag for tag in matched_rule.matched_tags if len(matched_rule.matched_tags)>0])
        #controllo che i tag trovati siano tutti uguali, altrimenti non notifico, ma aggiorno solo lo stato
        if(checkAllArrayElementsEquals(tags) and len(tags)>0):
            tags = [tag for lst in tags for tag in lst] #flatten
            self.sendLatexText(self.createLatexText(tags[0]))


def checkAllArrayElementsEquals(lst):
    return lst[1:] == lst[:-1]

#funzione generatrice. Si chiamerà così in tutti i moduli per convenzione
def generateGrammars():
    grammars = [Per()] #e a seguire nell'array creo un'istanza per classe nel modulo
    return grammars


