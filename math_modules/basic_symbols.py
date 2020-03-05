from math_modules.base_module import MathTopic
from jsgf import PublicRule, Literal, Grammar, AlternativeSet
from model.enums import NODE_TYPE

#TODO: Modificare il costruttore in stile Per
class Piu(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Piu.get_classname(),1)
        self._g = self.createGrammar()
    
    @staticmethod
    def createGrammar():
        rule = Literal("più")
        rule.tag = "+"
        plusRule = PublicRule("sum",rule)
        #setattr section
        setattr(plusRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(plusRule,'request_new_layer',False)
        setattr(plusRule,'next_rules_trigger_words',None)
        setattr(plusRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(plusRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    @staticmethod 
    def createLatexText(symbol):
        return '{}'.format(symbol)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)


class Per(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Per.get_classname(),2) #2 è la lunghezza massima per triggerare una entry_rule. La devo vedere io di volta in volta a seconda della grammatica
        self._g = self.createGrammar()
        # self._matched_leafs_tag = [] #tiene conto delle foglie che sono state metchate, ma non inoltrate a causa di regole in conflitto per cui è stata necessaria una wait

    @staticmethod #mi permette di non mettere il self tra parentesi perchè non è un metodo di istanza
    def createGrammar():
        short_rule = Literal("per") #sto definendo un'expansion, non è una regola!!
        short_rule.tag = "\cdot" #il contributo di questa regola per il latex finale
        long_rule = Literal("moltiplicato per") #expansion
        long_rule.tag = "\cdot"
        multiplication_rule = PublicRule("multiplication",AlternativeSet(short_rule,long_rule)) #rule
        #setattr section (Per ogni regola 4 setattr)
        setattr(multiplication_rule,'node_type',NODE_TYPE.FOGLIA) #aggiungiamo un attributo type direttamente sull'oggetto PublicRule per connotarlo come nodo o attributo
        setattr(multiplication_rule,'request_new_layer',False) #tiene conto del fatto che il match di questa regola possa richiedere la creazione di un nuovo layer
        setattr(multiplication_rule,'next_rules_trigger_words',None) #tiene conto del grafo della grammatica. Diverso da None solo quando 'request_new_layer':True
        setattr(multiplication_rule,'is_entry_rule',True) #tiene conto se questa regola è un entry point di un grafo
        #grammar creation section
        g = Grammar()
        g.add_rule(multiplication_rule)

        return g
    
    @classmethod
    def get_classname(cls):
        return cls.__name__
    
    @staticmethod 
    def createLatexText(symbol):
        return '{}'.format(symbol)

    def getLatexAlternatives(self,last_token):
        super().getLatexAlternatives(last_token)


#funzione generatrice. Si chiamerà così in tutti i moduli per convenzione
def generateGrammars(answerPoolSetter):
    grammars = [Per(answerPoolSetter),Piu(answerPoolSetter)] #e a seguire nell'array creo un'istanza per classe nel modulo
    return grammars


