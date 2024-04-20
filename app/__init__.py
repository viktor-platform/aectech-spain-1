from .my_folder.controller import Controller as MyFolder
from .my_entity_type.controller import Controller as MyEntityType

from viktor import InitialEntity

initial_entities = [
    InitialEntity('MyFolder', name='AEC Tech Project')
]
