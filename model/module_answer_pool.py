from queue import Queue
from typing import Dict, Tuple
from model.enums import ModuleMsg

class ModuleAnswersPool(Queue): #wrapper ad una coda che è una struttura dati thread safe

    def popMessage(self):
        return self.get()

    def addMessage(self,msg_info):
        return self.put(msg_info)
