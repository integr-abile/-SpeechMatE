from math_modules.base_module import MathTopic
from jsgf import PublicRule, Literal, Grammar, AlternativeSet
from model.enums import NODE_TYPE
import pdb

class Potenza(MathTopic):
    
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Potenza.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        #rule template (per regole complesse con filler). Le foglie come i simboli semplici non ce l'hanno
        self._ruleTemplate = '^{0}'
        self._body0 = ''
        self.entryRuleWords = ["alla"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
        self._lastRuleMatchedName = None #mi serve per sapere dov'è il cursore
        
    @staticmethod
    def createGrammar():
        rule = Literal("alla")
        rule.tag = '^{}'
        powerRule = PublicRule("power",rule) #volutamente non ha un tag. Non ha senso scrivere solo il '^'
        #setattr section
        setattr(powerRule,'node_type',NODE_TYPE.INTERNO)
        setattr(powerRule,'request_new_layer',True)
        setattr(powerRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(powerRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(powerRule)
        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rulename=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return self._ruleTemplate.format(self._body0)

    def updateStringFormat(self,text,rulename):
        self._body0 = text


    def getCursorOffsetForRulename(self,rulename,calledFromLayer=False): 
        """
        Data una certa regola, il modulo sapendo dov'è il cursore attualmente, può risalire a dove posizionarsi rispetto a dov'è
        è necessario specificare se la chiamata arriva dal layer oppure no perchè se arriva dal layer denota la fine del layer, se chiamata dal modulo l'inizio
        """
        # pdb.set_trace()
        if rulename is None: #se è None sono all'inizio del format
            return (2,True) #perchè deve passare i caratter '^' e '{'
        elif rulename == 'power': #vuol dire che col cursore sono al termine della scrittura del corpo della potenza
            if calledFromLayer:
                return (1,True,None)
            else:
                return(2,True,None)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)

class Uguale(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Uguale.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["uguale"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer

    @staticmethod
    def createGrammar():
        rule = Literal("uguale")
        rule.tag = "="
        equalRule = PublicRule("equal",rule)
        #setattr section
        setattr(equalRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(equalRule,'request_new_layer',False)
        setattr(equalRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(equalRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(equalRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)

class Diverso(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Diverso.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["diverso"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer

    @staticmethod
    def createGrammar():
        rule = Literal("diverso")
        rule.tag = "\\neq"
        neqRule = PublicRule("not_equal",rule)
        #setattr section
        setattr(neqRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(neqRule,'request_new_layer',False)
        setattr(neqRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(neqRule,'is_entry_rule',True)
        setattr(neqRule,'leaf_end_cursor_movement',1) #una foglia può specificare questo attributo per dire che dopo di lei il cursore deve muoversi di un tot (tipicamente per uno spazio)
        #grammar creation section
        g = Grammar()
        g.add_rule(neqRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)


class Minore(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Minore.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["minore"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer

    @staticmethod
    def createGrammar():
        rule = Literal("minore di")
        rule.tag = "<"
        lessThanRule = PublicRule("less_than",rule)
        #setattr section
        setattr(lessThanRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(lessThanRule,'request_new_layer',False)
        setattr(lessThanRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(lessThanRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(lessThanRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)




class Maggiore(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Minore.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["maggiore"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer

    @staticmethod
    def createGrammar():
        rule = Literal("maggiore di")
        rule.tag = ">"
        greaterThanRule = PublicRule("greater_than",rule)
        #setattr section
        setattr(greaterThanRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(greaterThanRule,'request_new_layer',False)
        setattr(greaterThanRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(greaterThanRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(greaterThanRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)






class ApertaParentesiTonda(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,ApertaParentesiTonda.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["aperta","apri","parentesi","tonda"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer

    @staticmethod
    def createGrammar():
        short_expansion = Literal("aperta tonda")
        short_expansion.tag = "("
        long_expansion = Literal("apri parentesi tonda")
        long_expansion.tag = "("
        long_expansion_2 = Literal("aperta parentesi tonda")
        long_expansion_2.tag = "("
        openParentesisRule = PublicRule("open_parenthesis",AlternativeSet(short_expansion,long_expansion,long_expansion_2))
        #setattr section
        setattr(openParentesisRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(openParentesisRule,'request_new_layer',False)
        setattr(openParentesisRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(openParentesisRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(openParentesisRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)








class ChiusaParentesiTonda(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,ChiusaParentesiTonda.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["chiusa","chiudi","tonda","parentesi"] #unione delle parole che triggerano entry rule (anche successive alla prima)
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer

    @staticmethod
    def createGrammar():
        short_expansion = Literal("chiusa tonda")
        short_expansion.tag = ")"
        long_expansion = Literal("chuidi parentesi tonda")
        long_expansion.tag = ")"
        long_expansion_2 = Literal("chiusa parentesi tonda")
        long_expansion_2.tag = ")"
        closeParentesisRule = PublicRule("close_parenthesis",AlternativeSet(short_expansion,long_expansion,long_expansion_2))
        #setattr section
        setattr(closeParentesisRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(closeParentesisRule,'request_new_layer',False)
        setattr(closeParentesisRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(closeParentesisRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(closeParentesisRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)





class ApertaParentesiQuadra(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,ApertaParentesiQuadra.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["aperta","apri","quadra","parentesi"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer

    @staticmethod
    def createGrammar():
        short_expansion = Literal("aperta quadra")
        short_expansion.tag = "["
        long_expansion = Literal("apri parentesi quadra")
        long_expansion.tag = "["
        long_expansion_2 = Literal("aperta parentesi quadra")
        long_expansion_2.tag = "["
        openSquareRule = PublicRule("open_square",AlternativeSet(short_expansion,long_expansion,long_expansion_2))
        #setattr section
        setattr(openSquareRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(openSquareRule,'request_new_layer',False)
        setattr(openSquareRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(openSquareRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(openSquareRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)






class ChiusaParentesiQuadra(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,ChiusaParentesiQuadra.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["chiusa","chiudi","quadra","parentesi"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer

    @staticmethod
    def createGrammar():
        short_expansion = Literal("chiusa quadra")
        short_expansion.tag = "]"
        long_expansion = Literal("chuidi parentesi quadra")
        long_expansion.tag = "]"
        long_expansion_2 = Literal("chiusa parentesi quadra")
        long_expansion_2.tag = "]"
        closeSquareRule = PublicRule("close_square",AlternativeSet(short_expansion,long_expansion,long_expansion_2))
        #setattr section
        setattr(closeSquareRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(closeSquareRule,'request_new_layer',False)
        setattr(closeSquareRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(closeSquareRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(closeSquareRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)







class ApertaParentesiGraffa(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,ApertaParentesiGraffa.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["aperta","apri","parentesi","graffa"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer

    @staticmethod
    def createGrammar():
        short_expansion = Literal("aperta graffa")
        short_expansion.tag = "{"
        long_expansion = Literal("apri parentesi graffa")
        long_expansion.tag = "{"
        long_expansion_2 = Literal("aperta parentesi graffa")
        long_expansion_2.tag = "{"
        openSquareRule = PublicRule("open_brace",AlternativeSet(short_expansion,long_expansion,long_expansion_2))
        #setattr section
        setattr(openSquareRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(openSquareRule,'request_new_layer',False)
        setattr(openSquareRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(openSquareRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(openSquareRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)






class ChiusaParentesiGraffa(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,ChiusaParentesiGraffa.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["chiusa","chiudi","parentesi","graffa"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer

    @staticmethod
    def createGrammar():
        short_expansion = Literal("chiusa graffa")
        short_expansion.tag = "}"
        long_expansion = Literal("chiudi parentesi graffa")
        long_expansion.tag = "}"
        long_expansion_2 = Literal("chiusa parentesi graffa")
        long_expansion_2.tag = "}"
        openSquareRule = PublicRule("close_brace",AlternativeSet(short_expansion,long_expansion,long_expansion_2))
        #setattr section
        setattr(openSquareRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(openSquareRule,'request_new_layer',False)
        setattr(openSquareRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(openSquareRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(openSquareRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)










class Meno(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Meno.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["meno"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer

    @staticmethod
    def createGrammar():
        rule = Literal("meno")
        rule.tag = "-"
        minusRule = PublicRule("sub",rule)
        #setattr section
        setattr(minusRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(minusRule,'request_new_layer',False)
        setattr(minusRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(minusRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(minusRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)



class Diviso(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Diviso.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["diviso"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer

    @staticmethod
    def createGrammar():
        rule = Literal("diviso")
        rule.tag = "\div"
        divideRule = PublicRule("divide",rule)
        #setattr section
        setattr(divideRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(divideRule,'request_new_layer',False)
        setattr(divideRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(divideRule,'is_entry_rule',True)
        setattr(divideRule,'leaf_end_cursor_movement',1) #una foglia può specificare questo attributo per dire che dopo di lei il cursore deve muoversi di un tot (tipicamente per uno spazio)
        #grammar creation section
        g = Grammar()
        g.add_rule(divideRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)




class Piu(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Piu.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["più"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
    
    @staticmethod
    def createGrammar():
        rule = Literal("più")
        rule.tag = "+"
        plusRule = PublicRule("sum",rule)
        #setattr section
        setattr(plusRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(plusRule,'request_new_layer',False)
        setattr(plusRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(plusRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(plusRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        self._cursorPos = len(text) #dopo l'inserimento della stringa la posizione del cursore è alla fine della stessa
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)





class Per(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Per.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["per","moltiplicato"] #esplicito quali sono i primi token di ogni expansione di ogni entry rule, almeno quando al layer arriva un toke nuovo del burst sa già vedere se inoltrare ai moduli o no
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer

    @staticmethod #mi permette di non mettere il self tra parentesi perchè non è un metodo di istanza
    def createGrammar():
        short_rule = Literal("per") #sto definendo un'expansion, non è una regola!!
        short_rule.tag = "\cdot" #il contributo di questa regola per il latex finale
        long_rule = Literal("moltiplicato per") #expansion
        long_rule.tag = "\cdot"
        multiplication_rule = PublicRule("multiplication",AlternativeSet(short_rule,long_rule)) #rule
        #setattr section (Per ogni rule 4 setattr)
        setattr(multiplication_rule,'node_type',NODE_TYPE.FOGLIA) #aggiungiamo un attributo type direttamente sull'oggetto PublicRule per connotarlo come nodo o attributo
        setattr(multiplication_rule,'request_new_layer',False) #tiene conto del fatto che il match di questa regola possa richiedere la creazione di un nuovo layer
        setattr(multiplication_rule,'next_rules_trigger_words',[]) #tiene conto del grafo della grammatica. Non mettere None se no salta tutto perchè None non è iterabile
        setattr(multiplication_rule,'is_entry_rule',True) #tiene conto se questa regola è un entry point di un grafo
        setattr(multiplication_rule,'leaf_end_cursor_movement',1) #una foglia può specificare questo attributo per dire che dopo di lei il cursore deve muoversi di un tot (tipicamente per uno spazio)
        #grammar creation section
        g = Grammar()
        g.add_rule(multiplication_rule)

        return g
    
    @classmethod
    def get_classname(cls):
        return cls.__name__
    
    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return '{}'.format(text)

    def getLatexAlternatives(self,last_token):
        super().getLatexAlternatives(last_token)


#funzione generatrice. Si chiamerà così in tutti i moduli per convenzione
def generateGrammars(answerPoolSetter):
    grammars = [Per(answerPoolSetter),
                Piu(answerPoolSetter),
                Meno(answerPoolSetter),
                Diviso(answerPoolSetter),
                Potenza(answerPoolSetter),
                Uguale(answerPoolSetter),
                Diverso(answerPoolSetter),
                Minore(answerPoolSetter),
                Maggiore(answerPoolSetter),
                ApertaParentesiTonda(answerPoolSetter),
                ApertaParentesiQuadra(answerPoolSetter),
                ApertaParentesiGraffa(answerPoolSetter),
                ChiusaParentesiTonda(answerPoolSetter),
                ChiusaParentesiQuadra(answerPoolSetter),
                ChiusaParentesiGraffa(answerPoolSetter)] 
    entryRuleWords = [{grammar.moduleName:grammar.entryRuleWords} for grammar in grammars] #entry rule words di tutte le grammatiche
    entryRuleWordsDict = {}
    for entryRuleWord in entryRuleWords:
        entryRuleWordsDict = {**entryRuleWordsDict,**entryRuleWord} #merge dictionaries
    return (grammars,entryRuleWordsDict)


