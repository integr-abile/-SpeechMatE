from notificationcenter import *

class MathTopic:

    def onInput(self,sender,notification_name,last_token):
        print("notification ok")
    
    
    def __init__(self):
        self._notificationCenter = NotificationCenter()
        self._observer_srv = self._notificationCenter.add_observer(with_block=self.onInput, for_name="new_input")

    def sendLatexText(self,text):
        self._notificationCenter.post_notification(sender=None,with_name="txt4texstudio",with_info=text)
        

    
