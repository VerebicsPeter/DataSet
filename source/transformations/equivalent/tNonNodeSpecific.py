# Implementations of non node specific or trivial transformations

# TODO: insert pass
# TODO: insert continue
# TODO: remove endlines

from redbaron import RedBaron

from redbaron.nodes import *


class NonNodeSpecificTransformation():
    
    def __init__(self, ast: RedBaron) -> None:
        self.ast = ast
    
    def insert_pass(self) -> None:
        pass   
    
    def insert_continue(self) -> None:
        pass
