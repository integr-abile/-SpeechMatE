from math_modules import algebra,analysis,basic_symbols,trigonometry,letters #genereremo dinamicamente i testi di questi import
from model.module_answer_pool import ModuleAnswersPool
from model.enums import ModuleMsg
import concurrent.futures
from typing import Tuple
import pdb

class RuleTouchedLayer:
    def __init__(self):
        self.initAll()
        

    def initAll(self):
        self._answersPool = ModuleAnswersPool()
        self._allGrammars = []
        for module in [algebra,analysis,basic_symbols,trigonometry,letters]: #genereremo dinamicamente questo sorgente in fase di installazione..... perchè non si riesce ad iterare sui moduli
            moduleGrammar = module.generateGrammars(self._answersPool.addMessage)
            self._allGrammars.append(moduleGrammar[0]) #[0] è la grammatica vera e propria
        self._allGrammars = [grammar for lst in self._allGrammars for grammar in lst] #flatten
        self.grammarTouched = set()

    def checkRuleReached(self,text_pos):
        #-------------------------- MATCHING RULES ------------------------------------------
        
        #inoltro ai moduli con la creazione dei thread e rispondo solo quando hanno finito tutti (ThreadPoolExecutor). Ognuno popola la struttura dati condivisa
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self._allGrammars)) as executor:
            for grammar in self._allGrammars:
                executor.submit(grammar.getLatexAlternatives,text_pos)
        while self._answersPool.empty() is False:
            msg = self._answersPool.popMessage()
            # pdb.set_trace()
            if msg[0] is not ModuleMsg.OUT_OF_PLAY:
                self.grammarTouched.add(msg[3]) #3 è l'indice che corrisponde al nome della grammatica nei ModuleMsg
        return self.grammarTouched


    ##################### NON DISPONIBILI IN QUESTO TIPO DI LAYER ###################################
    def handleRawText(self,text_pos,idx,num_burst_tokens):
        pass

    def updateGrammarStringFormat(self,text,grammarName,rulename):
        pass

    def redirectRuleToSrv(self,rule, grammar_name, cursor_offset):
        pass