from notificationcenter import *
from math_modules import algebra,analysis,basic_symbols,trigonometry #genereremo dinamicamente i testi di questi import
import os
from model.enums import NotificationName


class Layer:
    
    """
    notification cbks
    """
    def onInputFromSrv(self,sender,notification_name,text_pos_info):
        """
        text_pos_info è una tupla (text,POS) dove POS è tra i valori predefiniti da Spacy
        """
        print("ricevuto input dal server {}".format(text_pos_info))
        if text_pos_info[0] == 'fine':
            self.endLayer()
            return
        #inoltro ai moduli
        self._notificationCenter.post_notification(sender=None,with_name=NotificationName.NEW_INPUT_FROM_LAYER.name,with_info=text_pos_info)

    def onInputFromModule(self,sender,notification_name,text_rule_info):
        """
        text_rule_info è una tupla (text,{'leaf':bool}) che porta
        un testo (può essere anche None) e un'informazione della regola che l'ha generato
        """
        print("ricevuto input dal modulo: {}".format(text_rule_info))
        self._response_count += 1
        self._modules_answers.append(text_rule_info)
        #TODO: continuare
        
    def onWaitFromModule(self,sender,notification_name,info):
        print("wait arrived dal modulo.")
        self._response_count += 1
        self._modules_answers.append()
        #TODO: continuare
    
    """
    notification registration/deregistration
    """
    def setObservers(self):
        self._observer_srv = self._notificationCenter.add_observer(with_block=self.onInputFromSrv, for_name=NotificationName.NEW_INPUT.name)
        self._observer_module_text = self._notificationCenter.add_observer(with_block=self.onInputFromModule, for_name=NotificationName.TXT_FOR_TEXSTUDIO_FOR_LAYER.name)
        self._observer_module_wait = self._notificationCenter.add_observer(with_block=self.onWaitFromModule, for_name=NotificationName.WAIT.name)
    
    def removeObservers(self):
        self._notificationCenter.remove_observer(self._observer_srv)
        self._notificationCenter.remove_observer(self._observer_module_text)
        self._notificationCenter.remove_observer(self._observer_module_wait)


    def __init__(self):
        self._notificationCenter = NotificationCenter()
        self.setObservers()
        self._response_count = 0 #contatore che permette al layer di fare da buffer tenendo il conto di quanti moduli gli hanno risposto
        #conto quanti moduli ci sono (tutti i moduli stanno in quella cartella e sono file .py). Prima di valutare che un messaggio possa essere mandato al srv response_count == module_count
        self._modules_count = len([name for name in os.listdir('./math_modules') if name[-2:] == "py" and name != 'base_module.py']) 
        for module in [algebra,analysis,basic_symbols,trigonometry]: #genereremo dinamicamente questo sorgente in fase di installazione..... perchè non si riesce ad iterare sui moduli
            module.generateGrammars()
        self._modules_answers = []




    def sendLatexTextToSrv(self,text):
        self._notificationCenter.post_notification(sender=None,with_name=NotificationName.TXT_FOR_TEXSTUDIO_FOR_SRV.name,with_info=text)
    
    def endLayer(self):
        self._notificationCenter.post_notification(sender=None,with_name=NotificationName.END_LAYER.name)
