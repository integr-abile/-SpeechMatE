from math_modules.base_module import MathTopic
from jsgf import PublicRule, Literal, Grammar, AlternativeSet
from model.enums import NODE_TYPE
import pdb

class PiuMeno(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,PiuMeno.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["più","o","meno"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer

    @staticmethod
    def createGrammar():
        short_expansion = Literal("più meno")
        short_expansion.tag = "\pm"
        long_expansion = Literal("più o meno")
        long_expansion.tag = "\pm"
        piuMenoRule = PublicRule("open_parenthesis",AlternativeSet(short_expansion,long_expansion))
        #setattr section
        setattr(piuMenoRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(piuMenoRule,'request_new_layer',False)
        setattr(piuMenoRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(piuMenoRule,'is_entry_rule',True)
        setattr(piuMenoRule,'leaf_end_cursor_movement',1) #una foglia può specificare questo attributo per dire che dopo di lei il cursore deve muoversi di un tot (tipicamente per uno spazio)
        #grammar creation section
        g = Grammar()
        g.add_rule(piuMenoRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)





class Integrale(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Integrale.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        self.entryRuleWords = ["integrale"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer

    @staticmethod
    def createGrammar():
        short_expansion = Literal("integrale")
        short_expansion.tag = "\int"
        integralRule = PublicRule("integral",short_expansion)
        #setattr section
        setattr(integralRule,'node_type',NODE_TYPE.FOGLIA)
        setattr(integralRule,'request_new_layer',False)
        setattr(integralRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(integralRule,'is_entry_rule',True)
        setattr(integralRule,'leaf_end_cursor_movement',1) #una foglia può specificare questo attributo per dire che dopo di lei il cursore deve muoversi di un tot (tipicamente per uno spazio)
        #grammar creation section
        g = Grammar()
        g.add_rule(integralRule)

        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rule_name=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return '{}'.format(text)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)
        






class Pedice(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Pedice.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        #rule template (per regole complesse con filler). Le foglie come i simboli semplici non ce l'hanno
        self._ruleTemplate = '_{0}'
        self._body0 = ''
        self.entryRuleWords = ["pedice","sub"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
        self._lastRuleMatchedName = None #mi serve per sapere dov'è il cursore. soprattutto utile in caso in cui il comando sia spezzettato su più parentesi
        
    @staticmethod
    def createGrammar():
        rule = Literal("pedice")
        rule.tag = '_{}'
        alternative_rule = Literal("sub")
        alternative_rule.tag = '_{}'
        subscriptRule = PublicRule("subscript",AlternativeSet(rule,alternative_rule)) #volutamente non ha un tag. Non ha senso scrivere solo il '^'
        #setattr section
        setattr(subscriptRule,'node_type',NODE_TYPE.INTERNO)
        setattr(subscriptRule,'request_new_layer',True)
        setattr(subscriptRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(subscriptRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(subscriptRule)
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
        if rulename == 'subscript': #sia all'inizio che alla fine del comando vado avanti di 2 caratteri per via della struttura del comando stesso perchè deve passare i caratter '_' e '{'
            return (2,True) #questa regola è giunta al capolinea
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)






class ValoreAssoluto(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,ValoreAssoluto.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        #rule template (per regole complesse con filler). Le foglie come i simboli semplici non ce l'hanno
        self._ruleTemplate = '|{0}|'
        self._body0 = ''
        self.entryRuleWords = ["valore","assoluto","di"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
        self._lastRuleMatchedName = None #mi serve per sapere dov'è il cursore. soprattutto utile in caso in cui il comando sia spezzettato su più parentesi
        
    @staticmethod
    def createGrammar():
        rule = Literal("valore assoluto di")
        rule.tag = '||'
        absoluteValueRule = PublicRule("absolute_value",rule) 
        #setattr section
        setattr(absoluteValueRule,'node_type',NODE_TYPE.INTERNO) #vuol dire che si dovrà terminare con una foglia
        setattr(absoluteValueRule,'request_new_layer',True)
        setattr(absoluteValueRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(absoluteValueRule,'is_entry_rule',True)
        #grammar creation section
        g = Grammar()
        g.add_rule(absoluteValueRule)
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
        if rulename == 'absolute_value':
            if calledFromLayer:
                return (1,True) #True sta per ending rule
            else:
                return (1,True)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)






class Frazione(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Frazione.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        #rule template (per regole complesse con filler). Le foglie come i simboli semplici non ce l'hanno
        self._ruleTemplate = '\\frac{0}{1}'
        self._body0 = ''
        self._body1 = ''
        self.entryRuleWords = ["frazione"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
        self._lastRuleMatchedName = None #mi serve per sapere dov'è il cursore. soprattutto utile in caso in cui il comando sia spezzettato su più parentesi
        
    @staticmethod
    def createGrammar():
        fracExpansion = Literal("frazione")
        fracExpansion.tag = '\\frac{}{}'
        fracRule = PublicRule("fraction_main",fracExpansion) 
        numeratorExpansion = Literal("frazione numeratore")
        numeratorExpansion.tag = None
        numeratorRule = PublicRule("fraction_numerator",numeratorExpansion)
        denominatorExpansion = Literal("frazione numeratore denominatore")
        denominatorExpansion.tag = None
        denominatorRule = PublicRule("fraction_denominator",denominatorExpansion)
        #setattr section
        setattr(fracRule,'node_type',NODE_TYPE.INTERNO)
        setattr(fracRule,'request_new_layer',False)
        setattr(fracRule,'next_rules_trigger_words',['numeratore']) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(fracRule,'is_entry_rule',True)
        #-------------------
        setattr(numeratorRule,'node_type',NODE_TYPE.INTERNO)
        setattr(numeratorRule,'request_new_layer',True)
        setattr(numeratorRule,'next_rules_trigger_words',['denominatore']) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(numeratorRule,'is_entry_rule',False)
        setattr(numeratorRule,'go_to_begin',len('\\frac{}{}')) #attributo che specifica se fare carry-home.
        #------------------------
        setattr(denominatorRule,'node_type',NODE_TYPE.INTERNO)
        setattr(denominatorRule,'request_new_layer',True)
        setattr(denominatorRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(denominatorRule,'is_entry_rule',False)
        #grammar creation section
        g = Grammar()
        g.add_rules(fracRule,numeratorRule,denominatorRule)
        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rulename=None):
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return self._ruleTemplate.format(self._body0,self._body1)

    def updateStringFormat(self,text,rulename):
        if rulename == 'fraction_numerator':
            self._body0 = text
        elif rulename == 'fraction_denominator':
            self._body1 = text


    def getCursorOffsetForRulename(self,rulename,calledFromLayer=False): 
        """
        Data una certa regola, il modulo sapendo dov'è il cursore attualmente, può risalire a dove posizionarsi rispetto a dov'è
        è necessario specificare se la chiamata arriva dal layer oppure no perchè se arriva dal layer denota la fine del layer, se chiamata dal modulo l'inizio
        """
        if rulename == 'fraction_numerator':
            if not calledFromLayer:
                return (6,False,None)
            else: 
                return(2,False,self._g.get_rule_from_name("fraction_denominator")) #ritorno la regola successiva della catena
        elif rulename == 'fraction_denominator':
            if not calledFromLayer:
                return (0,True,None) 
            else:
                return(1,True,None)
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)





class IntegraleDefinito(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,IntegraleDefinito.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        #rule template (per regole complesse con filler). Le foglie come i simboli semplici non ce l'hanno
        self._ruleTemplate = '\\int\\limits_{0}^{1}'
        self._body0 = ''
        self._body1 = ''
        self.entryRuleWords = ["integrale","da"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
        self._lastRuleMatchedName = None #mi serve per sapere dov'è il cursore. soprattutto utile in caso in cui il comando sia spezzettato su più parentesi
        
    @staticmethod
    def createGrammar():
        integraleDefinitoExpansion = Literal("integrale da")
        integraleDefinitoExpansion.tag = "\\int\\limits_{}^{}"
        definedIntegralRule = PublicRule("defined_integral_main",integraleDefinitoExpansion)
        integraleDefinitoUpLimitExpansion = Literal("integrale da a")
        integraleDefinitoUpLimitExpansion.tag = None
        upLimitRule = PublicRule("defined_integral_limit",integraleDefinitoUpLimitExpansion)
        #setattr section
        setattr(definedIntegralRule,'node_type',NODE_TYPE.INTERNO)
        setattr(definedIntegralRule,'request_new_layer',True)
        setattr(definedIntegralRule,'next_rules_trigger_words',['a']) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(definedIntegralRule,'is_entry_rule',True)
        setattr(definedIntegralRule,'go_to_begin',len('\\int\\limits_{}^{}')) #attributo che specifica se fare carry-home.
        #------------------------------
        setattr(upLimitRule,'node_type',NODE_TYPE.INTERNO)
        setattr(upLimitRule,'request_new_layer',True)
        setattr(upLimitRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(upLimitRule,'is_entry_rule',False)

        #grammar creation section
        g = Grammar()
        g.add_rules(definedIntegralRule,upLimitRule)
        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rulename=None):
        #tanto non lo uso.. da togliere nel refactoring. non importa se è sbagliato
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return self._ruleTemplate.format(self._body0,self._body1)

    def updateStringFormat(self,text,rulename):
        #tanto non lo uso.. da togliere nel refactoring. non importa se è sbagliato
        if rulename == 'fraction_numerator':
            self._body0 = text
        elif rulename == 'fraction_denominator':
            self._body1 = text


    def getCursorOffsetForRulename(self,rulename,calledFromLayer=False): 
        """
        Data una certa regola, il modulo sapendo dov'è il cursore attualmente, può risalire a dove posizionarsi rispetto a dov'è
        è necessario specificare se la chiamata arriva dal layer oppure no perchè se arriva dal layer denota la fine del layer, se chiamata dal modulo l'inizio
        """
        if rulename == 'defined_integral_main':
            if not calledFromLayer: #called from module
                return (13,False,None)
            else: 
                return(3,False,self._g.get_rule_from_name("defined_integral_limit")) #ritorno la regola successiva della catena
        elif rulename == 'defined_integral_limit':
            if not calledFromLayer:
                return (0,True,None) 
            else:
                return(1,True,None) #per uscire dall'upper limit dell'integrale
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)






class Sommatoria(MathTopic):
    def __init__(self,answerPoolSetter):
        super().__init__(answerPoolSetter,Sommatoria.get_classname())
        self._g = self.createGrammar()
        self._cursorPos = 0
        #rule template (per regole complesse con filler). Le foglie come i simboli semplici non ce l'hanno
        self._ruleTemplate = '\\sum_{0}^{1}'
        self._body0 = ''
        self._body1 = ''
        self.entryRuleWords = ["sommatoria"]
        self._nextRulesWords = self.entryRuleWords #poi questa variabile cambierà restando allineata con quella che ha anche il layer
        self._lastRuleMatchedName = None #mi serve per sapere dov'è il cursore. soprattutto utile in caso in cui il comando sia spezzettato su più parentesi
        
    @staticmethod
    def createGrammar():
        sommatoriaExpansion = Literal("sommatoria")
        sommatoriaExpansion.tag = '\\sum_{}^{}'
        sommatoriaRule = PublicRule("sommatoria_main",sommatoriaExpansion)
        indexExpansion = Literal("sommatoria da")
        indexExpansion.tag = None
        indexRule = PublicRule("summation_index",indexExpansion)
        intervalExpansion = Literal("sommatoria da a")
        intervalExpansion.tag = None
        intervalRule = PublicRule("summation_interval",intervalExpansion)
        #setattr section
        setattr(sommatoriaRule,'node_type',NODE_TYPE.INTERNO)
        setattr(sommatoriaRule,'request_new_layer',False)
        setattr(sommatoriaRule,'next_rules_trigger_words',['da']) 
        setattr(sommatoriaRule,'is_entry_rule',True)
        #-------------------------
        setattr(indexRule,'node_type',NODE_TYPE.INTERNO)
        setattr(indexRule,'request_new_layer',True)
        setattr(indexRule,'next_rules_trigger_words',['a'])
        setattr(indexRule,'is_entry_rule',False)
        setattr(indexRule,'go_to_begin',len('\\sum_{}^{}')) #attributo che specifica se fare carry-home.
        #-------------------------------
        setattr(intervalRule,'node_type',NODE_TYPE.INTERNO)
        setattr(intervalRule,'request_new_layer',True)
        setattr(intervalRule,'next_rules_trigger_words',[]) #non mettere None se no salta tutto perchè None non è iterabile
        setattr(intervalRule,'is_entry_rule',False)

        #grammar creation section
        g = Grammar()
        g.add_rules(sommatoriaRule,indexRule,intervalRule)
        return g

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def createLatexText(self,text,rulename=None):
        #tanto non lo uso.. da togliere nel refactoring. non importa se è sbagliato
        """Nei comandi lunghi so come interpretare text in base ai comandi già passati"""
        return self._ruleTemplate.format(self._body0,self._body1)

    def updateStringFormat(self,text,rulename):
        #tanto non lo uso.. da togliere nel refactoring. non importa se è sbagliato
        if rulename == 'fraction_numerator':
            self._body0 = text
        elif rulename == 'fraction_denominator':
            self._body1 = text


    def getCursorOffsetForRulename(self,rulename,calledFromLayer=False): 
        """
        Data una certa regola, il modulo sapendo dov'è il cursore attualmente, può risalire a dove posizionarsi rispetto a dov'è
        è necessario specificare se la chiamata arriva dal layer oppure no perchè se arriva dal layer denota la fine del layer, se chiamata dal modulo l'inizio
        """
        if rulename == 'summation_index':
            if not calledFromLayer:
                return (6,False,None)
            else: 
                return(3,False,self._g.get_rule_from_name("summation_interval")) #ritorno la regola successiva della catena
        elif rulename == 'summation_interval':
            if not calledFromLayer:
                return (0,True,None) 
            else:
                return(1,True,None) #per uscire dalla sommatoria
    
    def getLatexAlternatives(self, last_token):
        return super().getLatexAlternatives(last_token)






#funzione generatrice. Si chiamerà così in tutti i moduli per convenzione
def generateGrammars(answerPoolSetter):
    grammars = [PiuMeno(answerPoolSetter),
                Pedice(answerPoolSetter),
                Frazione(answerPoolSetter),
                ValoreAssoluto(answerPoolSetter),
                Sommatoria(answerPoolSetter),
                Integrale(answerPoolSetter),
                IntegraleDefinito(answerPoolSetter)] 
    entryRuleWords = [{grammar.moduleName:grammar.entryRuleWords} for grammar in grammars] #entry rule words di tutte le grammatiche
    entryRuleWordsDict = {}
    for entryRuleWord in entryRuleWords:
        entryRuleWordsDict = {**entryRuleWordsDict,**entryRuleWord} #merge dictionaries
    return (grammars,entryRuleWordsDict)


