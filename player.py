from Constant import DELTA_TIME
from character import Character
from building import Building
from spells import Arrow, Fireball, Rage, Rocket, Heal, Poison
import random


class Player:
    def __init__(
        self,
        deck=[
            "Barbarians",
            "Minions",
            "Giant",
            "Knight",
            "Pekka",
            "SpearGoblins",
            "Bats",
            "Witch",
        ],
        type="player",
    ):
        self.deck = []
        for name in deck:
            if name == "Arrows":
                self.deck.append(Arrow())
            elif name == "FireBall":
                self.deck.append(Fireball())
            elif name == "Rocket":
                self.deck.append(Rocket())
            elif name == "Rage":
                self.deck.append(Rage())
            elif name == "Heal":
                self.deck.append(Heal())
            elif name == "Poison":
                self.deck.append(Poison())
            else:
                try:
                    c = Character(name)
                    self.deck.append(c)
                except:
                    b = Building(name)
                    self.deck.append(b)
        # random.shuffle(self.deck)

        self.type = type
        self.elixir = 5

    def put_card(self, which_card=0):
        if self.elixir >= self.deck[which_card].elixir_cost:
            card = self.deck.pop(which_card)
            self.elixir -= card.elixir_cost
            self.deck.append(card)
            return card
        else:
            return None

    def add_elixir(self, time=3):
        self.elixir = min(10, self.elixir + 1 / time * DELTA_TIME)
