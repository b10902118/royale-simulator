from env import ClashRoyaleEnv
from character import Character,DELTA_TIME
from player import Player
import pygame


pygame.init()

player=Player(deck=["Barbarians","Minions","Giant","Knight","MiniPekka","SpearGoblins","Bats","Wizard"],type="player")
enemy=Player(deck=["BabyDragon","MinionHorde","Giant","Knight","MiniPekka","SpearGoblins","Bats","Cannon"],type="enemy")

env = ClashRoyaleEnv(player,enemy)
env.reset()

simlation_time=20


for _ in range(round(simlation_time/DELTA_TIME)):  # 運行simlation_time秒
    action = env.action_space.sample()
    env.step(action)
    env.render()  

env.close()