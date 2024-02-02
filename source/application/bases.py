from typing import Protocol

class MonoState:
    # shared state of all objects
    __shared = {}
    
    def __init__(self) -> None:
        self.__dict__ = self.__shared


class Observable(Protocol):
    def attach(observer):
        ...
    
    def notify(self, event_type: str):
        ...


class Observer(Protocol):
    def on_update(self, event_type: str):
        ...