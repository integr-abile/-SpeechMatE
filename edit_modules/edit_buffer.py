import pdb
from model.enums import EditMsg

class EditBuffer: #classe delegata a tenere lo stao dell'editing
    def __init__(self,graph):
        self.graph = graph #albero di indici e parole
        self.resetState() 

    def newToken(self,token,isLatOfBurst):
        print('EDIT new token -> {}'.format(token))
        if token not in self.tokensOfIdx(self.curIdx):
            if self.lastLeafStr != "":
                self.resetState()
                return (EditMsg.RETRY,self.lastLeafStr)
            self.resetState()
            return (EditMsg.NEXT_TOKEN)
        #qua arrivo se il token che è arrivato è accettabile


    def resetState(self):
        self.curIdx = 0 #tiene traccia di dove siamo arrivati nella dettatura
        self.cumulativeStr = "" #tutto quello che nel burst è stato ricevuto
        self.lastLeafStr = "" #stato della stringa cumulativa all'ultima foglia metchata

    def tokensOfIdx(self,idx):
        words = []
        for tokenDict in self.graph[idx]:
            words.append(tokenDict['token'])
        print('words {}'.format(set(words)))
        return set(words)
    
