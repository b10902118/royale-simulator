from env import ClashRoyaleEnv
from character import Character, DELTA_TIME
from player import Player
import pygame


pygame.init()

player = Player(
    deck=[
        "Goblins",
        "Cannon",
        "Minions",
        "Giant",
        "MinionHorde",
        "MiniPekka",
        "Musketeer",
        "Arrows",
    ],
    type="player",
)
enemy = Player(
    deck=[
        "Giant",
        "Goblins",
        "Cannon",
        "Minions",
        "MinionHorde",
        "MiniPekka",
        "Musketeer",
        "Arrows",
    ],
    type="enemy",
)

env = ClashRoyaleEnv(player, enemy)
env.reset()

simlation_time = 60


for _ in range(round(simlation_time / DELTA_TIME)):  # 運行simlation_time秒
    action = env.action_space.sample()
    env.step(action)
    env.render()

env.close()
