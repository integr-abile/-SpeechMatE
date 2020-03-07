from math_modules.base_module import MathTopic
from jsgf import PublicRule, Literal, Grammar, AlternativeSet
from model.enums import NODE_TYPE

class Potenza(MathTopic):
    
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Potenza.get_classname(),1)
        self._g = self.createGrammar()
        self._cursorPos = 0
        #rule template (per regole complesse con filler). Le foglie come i simboli semplici non ce l'hanno
        self._ruleTemplate = '^{0}'
        #brace-rule-fillers
        self._body0 = ''
        self.entryRuleWords = ["alla"]
        #se mi arriva una richiesta di riposizionamento del cursore vuol dire che il srv ha già fatto il controllo che l'ultimo comando dato è DETTATURA e non EDITING
        #perciò devo sapere dov'è il cursore perchè il metodo di calcolo del cursore, partendo da questa posizione e dalla nuova regola metchata, sappia di quanto andare avanti
        
    
    @staticmethod
    def createGrammar():
        rule = Literal("alla")
        powerRule = PublicRule("power",rule) #volutamente non ha un tag. Non ha senso scrivere solo il '^'
        #setattr section
        setattr(powerRule,'node_type',NODE_TYPE.INTERNO)
        setattr(powerRule,'request_new_layer',True)
        setattr(powerRule,'next_rules_trigger_words',None)
        setattr(powerRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(powerRule)
        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        self._body0 = text
        return self._ruleTemplate.format(self._body0)

    def getCursorOffsetForRulename(self,rulename): 
        """Data una certa regola, il modulo sapendo dov'è il cursore attualmente, può risalire a dove posizionarsi rispetto a dov'è"""
        return 0
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)




class Piu(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Piu.get_classname(),1)
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["più"]
    
    @staticmethod
    def createGrammar():
        rule = Literal("più")
        rule.tag = "+"
        plusRule = PublicRule("sum",rule)
        #setattr section
        setattr(plusRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(plusRule,'request_new_layer',False)
        setattr(plusRule,'next_rules_trigger_words',[])
        setattr(plusRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(plusRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        self._cursorPos = len(text) #dopo l'inserimento della stringa la posizione del cursore è alla fine della stessa
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)


class Per(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Per.get_classname(),2) #2 è la lunghezza massima per triggerare una entry_rule. La devo vedere io di volta in volta a seconda della grammatica
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["per","moltiplicato"] #esplicito quali sono i primi token di ogni expansione di ogni entry rule, almeno quando al layer arriva un toke nuovo del burst sa già vedere se inoltrare ai moduli o no

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
        setattr(multiplication_rule,'next_rules_trigger_words',[]) #tiene conto del grafo della grammatica. None se è foglia
        setattr(multiplication_rule,'is_entry_rule',True) #tiene conto se questa regola è un entry point di un grafo
        #grammar creation section
        g = Grammar()
        g.add_rule(multiplication_rule)

        return g
    
    @classmethod
    def get_classname(cls):
        return cls.__name__
    
    def createLatexText(self,text,rule_name=None):
        return '{}'.format(text)

    def getLatexAlternatives(self,last_token):
        super().getLatexAlternatives(last_token)


#funzione generatrice. Si chiamerà così in tutti i moduli per convenzione
def generateGrammars(answerPoolSetter):
    grammars = [Per(answerPoolSetter),Piu(answerPoolSetter)] #e a seguire nell'array creo un'istanza per classe nel modulo
    entryRuleWords = [{grammar.moduleName:grammar.entryRuleWords} for grammar in grammars] #entry rule words di tutte le grammatiche
    entryRuleWordsDict = {}
    for entryRuleWord in entryRuleWords:
        entryRuleWordsDict = {**entryRuleWordsDict,**entryRuleWord} #merge dictionaries
    return (grammars,entryRuleWordsDict)


