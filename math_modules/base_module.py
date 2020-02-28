from notificationcenter import *
from model.enums import NotificationName

class MathTopic:

    def onInput(self,sender,notification_name,last_token):
        print("notification ok")
    
    
    def __init__(self):
        self._notificationCenter = NotificationCenter()
        self._observer_layer = self._notificationCenter.add_observer(with_block=self.onInput, for_name=NotificationName.NEW_INPUT_FROM_LAYER.name)

    def sendLatexText(self,text,node_type_info):
        """node_type_info è un dizionario {'leaf':bool} o None che specifica se la regola triggerata è una foglia oppure no"""
        self._notificationCenter.post_notification(sender=None,with_name=NotificationName.TXT_FOR_TEXSTUDIO_FOR_LAYER.name,with_info=(text,node_type_info))

    def postNewLayerRequest(self):
        self._notificationCenter.post_notification(sender=None,with_name=NotificationName.NEW_LAYER_REQUEST.name)
        

    
