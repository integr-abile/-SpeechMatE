from enum import Enum

class Action(Enum):
    NESSUNA = 0
    DETTATURA = 1

class NODE_TYPE(Enum):
    INTERNO = 0
    FOGLIA = 1

class NotificationName(Enum):
    NEW_INPUT = 0
    NEW_INPUT_FROM_LAYER = 1
    NEW_LAYER_REQUEST = 2
    TXT_FOR_TEXSTUDIO_FOR_LAYER = 3
    TXT_FOR_TEXSTUDIO_FOR_SRV = 4
    WAIT = 5
    END_LAYER = 6
