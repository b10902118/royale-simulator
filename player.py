from Constant import DELTA_TIME
from character import Character
from building import Building
import random
    
    
class Player():
    def __init__(self,deck=["Barbarians","Minions","Giant","Knight","Pekka","SpearGoblins","Bats","Witch"],type="player"):
        self.deck=[]
        for name in deck:
            try:
                c=Character(name)
                self.deck.append(c)
            except:
                b=Building(name)
                self.deck.append(b)
        random.shuffle(self.deck)
        
        self.type=type
        self.elixir=5
    
    def put_card(self,which_card=0):
        if self.elixir>=self.deck[which_card].elixir_cost:
            card=self.deck.pop(which_card)
            self.elixir-=card.elixir_cost
            self.deck.append(card)
            return card
        else:
            return None
    
    def add_elixir(self,time=3):
        self.elixir=min(10, self.elixir + 1/time*DELTA_TIME)
    
    
        
        
        




