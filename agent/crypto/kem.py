from abc import ABC, abstractmethod


class KEM(ABC):

    @abstractmethod
    def generate_keypair(self):
        pass

    @abstractmethod
    def encapsulate(self, public_key):
        pass

    @abstractmethod
    def decapsulate(self, ciphertext):
        pass