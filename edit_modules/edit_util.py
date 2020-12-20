import json
import pdb

def convertCommandsToTree(commandsDict):
    commands = commandsDict['commands']
    res = map(convert2ArrayOfDicts,commands)
    lst = list(res)
    max_sentence_len = max([len(elem) for elem in lst])
    toReturn = [[] for i in range(max_sentence_len)]
    for sentenceList in lst:
        for tokenDict in sentenceList:
            toReturn[int(tokenDict['idx'])].append(tokenDict)
    return toReturn
    
def convert2ArrayOfDicts(sentence):
    tokens = sentence.split()
    toReturn = []
    for idx,token in enumerate(tokens):
        toReturn.append({'idx':idx,'leaf':idx==len(tokens)-1,'token':token})
    return toReturn

def convertCorrspondencesToString():
    with open('./json/correspondences.json') as correspondences_json:
        correspondencesDict = json.load(correspondences_json)
        toReturn = ""
        for correspondence in correspondencesDict:
            toReturn += '{}{};'.format(correspondence["open_symbol"],correspondence["close_symbol"])
        return toReturn[:-1] #tolgo ; finale