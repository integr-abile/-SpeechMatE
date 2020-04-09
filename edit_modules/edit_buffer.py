import pdb
from model.enums import EditMsg

class EditBuffer: #classe delegata a tenere lo stao dell'editing
    def __init__(self,graph):
        self.graph = graph #albero di indici e parole
        self.resetState() 
        

    def newToken(self,token,isLastOfBurst):
        print('EDIT new token -> {}'.format(token))
        # pdb.set_trace()
        possibleSpecialSymbolsForCurIdx = self.possibleSpecialSymbolsForIdx(self.curIdx)
        if token not in self.tokensOfIdx(self.curIdx) and not self.isTokenBelongToSpecialSymbol(token,possibleSpecialSymbolsForCurIdx):
            if self.lastLeafStr != "":
                msg = (EditMsg.RETRY,self.lastLeafStr.strip())
                self.resetState()
                return msg
            self.resetState()
            return (EditMsg.NEXT_TOKEN,None)
        #qua arrivo se il token che è arrivato è accettabile
        self.cumulativeStr += " {}".format(token)
        matchedNodes = self.nodesOfIdxMatchingToken(token,self.curIdx,possibleSpecialSymbolsForCurIdx)
        if self.areNodesAllLeaves(matchedNodes):
            self.lastLeafStr = self.cumulativeStr
            msg = (EditMsg.COMMAND,self.lastLeafStr.strip())
            self.resetState()
            return msg
        if self.isAtLeastOneLeafPresent(matchedNodes):
            self.lastLeafStr = self.cumulativeStr
            if isLastOfBurst or self.curIdx == len(self.graph)-1: #controllo necessario perchè limito un comando di editing al burst corrente o cmq non posso permettere overflow dal grafo
                msg = (EditMsg.COMMAND,self.lastLeafStr.strip())
                self.resetState()
                return msg
        if isLastOfBurst or self.curIdx == len(self.graph)-1: #potrebbe essere che con questo token non abbia metchato nessuna foglia e sia arrivato a fine grafo
            msg = (EditMsg.COMMAND,self.lastLeafStr.strip()) if self.lastLeafStr != "" else (EditMsg.NEXT_TOKEN,None)
            self.resetState()
            return msg
        self.curIdx += 1
        return (EditMsg.WAIT,None)

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

    def possibleSpecialSymbolsForIdx(self,idx):
        return set(list(map(lambda tokenDict:tokenDict['token'] if tokenDict['token'][0] == '_' else "",self.graph[idx]))) #i comandi speciali per convenzione cominciano con _

    def isTokenBelongToSpecialSymbol(self,token,possibleSpecialSymbolsForCurIdx):
        if token.isdigit():
            if '_num' in possibleSpecialSymbolsForCurIdx: #per ora come simbolo speciale abbiamo solo numeri
                return True
        return False


    def nodesOfIdxMatchingToken(self,token,idx,possibleSpecialSymbolsForCurIdx):
        matchingNodes = []
        for tokenDict in self.graph[idx]:
            if tokenDict['token'] == token or self.isTokenBelongToSpecialSymbol(token,possibleSpecialSymbolsForCurIdx):
                matchingNodes.append(tokenDict)
        return matchingNodes

    def isAtLeastOneLeafPresent(self,nodes):
        return any(list(map(lambda tokenDict:tokenDict['leaf'],nodes)))

    def areNodesAllLeaves(self,nodes):
        return all(list(map(lambda tokenDict:tokenDict['leaf'],nodes)))
    
