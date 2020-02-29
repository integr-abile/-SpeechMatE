from enum import Enum

class Action(Enum):
    NESSUNA = 0
    DETTATURA = 1

class NODE_TYPE(Enum):
    INTERNO = 0
    FOGLIA = 1

class LayerMsg(Enum):
    NEW_LAYER_REQUEST = 0 #forward da ModuleMsg
    END_THIS_LAYER = 1
    END_THIS_LAYER_WITH_TEXT = 2 #quando hanno dato tutti una risposta e sono tutti foglie
    TEXT = 3
    WAIT = 4 #quando uno o più moduli gli hanno risposto Wait

class ModuleMsg(Enum):
    TEXT = 0
    NEW_LAYER_REQUEST = 1
    WAIT = 2
    
