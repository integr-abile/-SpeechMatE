from queue import Queue
from typing import Dict, Tuple
from model.enums import ModuleMsg

class ModuleAnswersPool(Queue):

    def popMessage(self):
        return self.get()

    def addMessage(self,msg_info):
        return self.put(msg_info)
