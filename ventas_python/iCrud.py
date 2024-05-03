from abc import ABC, abstractmethod

class ICrud(ABC):

    @abstractmethod
    def create(self):
        pass
    @abstractmethod
    def update(self):
        pass
    @abstractmethod
    def delete(self):
        pass
    @abstractmethod
    def consult(self):
        pass