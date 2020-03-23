from math_modules.base_module import MathTopic
from jsgf import PublicRule, Literal, Grammar, AlternativeSet
from model.enums import NODE_TYPE
import pdb


class Seno(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Seno.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        #rule template (per regole complesse con filler). Le foglie come i simboli semplici non ce l'hanno
        self._ruleTemplate = '\sin{0}'
        self._body0 = ''
        self.entryRuleWords = ["seno","di"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
        self._lastRuleMatchedName = None #mi serve per sapere dov'è il cursore. soprattutto utile in caso in cui il comando sia spezzettato su più parentesi
        
    @staticmethod
    def createGrammar():
        rule = Literal("seno di")
        rule.tag = '\sin{}'
        sinRule = PublicRule("seno",rule)
        #setattr section
        setattr(sinRule,'node_type',NODE_TYPE.INTERNO)
        setattr(sinRule,'request_new_layer',True)
        setattr(sinRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(sinRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(sinRule)
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
        if rulename == 'seno':
            if calledFromLayer:
                return (1,True,None)
            else: #called from module
                return (5,True,None) #True perchè ho finito questa regola
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)


class Coseno(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Coseno.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        #rule template (per regole complesse con filler). Le foglie come i simboli semplici non ce l'hanno
        self._ruleTemplate = '\cos{0}'
        self._body0 = ''
        self.entryRuleWords = ["coseno","di"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
        self._lastRuleMatchedName = None #mi serve per sapere dov'è il cursore. soprattutto utile in caso in cui il comando sia spezzettato su più parentesi
        
    @staticmethod
    def createGrammar():
        rule = Literal("coseno di")
        rule.tag = '\cos{}'
        cosineRule = PublicRule("coseno",rule)
        #setattr section
        setattr(cosineRule,'node_type',NODE_TYPE.INTERNO)
        setattr(cosineRule,'request_new_layer',True)
        setattr(cosineRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(cosineRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(cosineRule)
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
        if rulename == 'coseno':
            if calledFromLayer:
                return (1,True,None)
            else: #called from module
                return (5,True,None) #True perchè ho finito questa regola
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)




class Tangente(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Tangente.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        #rule template (per regole complesse con filler). Le foglie come i simboli semplici non ce l'hanno
        self._ruleTemplate = '\\tan{0}'
        self._body0 = ''
        self.entryRuleWords = ["tangente","di"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
        self._lastRuleMatchedName = None #mi serve per sapere dov'è il cursore. soprattutto utile in caso in cui il comando sia spezzettato su più parentesi
        
    @staticmethod
    def createGrammar():
        rule = Literal("tangente di")
        rule.tag = '\\tan{}'
        tanRule = PublicRule("tangente",rule)
        #setattr section
        setattr(tanRule,'node_type',NODE_TYPE.INTERNO)
        setattr(tanRule,'request_new_layer',True)
        setattr(tanRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(tanRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(tanRule)
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
        if rulename == 'tangente':
            if calledFromLayer:
                return (1,True,None) #True sta per isEndingRule, il terzo parametro sta per la prossima regola metchata
            else: #called from module
                return (5,True,None) #True perchè ho finito questa regola
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)






#funzione generatrice. Si chiamerà così in tutti i moduli per convenzione
def generateGrammars(answerPoolSetter):
    grammars = [Seno(answerPoolSetter),
                Coseno(answerPoolSetter),
                Tangente(answerPoolSetter)] 
    entryRuleWords = [{grammar.moduleName:grammar.entryRuleWords} for grammar in grammars] #entry rule words di tutte le grammatiche
    entryRuleWordsDict = {}
    for entryRuleWord in entryRuleWords:
        entryRuleWordsDict = {**entryRuleWordsDict,**entryRuleWord} #merge dictionaries
    return (grammars,entryRuleWordsDict)