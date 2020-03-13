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
        openParentesisRule = PublicRule("open_parenthesis",AlternativeSet(short_expansion,long_expansion))
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


#funzione generatrice. Si chiamerà così in tutti i moduli per convenzione
def generateGrammars(answerPoolSetter):
    grammars = [PiuMeno(answerPoolSetter)] 
    entryRuleWords = [{grammar.moduleName:grammar.entryRuleWords} for grammar in grammars] #entry rule words di tutte le grammatiche
    entryRuleWordsDict = {}
    for entryRuleWord in entryRuleWords:
        entryRuleWordsDict = {**entryRuleWordsDict,**entryRuleWord} #merge dictionaries
    return (grammars,entryRuleWordsDict)