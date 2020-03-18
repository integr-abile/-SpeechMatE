from math_modules.base_module import MathTopic
from jsgf import PublicRule, Literal, Grammar, AlternativeSet
from model.enums import NODE_TYPE
import pdb


class Alpha(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Alpha.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["alfa"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
    
    @staticmethod
    def createGrammar():
        rule = Literal("alfa")
        rule.tag = "\\alpha"
        alphaRule = PublicRule("alpha",rule)
        #setattr section
        setattr(alphaRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(alphaRule,'request_new_layer',False)
        setattr(alphaRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(alphaRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(alphaRule)

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









class Beta(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Beta.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["beta"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
    
    @staticmethod
    def createGrammar():
        rule = Literal("beta")
        rule.tag = "\\beta"
        betaRule = PublicRule("beta",rule)
        #setattr section
        setattr(betaRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(betaRule,'request_new_layer',False)
        setattr(betaRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(betaRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(betaRule)

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






class Gamma(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Gamma.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["gamma"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
    
    @staticmethod
    def createGrammar():
        rule = Literal("gamma")
        rule.tag = "\\gamma"
        gammaRule = PublicRule("gamma",rule)
        #setattr section
        setattr(gammaRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(gammaRule,'request_new_layer',False)
        setattr(gammaRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(gammaRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(gammaRule)

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








class Delta(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Delta.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["delta"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
    
    @staticmethod
    def createGrammar():
        rule = Literal("delta")
        rule.tag = "\\delta"
        deltaRule = PublicRule("delta",rule)
        #setattr section
        setattr(deltaRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(deltaRule,'request_new_layer',False)
        setattr(deltaRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(deltaRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(deltaRule)

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





class DeltaMaiusc(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,DeltaMaiusc.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["delta","grande"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
    
    @staticmethod
    def createGrammar():
        rule = Literal("delta grande")
        rule.tag = "\\Delta"
        deltaBigRule = PublicRule("delta_big",rule)
        #setattr section
        setattr(deltaBigRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(deltaBigRule,'request_new_layer',False)
        setattr(deltaBigRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(deltaBigRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(deltaBigRule)

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








class Epsilon(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Epsilon.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["epsilon"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
    
    @staticmethod
    def createGrammar():
        rule = Literal("epsilon")
        rule.tag = "\\varepsilon"
        epsilonRule = PublicRule("epsilon",rule)
        #setattr section
        setattr(epsilonRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(epsilonRule,'request_new_layer',False)
        setattr(epsilonRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(epsilonRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(epsilonRule)

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







class Lambda(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Lambda.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["lambda"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
    
    @staticmethod
    def createGrammar():
        rule = Literal("lambda")
        rule.tag = "\\lambda"
        lambdaRule = PublicRule("lambda",rule)
        #setattr section
        setattr(lambdaRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(lambdaRule,'request_new_layer',False)
        setattr(lambdaRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(lambdaRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(lambdaRule)

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








class PiGreco(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,PiGreco.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["pi","greco","pigreco"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
    
    @staticmethod
    def createGrammar():
        rule = Literal("pi greco")
        rule.tag = "\\pi"
        alternative_rule = Literal("pigreco")
        alternative_rule.tag = "\\pi"
        alternative_rule2 = Literal("p greco")
        alternative_rule2.tag = "\\pi"
        piGrecoRule = PublicRule("pi-greco",AlternativeSet(rule,alternative_rule,alternative_rule2))
        #setattr section
        setattr(piGrecoRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(piGrecoRule,'request_new_layer',False)
        setattr(piGrecoRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(piGrecoRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(piGrecoRule)

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






#funzione generatrice. Si chiamerà così in tutti i moduli per convenzione
def generateGrammars(answerPoolSetter):
    grammars = [Alpha(answerPoolSetter),
                Beta(answerPoolSetter),
                Gamma(answerPoolSetter),
                Delta(answerPoolSetter),
                DeltaMaiusc(answerPoolSetter),
                Epsilon(answerPoolSetter),
                Lambda(answerPoolSetter),
                PiGreco(answerPoolSetter)] 
    entryRuleWords = [{grammar.moduleName:grammar.entryRuleWords} for grammar in grammars] #entry rule words di tutte le grammatiche
    entryRuleWordsDict = {}
    for entryRuleWord in entryRuleWords:
        entryRuleWordsDict = {**entryRuleWordsDict,**entryRuleWord} #merge dictionaries
    return (grammars,entryRuleWordsDict)