from math_modules import algebra,analysis,basic_symbols,trigonometry #genereremo dinamicamente i testi di questi import
import os
from model.enums import LayerMsg
from model.module_answer_pool import ModuleAnswersPool
import concurrent.futures
from typing import Tuple


class Layer:
    
    def handleRawText(self,text_pos):
        """Chiamata token per token e token per token deve rispondere"""
        print("LAYER: ricevuto input dal server {}".format(text_pos))
        if text_pos[0] == 'fine':
            return (LayerMsg.END_THIS_LAYER,None)
        #inoltro ai moduli con la creazione dei thread e rispondo solo quando hanno finito tutti (ThreadPoolExecutor)
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self._allGrammars)) as executor:
            for grammar in self._allGrammars:
                executor.submit(grammar.getLatexAlternatives,text_pos)
        #guardo la struttura dati condivisa per fare le mie valutazioni
        print("LAYER: ora che hanno finito tutti i thread guardo cosa mi hanno risposto")
        answers = []
        while self._answersPool.empty() is False:
            answers.append(self._answersPool.popMessage())
        print(answers)
        return (LayerMsg.TEXT,"wow")

    
    def __init__(self):
        self._answersPool = ModuleAnswersPool()
        self._allGrammars = []
        for module in [algebra,analysis,basic_symbols,trigonometry]: #genereremo dinamicamente questo sorgente in fase di installazione..... perchè non si riesce ad iterare sui moduli
            self._allGrammars.append(module.generateGrammars(self._answersPool.addMessage))
        self._allGrammars = [grammar for lst in self._allGrammars for grammar in lst] #flatten
        
