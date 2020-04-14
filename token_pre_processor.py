import spacy
import json

class TokenPreProcessor:
    def __init__(self):
        with open('./util/macro_expansions.json') as macro_expansions_json:
            self.macroExpansionDict = json.load(macro_expansions_json)
        with open('./util/derivata_word2num.json') as derivata_word2num_json:
            self.derivataWord2numDict = json.load(derivata_word2num_json)

    def expandBurstIfNeeded(self,text_burst):
        toReturn = []
        for token in text_burst: #text_burst viene da spacy direttamente
            if token.text in self.macroExpansionDict.keys():
                expansion_tokens = self.macroExpansionDict[token.text]
                for expansion_token in expansion_tokens:
                    toReturn.append({'token':expansion_token,'pos':'NA'})
            elif token.text in self.derivataWord2numDict.keys():
                toReturn.append({'token':self.derivataWord2numDict[token.text],'pos':'ADJ'})
            else:
                toReturn.append({'token':token.text,'pos':token.pos_})
        return toReturn
