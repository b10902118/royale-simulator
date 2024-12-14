from projectile import Projectile
import csv,os
import pygame
import numpy as np
from Constant import GRID_WIDTH,GRID_HEIGHT,DELTA_TIME,RAGE_PURPLE,SLOW_BLUE,RAGE_SLOW_MIXED
from character import Character

BLUE = (0, 150, 238)
RED = (255, 85, 85)



def read_buildng_csv(file_path):
    _data = {}
    # Define the columns we want to extract
    columns_to_extract = [
        "SightRange","Range","DeployTime","LifeTime","LoadTime","Range","Scale",
        "Hitpoints","HitSpeed","Damage","Projectile","CollisionRadius",
        "AttacksGround","AttacksAir",
        "SpawnCharacter","SpawnNumber","SpawnInterval","SpawnPauseTime"
    ]
    
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Name']!="string":
                name = row['Name']
                _info = {}
                
                for col in columns_to_extract:
                    value = row[col]
                    
                    # Handle boolean fields, setting missing values to "false"
                    if value=="" or value.lower() == "false":
                        _info[col] = False
                    # Handle integer fields, setting missing values to -1
                    elif value=="" or value == "NULL":
                        _info[col] = -1
                    else:
                        # Convert non-empty values to the appropriate type (boolean or integer)
                        if col in ["SightRange","Range","DeployTime","LifeTime","LoadTime",
                                    "Hitpoints","HitSpeed","Damage","CollisionRadius","Range","Scale"
                                    ,"SpawnNumber","SpawnInterval","SpawnPauseTime"]:  # These are integers
                            _info[col] = int(value)
                        elif col in ["Projectile","SpawnCharacter"]:
                            _info[col]=value
                        else:  # Handle boolean fields like "AoeToAir", "AoeToGround", etc.
                            _info[col] = value.lower() == 'true'
                
                # Add the processed data for this projectile to the main dictionary
                _data[name] = _info
    
    return _data

building_data=read_buildng_csv("logic_csv//buildings.csv")



class Building():
    def __init__(self,name,type="player"):
        self.name=name
        for key, value in building_data[name].items():
            setattr(self, key, value)
        with open("logic_csv//spells_buildings.csv", 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Name"]==self.name:
                    self.elixir_cost=int(row["ManaCost"])
                    break
                
        self.current_time = pygame.time.get_ticks()
        self.last_attack_time = 0
        self.last_spawn_time=0
        self.total_life=self.Hitpoints
        self.life=self.total_life
        self.sight_line_width=1
        self.attack_line_width=1
        self.W=2*self.CollisionRadius/1000*GRID_WIDTH
        self.H=2*self.CollisionRadius/1000*GRID_HEIGHT
        self.target=None
        self.minus_life_fps=self.total_life/(self.LifeTime/1000) *DELTA_TIME 
        self.type=type
        self.can_fly=False
        self.deck_img=pygame.image.load(f"card_img//{name}.webp") if os.path.exists(f"card_img//{name}.webp") else None
        self.font = pygame.font.SysFont("Arial", 12, bold=True)
        
        self.last_rage_time=0
        self.has_rage=False
        self.in_rage=False
        
        self.last_slow_time=0
        self.has_slow=False
        self.need_slow=False
        
        self.original_HitSpeed=self.HitSpeed
        self.original_spawn_speed=self.SpawnPauseTime
        
                
    def __str__(self):
        # Build a string representation of the object
        attributes = [f"{key}: {value}" for key, value in sorted(self.__dict__.items())]
        return f"Character({self.name})\n" + "\n".join(attributes)
    
    def initiate(self,X,Y):
        self.posX=X
        self.posY=Y
    
    def act(self,enemy_troops,arena):
        self.current_time = pygame.time.get_ticks()
        
        if self.in_rage:
            if self.has_rage==False:
                self.has_rage=True
                self.SpawnPauseTime*=0.65
                self.HitSpeed*=0.65
            if self.current_time-self.last_rage_time>2000:
                self.in_rage=False
                self.has_rage=False
                self.SpawnPauseTime=self.original_spawn_speed
                self.HitSpeed=self.original_HitSpeed

            
        if self.need_slow:
            if self.has_slow==False:
                self.has_slow=True
                self.SpawnPauseTime*=1.35
                self.HitSpeed*=1.35 
            if self.current_time-self.last_slow_time>2000:
                self.need_slow=False
                self.has_slow=False
                self.SpawnPauseTime=self.original_spawn_speed
                self.HitSpeed=self.original_HitSpeed

        
        if self.current_time<self.DeployTime:
            self.msg="Deploying..."
        else:
            #建築因爲生存時間會自己扣血，
            self.life-= self.minus_life_fps   
                         
            if self.SpawnNumber:#生產建築
                if self.current_time-self.last_spawn_time>self.SpawnPauseTime or self.last_spawn_time==0:
                    self.msg="Spawning"
                    self.last_spawn_time=self.current_time
                    enemy_left_tower=arena.enemy_left_tower if self.type=="player" else arena.player_left_tower
                    enemy_right_tower=arena.enemy_right_tower if self.type=="player" else arena.player_right_tower
                    enemy_main_tower=arena.enemy_castle if self.type=="player" else arena.player_castle
                    for i in range(self.SpawnNumber):
                        c_i=Character(self.SpawnCharacter+"s",arena,enemy_left_tower,enemy_right_tower,enemy_main_tower,arena.left_bridge,arena.right_bridge,pos_x=self.posX,pos_y=self.posY-0.5*self.H if self.type=="player" else self.posY+0.5*self.H,type=self.type)
                        arena.avoid_out_of_bound(c_i)
                        arena.player_queue.append(c_i) if self.type=="player" else arena.enemy_queue.append(c_i)

            elif self.name=="ElixirCollector":
                if self.current_time-self.last_spawn_time>8500:
                    self.msg="Add Elixir"
                    self.last_spawn_time=self.current_time
                    if self.type=="player":
                        arena.player.elixir+=1  
                    else:
                        arena.enemy.elixir+=1
                else:
                    self.msg="Generating..."
                    
            else:#攻擊建築
                target=self.find_target(enemy_troops)
                if self.target==None:
                    self.target=target
                else:
                    if hasattr(self.target,"enemis_in_range"):#原本目標為敵方防禦塔
                        #將目標轉爲敵方單位
                        self.target=target
                    else:
                        if self.target:
                            if self.target.life<0:
                                if target:
                                    if target.life<0:
                                        self.target=None
                                    else:
                                        self.target=target
                            else:#如果原本目標還活著,繼續攻擊原本目標
                                if self.is_in_sight(self.target):
                                    target=self.target   
                                        
                if target!=None:
                    self.attack_line_width=3
                    self.attack(target,arena)    
                else:
                    self.msg="No target found"
                    self.attack_line_width=1
                
    def find_target(self,enemy_troops):        
        targets_in_sight=[]
        all_distance={}
        for enemy in enemy_troops:
            if self.is_in_sight(enemy):
                if not (self.AttacksAir==False and enemy.can_fly):
                    targets_in_sight.append(enemy)
        if len(targets_in_sight)>0:
            self.sight_line_width=3
            for t in targets_in_sight:
                all_distance[t]=self.calc_distance(self.posX,t.posX,self.posY,t.posY)          
            target = min(all_distance, key=all_distance.get)
            return target
        else:
            self.sight_line_width=1
            return None
        
    def attack(self,target,arena):
        self.msg=f"Attack {target.name}"
        #print(self.current_time,self.last_attack_time,self.HitSpeed)
        if self.current_time - self.last_attack_time >= self.HitSpeed:
            self.last_attack_time = self.current_time
            if self.Projectile!=False:
                proj=Projectile(self.Projectile,self.type)
                proj.initiate(target,self.posX,self.posY+0.5*self.CollisionRadius*GRID_HEIGHT/1000)
                arena.all_projectile.append(proj)
            else:
                target.life -= self.Damage
             
    def is_in_sight(self,enemy):
        if hasattr(enemy,"summon_num"):
            ellipse_sight = {"cx": self.posX, "cy": self.posY, "a": self.SightRange / 1000 * GRID_WIDTH, "b": self.SightRange / 1000 * GRID_HEIGHT}  
            ellipse_enemy = {"cx": enemy.posX, "cy": enemy.posY, "a": enemy.CollisionRadius/1000*GRID_WIDTH, "b": enemy.CollisionRadius/1000*GRID_HEIGHT} 

            # 檢查 enemy是否在sight橢圓內
            return self.are_ellipses_intersecting(ellipse_enemy,ellipse_sight)
        else:
            a = self.SightRange / 1000 *GRID_WIDTH  # 長軸半徑
            b = self.SightRange / 1000 *GRID_HEIGHT  # 短軸半徑

            # 檢查 (posX, posY) 是否在橢圓內
            if ((enemy.posX - self.posX) ** 2) / a ** 2 + ((enemy.posY - self.posY) ** 2) / b ** 2 <= 1:
                return True
            else:
                return False
    
    def rage_buff(self):
        self.last_rage_time=self.current_time
        self.in_rage=True
    
    def slow_down_debuff(self):
        self.last_slow_time=self.current_time
        self.need_slow=True        
            
    def calc_distance(self,X1,X2,Y1,Y2):
        return ((X1-X2)**2+(Y1-Y2)**2)**0.5
    
    def are_ellipses_intersecting(self,ellipse1, ellipse2,sample=360):
        # 橢圓1參數
        cx1, cy1, a1, b1 = ellipse1["cx"], ellipse1["cy"], ellipse1["a"], ellipse1["b"]
        # 橢圓2參數
        cx2, cy2, a2, b2 = ellipse2["cx"], ellipse2["cy"], ellipse2["a"], ellipse2["b"]

        # 快速檢測：外接圓篩選
        distance = np.sqrt((cx2 - cx1) ** 2 + (cy2 - cy1) ** 2)
        if distance > max(a1, b1) + max(a2, b2):
            #print("No Intersection")
            return False  # 一定不相交

        theta = np.linspace(0, 2 * np.pi, sample)
        x1 = cx1 + a1 * np.cos(theta)
        y1 = cy1 + b1 * np.sin(theta)
        x2 = cx2 + a2 * np.cos(theta)
        y2 = cy2 + b2 * np.sin(theta)

        # 判斷橢圓1邊界點是否落在橢圓2內
        for x, y in zip(x1, y1):
            if ((x - cx2) ** 2) / a2 ** 2 + ((y - cy2) ** 2) / b2 ** 2 <= 1:
                return True  # 存在交集

        # 判斷橢圓2邊界點是否落在橢圓1內
        for x, y in zip(x2, y2):
            if ((x - cx1) ** 2) / a1 ** 2 + ((y - cy1) ** 2) / b1 ** 2 <= 1:
                return True  # 存在交集

        return False  # 無交集
    def draw_elispse(self,screen,color,X,Y,range,line_thickness = 2):
        attack_range_long_axis = (range +0.5*self.CollisionRadius)/1000 *2* GRID_WIDTH  # Long axis of the ellipse
        attack_range_short_axis = (range +0.5*self.CollisionRadius)/1000 *2* GRID_HEIGHT  # Short axis of the ellipse  

            
        pygame.draw.ellipse(screen, color,
                            (X - 0.5*attack_range_long_axis ,
                             Y - 0.5*attack_range_short_axis ,
                             attack_range_long_axis, attack_range_short_axis),
                            width=line_thickness)
    
    def draw(self, screen, show_act=False):
        # 1. 在屏幕上 (posX, posY) 顯示 deck_img
        scaled_width = int(self.deck_img.get_width() * self.Scale / 1000)
        scaled_height = int(self.deck_img.get_height() * self.Scale / 1000)
        scaled_img = pygame.transform.scale(self.deck_img, (scaled_width, scaled_height))
        img_rect = scaled_img.get_rect(center=(self.posX, self.posY))
        scaled_img.convert()
        # screen.blit(scaled_img, img_rect)
        
        # 2. 以 (posX, posY) 為中心畫三個圓        
        pygame.draw.rect(screen, BLUE if self.type=="blue" else RED, pygame.Rect(self.posX-0.5*self.W,self.posY-0.5*self.H,self.W,self.H))
        self.draw_elispse(screen, (0, 255, 0), self.posX, self.posY, self.SightRange-0.5*self.CollisionRadius,line_thickness=self.sight_line_width)  # 目視距離
        self.draw_elispse(screen, (255, 0, 255), self.posX, self.posY, self.Range-0.5*self.CollisionRadius,line_thickness=self.attack_line_width)  # 攻擊距離

        # 3. 如果受傷畫一個血條
        if self.life<self.total_life or True:
            health_bar_width = 70  # 健康條的總寬度
            health_bar_height = 10  # 健康條的高度
            bar_x = self.posX - health_bar_width // 2
            bar_y = self.posY - img_rect.height // 2 -10 
            health_ratio = max(0, self.life / self.total_life)  # 確保生命值不低於 0
            pygame.draw.rect(screen, (128, 128, 128), (bar_x, bar_y, health_bar_width, health_bar_height))  # 灰色背景條
            pygame.draw.rect(screen, BLUE if self.type=="player" else RED, (bar_x, bar_y, int(health_bar_width * health_ratio), health_bar_height))  # 血條
            health_text = f"{round(self.life)}/{self.total_life}"
            text_surface = self.font.render(health_text, True, (255, 255, 255))  # White text
            text_rect = text_surface.get_rect(center=(self.posX, bar_y + health_bar_height // 2))
            screen.blit(text_surface, text_rect)

        # 4. 在 deck_img 上方顯示名字
        font = pygame.font.Font(None, 20)  # 使用默認字體，大小為 24
        name_surface = font.render(self.name, True, (0,0,255) if self.type=="player" else (255,0,0))
        name_rect = name_surface.get_rect(center=(self.posX, self.posY - img_rect.height // 2 - 2*health_bar_height))  # 名字在 deck_img 上方
        screen.blit(name_surface, name_rect)
        
        # 5. 顯示動作
        if show_act:
            font = pygame.font.Font(None, 20)  # 使用默認字體，大小為 24
            if self.in_rage and self.need_slow:
                color=RAGE_SLOW_MIXED
            elif self.in_rage:
                color=RAGE_PURPLE
            elif self.need_slow:
                color=SLOW_BLUE
            else:
                color=(255,255,255)
            msg_surface = font.render(self.msg, True, color)  # 白色字體
            msg_rect = msg_surface.get_rect(center=(self.posX, self.posY - img_rect.height // 2 - 3*health_bar_height))  # 名字在 deck_img 上方
            screen.blit(msg_surface, msg_rect)

    
    
if __name__=="__main__":
    pygame.init()
    b=Building("Tesla")
    print(b)