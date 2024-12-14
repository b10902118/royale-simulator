import gym,random
from gym import spaces
import numpy as np
import pygame
from arena import GRID_HEIGHT,GRID_WIDTH,Arena
from character import Character
from building import Building
from player import Player
from spells import Arrow,Fireball,Rocket,Rage,Heal,Poison

class GameWindow():
    def __init__(self):
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 450, 800
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Clash Royale Simulator")

        # 顏色
        self.GREEN = (102, 204, 0)
        self.BROWN = (139, 69, 19)
        self.BLUE = (0, 102, 255)
        self.RED = (255, 22, 0)
        self.LIGHT_BLUE = (173, 216, 230)
        self.GRAY = (169, 169, 169)
        self.BLACK = (0, 0, 0)
        self.PINK = (189,52,205)
        self.ROAD_COLOR = (182,157,102)

        # 設定基礎參數
        self.clock = pygame.time.Clock()

        self.ui_height=6*GRID_HEIGHT
        self.card_width = 2.4*GRID_WIDTH
        self.card_height= 3.5*GRID_HEIGHT
        self.elixir_height=GRID_HEIGHT
        self.elixir_width=1.8*GRID_WIDTH
        
        bg=pygame.image.load("background.png")
        self.background_image = pygame.transform.scale(bg, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        
    def draw_background(self):
        # 背景
        self.screen.blit(self.background_image, (0, 0))
        #self.screen.fill(self.GREEN)
        # 河流
        # pygame.draw.rect(self.screen, self.LIGHT_BLUE, (0, 26*GRID_HEIGHT, self.SCREEN_WIDTH, 2*GRID_HEIGHT))
        
        # 道路
        # pygame.draw.rect(self.screen, self.ROAD_COLOR, (4*GRID_WIDTH,13.5*GRID_HEIGHT,GRID_WIDTH,26*GRID_HEIGHT))
        # pygame.draw.rect(self.screen, self.ROAD_COLOR, (15*GRID_WIDTH,13.5*GRID_HEIGHT,GRID_WIDTH,26*GRID_HEIGHT))
        # pygame.draw.rect(self.screen, self.ROAD_COLOR, (4*GRID_WIDTH,13.5*GRID_HEIGHT,12*GRID_WIDTH,GRID_HEIGHT))
        # pygame.draw.rect(self.screen, self.ROAD_COLOR, (4*GRID_WIDTH,38.5*GRID_HEIGHT,12*GRID_WIDTH,GRID_HEIGHT))
        
        # 橋樑
        # pygame.draw.rect(self.screen, self.BROWN, (3.5*GRID_WIDTH,25.5*GRID_HEIGHT, 2*GRID_WIDTH, 3*GRID_HEIGHT))
        # pygame.draw.rect(self.screen, self.BROWN, (14.5*GRID_WIDTH,25.5*GRID_HEIGHT, 2*GRID_WIDTH, 3*GRID_HEIGHT))

    def draw_deck_ui(self,player :Player,enemy: Player):
        # （敵方卡牌欄和聖水槽）
        pygame.draw.rect(self.screen, self.BLACK, (0, 0, self.SCREEN_WIDTH, self.ui_height))
        
        # 卡牌槽
        for i in range(4):
            card_rect = pygame.Rect(2.5*GRID_WIDTH + i * (self.card_width + 10), 2.2*GRID_HEIGHT, self.card_width, self.card_height)
            if enemy.deck[i].deck_img:
                img = pygame.transform.scale(enemy.deck[i].deck_img, (self.card_width, self.card_height))  # Scale image to fit the card slot
                img.convert()
                self.screen.blit(img, card_rect.topleft)  # Place the image at the calculated position
            else:
                # If no image, just draw a placeholder (you can customize it)
                pygame.draw.rect(self.screen, self.GRAY, card_rect)
            
        
        #下一張卡
        next_card_rect = pygame.Rect(0.5*GRID_WIDTH, 3.5*GRID_HEIGHT, 0.5*self.card_width, 0.5*self.card_height)
        if enemy.deck[5].deck_img:
            img = pygame.transform.scale(enemy.deck[5].deck_img, (0.5*self.card_width, 0.5*self.card_height))  # Scale image to fit the card slot
            img.convert()
            self.screen.blit(img, next_card_rect.topleft)  # Place the image at the calculated position
        else:
            # If no image, just draw a placeholder (you can customize it)
            pygame.draw.rect(self.screen, self.GRAY, next_card_rect)
        
        # 聖水槽
        for i in range(10):
            gap=1
            # 填充已獲得聖水的格子
            if i < int(enemy.elixir):
                pygame.draw.rect(self.screen, self.PINK, (1.2*GRID_WIDTH + i * (self.elixir_width+gap), GRID_HEIGHT, self.elixir_width , self.elixir_height))
            else:
                # 未獲得的聖水格子顏色為深灰色
                pygame.draw.rect(self.screen, (100, 100, 100), (1.2*GRID_WIDTH + i * (self.elixir_width+gap), GRID_HEIGHT, self.elixir_width , self.elixir_height))
            
            
                
        # （玩家卡牌欄和聖水槽）
        pygame.draw.rect(self.screen, self.BLACK, (0, self.SCREEN_HEIGHT-self.ui_height, self.SCREEN_WIDTH, self.ui_height))
        
        # 卡牌槽
        for i in range(4):
            card_rect = pygame.Rect(2.5*GRID_WIDTH + i * (self.card_width + 10), self.SCREEN_HEIGHT-5.5*GRID_HEIGHT, self.card_width, self.card_height)
            if player.deck[i].deck_img:
                img = pygame.transform.scale(player.deck[i].deck_img, (self.card_width, self.card_height))  # Scale image to fit the card slot
                img.convert()
                self.screen.blit(img, card_rect.topleft)  # Place the image at the calculated position
            else:
                # If no image, just draw a placeholder (you can customize it)
                pygame.draw.rect(self.screen, self.GRAY, card_rect)
        
        #下一張卡
        next_card_rect = pygame.Rect(0.5*GRID_WIDTH, self.SCREEN_HEIGHT-5.5*GRID_HEIGHT, 0.5*self.card_width, 0.5*self.card_height)
        if player.deck[5].deck_img:
            img = pygame.transform.scale(player.deck[5].deck_img, (0.5*self.card_width, 0.5*self.card_height))  # Scale image to fit the card slot
            img.convert()
            self.screen.blit(img, next_card_rect.topleft)  # Place the image at the calculated position
        else:
            # If no image, just draw a placeholder (you can customize it)
            pygame.draw.rect(self.screen, self.GRAY, next_card_rect)
        
        # 聖水槽
        for i in range(10):
            gap=1
            # 填充已獲得聖水的格子
            if i < int(player.elixir):
                pygame.draw.rect(self.screen, self.PINK, (1.2*GRID_WIDTH + i * (self.elixir_width+gap), self.SCREEN_HEIGHT-1.5*GRID_HEIGHT, self.elixir_width , self.elixir_height))
            else:
                # 未獲得的聖水格子顏色為深灰色
                pygame.draw.rect(self.screen, (100, 100, 100), (1.2*GRID_WIDTH + i * (self.elixir_width+gap), self.SCREEN_HEIGHT-1.5*GRID_HEIGHT, self.elixir_width , self.elixir_height))
        

class ClashRoyaleEnv(gym.Env):
    def __init__(self,player: Player,enemy :Player):
        super(ClashRoyaleEnv, self).__init__()
        
        # 定義狀態空間和動作空間
        self.observation_space = spaces.Box(low=0, high=1, shape=(10,), dtype=np.float32)
        self.action_space = spaces.Discrete(8)

        # 初始化遊戲狀態

        self.arena=Arena(player,enemy)
        self.game_window=GameWindow()
        
        self.player=player
        self.enemy=enemy
        
        self.state = self.reset()
        self.hasput=False

    def reset(self):
        self.state = np.zeros(self.observation_space.shape)
        self.player.elixir=5
        self.enemy.elixir=5
        return self.state

    def step(self, action):
        reward = 0
        done = False
        info = {}

        #先暫時隨便丟一張
        if self.hasput==False:
            self.arena.place_card(self.player.put_card(random.randint(0,3)),8,20,self.player.type)
            self.arena.place_card(self.enemy.put_card(random.randint(0,3)),8,10,self.enemy.type)
            
            # self.arena.place_card(Character("IceWizard"),6,13,self.player.type)
            # self.arena.place_card(Heal(),6,9,self.player.type)
            
            # self.arena.place_card(Building("Cannon"),8,10,self.enemy.type)
            # self.arena.place_card(Character("Giant"),5,15,self.player.type)
            self.hasput=True
        
        self.arena.update()
        self.player.add_elixir()
        self.enemy.add_elixir()
        return self.state, reward, done, info

    def render(self, mode="human"):
        # 更新游戲視窗
        self.game_window.draw_background()
        self.arena.draw_castles_and_towers(self.game_window.screen)
        self.arena.update_screen(self.game_window.screen)
        self.game_window.draw_deck_ui(self.player,self.enemy)
        pygame.display.flip()
        self.game_window.clock.tick(30)

    def close(self):
        pygame.quit()