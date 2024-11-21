import os,csv,math,random
import pygame
import numpy as np



GRID_WIDTH=22.5
GRID_HEIGHT=16
BLUE = (0, 150, 238)
RED = (255, 85, 85)

fps=30
DELTA_TIME=1/fps

# Function to read the CSV file and load character data into a dictionary
def read_characters_csv(file_path):
    characters_data = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['Name']  # Assuming the CSV has a "Name" column
            characters_data[name] = {key: value for key, value in row.items() if key != 'Name'}
    return characters_data

def read_spells_characters_csv(file_path):
    spells_characters_data = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Name']!="string":
                name = row['Name']  # Assuming the CSV has a "Name" column
                mana_cost = int(row['ManaCost']) if row['ManaCost'] else 0  # Convert to int, default to 0 if empty
                summon_number = int(row['SummonNumber']) if row['SummonNumber'] else 1  # Default to 1 if empty
                spells_characters_data[name] = {'ManaCost': mana_cost, 'SummonNumber': summon_number if name !="GoblinGang" else 5}
                
                summon_character= row["SummonCharacter"]
                if summon_character:
                    Character_data[name]=Character_data[summon_character]
    return spells_characters_data

def read_projectiles_csv(file_path):
    projectiles_data = {}
    # Define the columns we want to extract
    columns_to_extract = [
        "Damage", "CrownTowerDamagePercent", "Pushback", "Radius", "AoeToAir", 
        "AoeToGround", "OnlyEnemies", "BuffTime", "ProjectileRadius", "ProjectileRange", 
        "MinDistance"
    ]
    
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Name']!="string":
                name = row['Name']
                # Initialize a dictionary to hold the extracted data for each projectile
                projectile_info = {}
                
                for col in columns_to_extract:
                    value = row[col]
                    
                    # Handle boolean fields, setting missing values to "false"
                    if value=="" or value.lower() == "false":
                        projectile_info[col] = False
                    # Handle integer fields, setting missing values to -1
                    elif value=="" or value == "NULL":
                        projectile_info[col] = -1
                    else:
                        # Convert non-empty values to the appropriate type (boolean or integer)
                        if col in ["Damage", "CrownTowerDamagePercent", "Pushback", "Radius", 
                                "ProjectileRange", "MinDistance"]:  # These are integers
                            projectile_info[col] = int(value)
                        else:  # Handle boolean fields like "AoeToAir", "AoeToGround", etc.
                            projectile_info[col] = value.lower() == 'true'
                
                # Add the processed data for this projectile to the main dictionary
                projectiles_data[name] = projectile_info
    
    return projectiles_data

Character_data=read_characters_csv("./logic_csv/characters.csv")
Spells_characters_data = read_spells_characters_csv("./logic_csv/spells_characters.csv")
Projectile_data=read_projectiles_csv("./logic_csv/projectiles.csv")

remove_keys=["AngryBarbarian","Archer","Barbarian","Bat","Goblin","Minion","Skeleton","SkeletonWarrior","SpearGoblin"]+[f"NOTINUSE{i}"for i in range(1,10) if i !=7]
for k in remove_keys:
    Character_data.pop(k)

# Class to represent a Character
class Character:
    def __init__(self, name,arena=None,enemy_left_tower=None,enemy_right_tower=None,enemy_main_tower=None,left_bridge=None,right_bridge=None,type="player",pos_x=0,pos_y=0):
        
        if name not in Character_data:
            raise ValueError(f"Character '{name}' not exist .")
        self.name = name
        if name in list(Spells_characters_data.keys()):
            self.summon_num=Spells_characters_data[name]['SummonNumber']
            self.elixir_cost=Spells_characters_data[name]['ManaCost']
        elif name=="Golemite":
            self.summon_num=2
            self.elixir_cost=-1
        elif name=="LavaPups":
            self.summon_num=5
            self.elixir_cost=-1
        else:
            self.summon_num=1
            self.elixir_cost=-1
        
        self.type=type
        self.posX=pos_x
        self.posY=pos_y
        self.total_life=int(Character_data[name]["Hitpoints"])
        self.life=self.total_life
        self.font = pygame.font.SysFont("Arial", 12, bold=True)
        self.deck_img=pygame.image.load(f"card_img//{name}.webp") if os.path.exists(f"card_img//{name}.webp") else None
        
        self.arena=arena
        self.enemy_left_tower=enemy_left_tower
        self.enemy_right_tower=enemy_right_tower
        self.enemy_main_tower=enemy_main_tower
        self.left_bridge=left_bridge
        self.right_bridge=right_bridge
        
        self.msg="Loading..."
        
        self.current_time = pygame.time.get_ticks()
        self.last_attack_time = 0
        
        self.sight_line_width=1
        self.attack_line_width=1
        
        
        # Dynamically add attributes based on the CSV data
        for key, value in Character_data[name].items():
            if key=="AttacksAir" or key=="TargetOnlyBuildings":
                setattr(self, key, True if value else False)
            else:
                if value and key not in ["AttackStartEffect","BlueExportName","DeployBaseAnimExportName","FileName","RedExportName","TID","UseAnimator"]:
                    if value.isdigit():
                        setattr(self, key, int(value))
                    else:
                        setattr(self, key, value)
        if hasattr(self, 'Projectile'):
            if self.Projectile in list(Projectile_data.keys()):
                for key, value in Projectile_data[self.Projectile].items():
                    setattr(self, key, value)
        self.can_fly=hasattr(self, 'FlyingHeight')
        if hasattr(self,"AoeToGround" )==False:
            self.AoeToGround=False
        if hasattr(self,"AoeToAir")==False:
            self.AoeToAir=False

    
    def __str__(self):
        # Build a string representation of the object
        attributes = [f"{key}: {value}" for key, value in sorted(self.__dict__.items())]
        return f"Character({self.name})\n" + "\n".join(attributes)
    
    def act(self,enemy_troops,player_troops,arena):
        self.current_time = pygame.time.get_ticks()
        if self.current_time<self.DeployTime:
            self.msg="Deploying..."
        else:
            target=self.find_target(enemy_troops)
            if self.can_attack(target):
                self.attack_line_width=3
                self.attack(target,enemy_troops)    
            else:
                self.attack_line_width=1
                self.move(target)
            self.avoid_collisions(enemy_troops+player_troops,arena)
        
        
    def find_target(self,enemy_troops):
        l_tower_distance=self.calc_distance(self.posX,self.enemy_left_tower.gameObject.centerx,self.posY,self.enemy_left_tower.gameObject.centery) if self.enemy_left_tower.is_destroyed()==False else 8787878787
        r_tower_distance=self.calc_distance(self.posX,self.enemy_right_tower.gameObject.centerx,self.posY,self.enemy_right_tower.gameObject.centery) if self.enemy_right_tower.is_destroyed()==False else 8787878787
        main_tower_distance=self.calc_distance(self.posX,self.enemy_main_tower.gameObject.centerx,self.posY,self.enemy_main_tower.gameObject.centery) if self.enemy_main_tower.is_destroyed()==False else 8787878787
        
        #預設target為最近的防禦塔
        all_distance={}
        all_distance[self.enemy_left_tower]=l_tower_distance
        all_distance[self.enemy_right_tower]=r_tower_distance
        all_distance[self.enemy_main_tower]=main_tower_distance
        
        targets_in_sight=[]
        if self.TargetOnlyBuildings==False:
            for enemy in enemy_troops:
                if self.is_in_sight(enemy):
                    if not (self.AttacksAir==False and enemy.can_fly):
                        targets_in_sight.append(enemy)
            if len(targets_in_sight)>0:
                all_distance={} #有敵方軍隊出現，敵方防禦塔變為次要目標
                for t in targets_in_sight:
                    all_distance[t]=self.calc_distance(self.posX,t.posX,self.posY,t.posY)
        else:
            "not implement"
        
        if len(targets_in_sight)>0:
            self.sight_line_width=3
        else:
            self.sight_line_width=1
 
        target = min(all_distance, key=all_distance.get)
        #print(f"{self.name}'s tagret is {target.name}")
        return target
        
    def can_attack(self,enemy):     
        if hasattr(enemy,"summon_num"):  
            ellipse_atk_range = {"cx": self.posX, "cy": self.posY, "a": self.Range / 1000 * GRID_WIDTH, "b": self.Range / 1000 * GRID_HEIGHT}
            ellipse_enemy = {"cx": enemy.posX, "cy": enemy.posY, "a": enemy.CollisionRadius/1000*GRID_WIDTH, "b": enemy.CollisionRadius/1000*GRID_HEIGHT} 
            return self.are_ellipses_intersecting(ellipse_enemy,ellipse_atk_range)
        else:
            a = self.Range / 1000 *GRID_WIDTH  # 長軸半徑
            b = self.Range / 1000 *GRID_HEIGHT  # 短軸半徑
            
            tower_y=enemy.posY-self.CollisionRadius*GRID_HEIGHT/1000 if self.type=="player" else enemy.posY+self.CollisionRadius*GRID_HEIGHT/1000

            # 檢查 (posX, posY) 是否在橢圓內
            if ((enemy.posX - self.posX) ** 2) / a ** 2 + ((tower_y - self.posY) ** 2) / b ** 2 <= 1:
                return True
            else:
                return False

    def attack(self,target,enemy_troop):
        self.msg=f"Attack {target.name}"
        #print(self.current_time,self.last_attack_time,self.HitSpeed)
        if self.current_time - self.last_attack_time >= self.HitSpeed:
            self.last_attack_time = self.current_time
            if self.AoeToGround==False and self.AoeToAir==False:#單體攻擊
                target.life -= self.Damage
            else:
                ground_enemys=[e for e in enemy_troop if e.can_fly==False]
                air_enemys=[e for e in enemy_troop if e.can_fly]
                if self.AoeToGround==True:
                    for g in ground_enemys:
                        if ((g.posX-target.posX) ** 2) / (self.Radius/1000*GRID_WIDTH) ** 2 + ((g.posY - target.posY) ** 2) / (self.Radius/1000*GRID_HEIGHT) ** 2 <= 1:
                            g.life-=self.Damage     
                if self.AoeToAir==True:
                    for a in air_enemys:
                        if ((a.posX-target.posX) ** 2) / (self.Radius/1000*GRID_WIDTH) ** 2 + ((a.posY - target.posY) ** 2) / (self.Radius/1000*GRID_HEIGHT) ** 2 <= 1:
                            a.life-=self.Damage
                for t in [self.enemy_left_tower,self.enemy_right_tower,self.enemy_main_tower]:
                      if ((t.posX-target.posX) ** 2) / (self.Radius/1000*GRID_WIDTH) ** 2 + ((t.posY - target.posY) ** 2) / (self.Radius/1000*GRID_HEIGHT) ** 2 <= 1:
                            t.life-=self.Damage  
        
    def move(self,target):
        #目標是防禦塔
        if hasattr(target,"summon_num")==False:
            if self.can_fly or self.name=="HogRider":#野豬騎士可以無視河直接過去
                self.msg=f"Move to {target.name}"
                self._move_to_target(target)
            else:
                if self.is_over_bridge()==False:
                    self.msg=f"Move to {target.name} (to bridge)"
                    self._move_to_bridge()
                else:
                        if self.is_on_the_bridge():
                            self.msg=f"Move to {target.name} (on bridge)"
                            self._move_on_the_bridge(target)
                        else:
                            self.msg=f"Move to {target.name} (over the bridge)"
                            self._move_to_target(target)
        #目標是敵方軍隊    
        else:
            if self.can_fly or self.name=="HogRider":
                self.msg=f"Move to {target.name}"
                self._move_to_target(target)
            else:
                if self.is_over_bridge()==target.is_over_bridge():#目標和自己隔了一條河
                    if self.is_on_the_bridge():
                        self.msg=f"Move to {target.name} (on bridge)"
                        self._move_on_the_bridge(target)
                    else:
                        self.msg=f"Move to {target.name} (to bridge)"
                        self._move_to_bridge()
                else:
                    if self.is_on_the_bridge():
                        self.msg=f"Move to {target.name} (on bridge)"
                        self._move_on_the_bridge(target)
                    else:
                        self.msg=f"Move to {target.name} (over the bridge)"
                        self._move_to_target(target)
            
    def avoid_collisions(self, all_characters,arena):
        #self.avoid_out_of_bound(arena)
        for other in all_characters:
            if other is not self and hasattr(other,"summon_num") and self.can_fly==other.can_fly:  # 避免和自己進行檢測
                # 計算與其他角色的距離
                ellipse_self = {"cx": self.posX, "cy": self.posY, "a": self.CollisionRadius / 1000 * GRID_WIDTH, "b": self.CollisionRadius / 1000 * GRID_HEIGHT}  
                ellipse_other = {"cx": other.posX, "cy": other.posY, "a": other.CollisionRadius/1000*GRID_WIDTH, "b": other.CollisionRadius/1000*GRID_HEIGHT} 
                if self.are_ellipses_intersecting(ellipse_self, ellipse_other):
                    # 計算兩橢圓中心之間的距離
                    dx = self.posX - other.posX
                    dy = self.posY - other.posY
                    distance = math.sqrt(dx**2 + dy**2)

                    # 確保橢圓推開方向
                    if distance != 0:
                        dx /= distance
                        dy /= distance
                    else:
                        # 如果距離為零，隨機方向推開，避免重疊
                        dx = 1
                        dy = 0

                    # 推開距離，取橢圓半徑的和作為最小安全距離
                    min_distance = (ellipse_self["a"] + ellipse_other["a"])
                    overlap = max(0, min_distance - distance)
                    #print(min_distance,distance,overlap)

                    # 更新角色位置，將兩者分開
                    self.posX += (other.Mass/self.Mass)*dx * overlap *DELTA_TIME
                    self.posY += (other.Mass/self.Mass)*dy * overlap *DELTA_TIME
                    other.posX -= (self.Mass/other.Mass)*dx * overlap *DELTA_TIME
                    other.posY -= (self.Mass/other.Mass)*dy * overlap *DELTA_TIME  
        
    
    def push_x(self,px):
        overlap=px-self.posX
        self.posX+=overlap/self.Speed*10*DELTA_TIME
        
    def push_y(self,py):
        overlap=py-self.posY
        self.posY+=overlap/self.Speed*10*DELTA_TIME
        
        
    
    def avoid_out_of_bound(self,arena):
        px,py=self.posX,self.posY
        #四周
        if px<arena.left_boundary:
            self.push_x(arena.left_boundary+self.CollisionRadius/1000*GRID_WIDTH)
        if px>arena.right_boundary:
            self.push_x(arena.right_boundary-self.CollisionRadius/1000*GRID_WIDTH)
        if py<arena.top_boundary:
            self.push_y(arena.top_boundary+self.CollisionRadius/1000*GRID_HEIGHT)
        if py>arena.bottom_boundary:
            self.push_y(arena.bottom_boundary-self.CollisionRadius/1000*GRID_HEIGHT)
        
        #防禦塔，邊界
        if arena.Grid_to_XYpos(0,0)[1]-0.5*GRID_HEIGHT<=py<=arena.Grid_to_XYpos(0,0)[1]+0.5*GRID_HEIGHT or arena.Grid_to_XYpos(0,31)[1]-0.5*GRID_HEIGHT<=py<=arena.Grid_to_XYpos(0,31)[1]+0.5*GRID_HEIGHT:
            if px<arena.Grid_to_XYpos(6,0)[0]:
                self.push_x(arena.Grid_to_XYpos(6,0)[0])
            if px>arena.Grid_to_XYpos(11,0)[0]:
                self.push_x(arena.Grid_to_XYpos(11,0)[0])                  
            
        #河流
        x1=arena.Grid_to_XYpos(1,15)[0]-0.5*GRID_WIDTH +self.CollisionRadius*GRID_WIDTH/1000
        x2=arena.Grid_to_XYpos(3,15)[0]+0.5*GRID_WIDTH -self.CollisionRadius*GRID_WIDTH/1000
        x3=arena.Grid_to_XYpos(12,15)[0]-0.5*GRID_WIDTH+self.CollisionRadius*GRID_WIDTH/1000
        x4=arena.Grid_to_XYpos(14,15)[0]+0.5*GRID_WIDTH-self.CollisionRadius*GRID_WIDTH/1000
        if self.can_fly==False and self.name!="HogRider" and not ((x1<=px<=x2) or (x3<=px<=x4)):
            if arena.Grid_to_XYpos(0,15)[1]-GRID_HEIGHT<=py<=arena.Grid_to_XYpos(0,16)[1]+GRID_HEIGHT:
                self.push_y(arena.Grid_to_XYpos(0,16)[1]+GRID_HEIGHT+2*self.CollisionRadius/1000*GRID_HEIGHT if self.type=="player" else arena.Grid_to_XYpos(0,15)[1]-GRID_HEIGHT-2*self.CollisionRadius/1000*GRID_HEIGHT)

                              
    
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
    
    def is_in_sight(self,enemy):
        if hasattr(enemy,"summon_num"):
            ellipse_sight = {"cx": self.posX, "cy": self.posY, "a": self.SightRange / 1000 * GRID_WIDTH, "b": self.SightRange / 1000 * GRID_HEIGHT}  
            ellipse_enemy = {"cx": enemy.posX, "cy": enemy.posY, "a": enemy.CollisionRadius/1000*GRID_WIDTH, "b": enemy.CollisionRadius/1000*GRID_HEIGHT} 

            # 檢查 enemy是否在sight橢圓內
            return self.are_ellipses_intersecting(ellipse_enemy,ellipse_sight)
        else:
            a = self.Range / 1000 *GRID_WIDTH  # 長軸半徑
            b = self.Range / 1000 *GRID_HEIGHT  # 短軸半徑
            
            tower_y=enemy.posY-self.CollisionRadius*GRID_HEIGHT/1000 if self.type=="player" else enemy.posY+self.CollisionRadius*GRID_HEIGHT/1000

            # 檢查 (posX, posY) 是否在橢圓內
            if ((enemy.posX - self.posX) ** 2) / a ** 2 + ((tower_y - self.posY) ** 2) / b ** 2 <= 1:
                return True
            else:
                return False
    
    def is_over_bridge(self):
        x1_left=self.left_bridge.posX-0.5*self.left_bridge.W+self.CollisionRadius*GRID_WIDTH/1000
        x2_left=self.left_bridge.posX+0.5*self.left_bridge.W-self.CollisionRadius*GRID_WIDTH/1000
        x1_right=self.right_bridge.posX-0.5*self.right_bridge.W+self.CollisionRadius*GRID_WIDTH/1000
        x2_right=self.right_bridge.posX+0.5*self.right_bridge.W-self.CollisionRadius*GRID_WIDTH/1000
        
        if self.type=="player":
            return (self.posY<=self.left_bridge.posY+0.5*self.left_bridge.H -2*self.CollisionRadius*GRID_HEIGHT/1000) and (x1_left<=self.posX<=x2_left or x1_right<self.posX<=x2_right)
        else:
            return (self.posY>=self.left_bridge.posY-0.5*self.left_bridge.H -2*self.CollisionRadius*GRID_HEIGHT/1000) and (x1_left<=self.posX<=x2_left or x1_right<self.posX<=x2_right)
    
    def is_on_the_bridge(self):
        x1_left=self.left_bridge.posX-0.5*self.left_bridge.W+self.CollisionRadius*GRID_WIDTH/1000
        x2_left=self.left_bridge.posX+0.5*self.left_bridge.W-self.CollisionRadius*GRID_WIDTH/1000
        x1_right=self.right_bridge.posX-0.5*self.right_bridge.W+self.CollisionRadius*GRID_WIDTH/1000
        x2_right=self.right_bridge.posX+0.5*self.right_bridge.W-self.CollisionRadius*GRID_WIDTH/1000
        
        if self.type=="player":
            y1=self.left_bridge.posY-0.5*self.left_bridge.H-2*self.CollisionRadius*GRID_HEIGHT/1000
            y2=self.left_bridge.posY+0.5*self.left_bridge.H+2*self.CollisionRadius*GRID_HEIGHT/1000
        else:
            y1=self.left_bridge.posY-0.5*self.left_bridge.H-2*self.CollisionRadius*GRID_HEIGHT/1000
            y2=self.left_bridge.posY+0.5*self.left_bridge.H-1*self.CollisionRadius*GRID_HEIGHT/1000
        # print((x1_left,x1_right,x2_left,x2_right,self.posX),(y1,y2,self.posY))
        return (y1<=self.posY<=y2) and (x1_left<=self.posX<=x2_left or x1_right<self.posX<=x2_right)
    
    def _move_around_tower(self, tower, next_posX, next_posY):
        # 角色的橢圓半徑（長軸和短軸）
        ellipse_radius_x = self.CollisionRadius / 1000 * GRID_WIDTH
        ellipse_radius_y = self.CollisionRadius / 1000 * GRID_HEIGHT

        # 防禦塔的中心和半徑
        tower_center = pygame.Vector2(tower.gameObject.center)
        char_center = pygame.Vector2(next_posX, next_posY)
        direction_to_tower = char_center - tower_center
        distance_to_tower = direction_to_tower.length()

        # 防禦塔的有效半徑（加上角色橢圓邊界的外接圓）
        tower_radius = tower.gameObject.width / 2 + 2*max(ellipse_radius_x, ellipse_radius_y)

        # 檢查是否碰撞
        if distance_to_tower < tower_radius:
            on_the_left=char_center.x<tower_center.x

            # 更新角色位置
            self.posX += -self.Speed*GRID_WIDTH / 100*DELTA_TIME if on_the_left else self.Speed*GRID_WIDTH / 100*DELTA_TIME
        else:
            # 如果不碰撞，直接更新目標位置，並考慮 DELTA_TIME
            self.posX += (next_posX - self.posX) * DELTA_TIME
            self.posY += (next_posY - self.posY) * DELTA_TIME    
                      
    def _move_to_bridge(self):
        l_bridge_dist=self.calc_distance(self.posX,self.left_bridge.posX,self.posY,self.left_bridge.posY)
        r_bridge_dist=self.calc_distance(self.posX,self.right_bridge.posX,self.posY,self.right_bridge.posY)
        target_bridge=self.left_bridge if l_bridge_dist<r_bridge_dist else self.right_bridge
        bridge_distance=l_bridge_dist if l_bridge_dist<r_bridge_dist else r_bridge_dist
        delta_x = target_bridge.posX - self.posX
        delta_y = target_bridge.posY - self.posY
        unit_vector_x = delta_x / bridge_distance
        unit_vector_y = delta_y / bridge_distance
        if self.can_fly == False:
            # 如果角色不能飛行，則直接更新位置
            next_posX = self.posX + unit_vector_x * (self.Speed / 100 * GRID_WIDTH) * DELTA_TIME
            next_posY = self.posY + unit_vector_y * (self.Speed / 100 * GRID_HEIGHT) * DELTA_TIME

            # 如果角色會碰到防禦塔，則讓角色繞過防禦塔
            tower_list=[self.arena.player_left_tower,self.arena.player_right_tower,self.arena.player_castle] if self.type=="player" else [self.arena.enemy_left_tower,self.arena.enemy_right_tower,self.arena.enemy_castle]
            for tower in tower_list:
                if tower.gameObject.colliderect(self._ellipse_rect(next_posX,next_posY)):  # 檢查是否會碰撞
                    # 計算繞過防禦塔的方向
                    self._move_around_tower(tower, next_posX, next_posY)
                    break
            else:
                # 沒有碰撞時更新位置
                self.posX = next_posX
                self.posY = next_posY
        else:
            # 如果角色可以飛行，則根據移動速度更新位置
            self.posX += unit_vector_x * (self.Speed / 100 * GRID_WIDTH) * DELTA_TIME
            self.posY += unit_vector_y * (self.Speed / 100 * GRID_HEIGHT) * DELTA_TIME
        
    def _move_on_the_bridge(self,target):
        l_bridge_dist=self.calc_distance(self.posX,self.left_bridge.posX,self.posY,self.left_bridge.posY)
        r_bridge_dist=self.calc_distance(self.posX,self.right_bridge.posX,self.posY,self.right_bridge.posY)
        target_bridge=self.left_bridge if l_bridge_dist<r_bridge_dist else self.right_bridge
        
        delta_x = target.posX - self.posX
        delta_y = target.posY - self.posY
        
        # 計算向量的長度
        distance = self.calc_distance(self.posX, target.posX, self.posY, target.posY)
        
        if hasattr(target,"summon_num"):
            if distance <= 0.5*(self.Scale+target.Scale)/100*0.5*(GRID_WIDTH+GRID_HEIGHT):# 如果目標與角色夠近，則不需要移動
                return 
        
        # 單位化方向向量
        unit_vector_x = delta_x / distance
        unit_vector_y = delta_y / distance
        
        # 根據角色的移動速度更新位置
        # 限制posX只能在橋上
        if target_bridge.posX-0.5*target_bridge.W+self.CollisionRadius / 1000 * GRID_WIDTH <= self.posX + unit_vector_x * (self.Speed/100*GRID_WIDTH)*DELTA_TIME <= target_bridge.posX+0.5*target_bridge.W-self.CollisionRadius / 1000 * GRID_WIDTH:
            self.posX += unit_vector_x * (self.Speed/100*GRID_WIDTH)*DELTA_TIME 
        self.posY += unit_vector_y * (self.Speed/100*GRID_HEIGHT)*DELTA_TIME 

    def _ellipse_rect(self, centerX, centerY):
        """
        計算角色橢圓的外接矩形，方便進行碰撞檢測。
        """
        width = 2*self.CollisionRadius / 1000 * GRID_WIDTH
        height = 2*self.CollisionRadius / 1000 * GRID_HEIGHT
        return pygame.Rect(centerX - width // 2, centerY - height // 2, width, height)
        
    def _move_to_target(self,target):
        delta_x = target.posX - self.posX
        delta_y = target.posY - self.posY
        
        # 計算向量的長度
        distance = self.calc_distance(self.posX, target.posX, self.posY, target.posY)
        
        if hasattr(target,"summon_num"):
            if distance <= 0.5*(self.Scale+target.Scale)/100*0.5*(GRID_WIDTH+GRID_HEIGHT):# 如果目標與角色夠近，則不需要移動
                return  
        
        # 單位化方向向量
        unit_vector_x = delta_x / distance
        unit_vector_y = delta_y / distance
        
        if self.can_fly == False:
            # 如果角色不能飛行，則直接更新位置
            next_posX = self.posX + unit_vector_x * (self.Speed / 100 * GRID_WIDTH) * DELTA_TIME
            next_posY = self.posY + unit_vector_y * (self.Speed / 100 * GRID_HEIGHT) * DELTA_TIME
            
            tower_list=[self.arena.player_left_tower,self.arena.player_right_tower,self.arena.player_castle] if self.type=="player" else [self.arena.enemy_left_tower,self.arena.enemy_right_tower,self.arena.enemy_castle]
            # 如果角色會碰到防禦塔，則讓角色繞過防禦塔
            for tower in tower_list:
                if tower.gameObject.colliderect(self._ellipse_rect(next_posX,next_posY)):  # 檢查是否會碰撞
                    # 計算繞過防禦塔的方向
                    self._move_around_tower(tower, next_posX, next_posY)
                    break
            else:
                # 沒有碰撞時更新位置
                self.posX = next_posX
                self.posY = next_posY
        else:
            # 如果角色可以飛行，則根據移動速度更新位置
            self.posX += unit_vector_x * (self.Speed / 100 * GRID_WIDTH) * DELTA_TIME
            self.posY += unit_vector_y * (self.Speed / 100 * GRID_HEIGHT) * DELTA_TIME
        

    
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
        self.draw_elispse(screen, (255, 255, 255), self.posX, self.posY, 0.5*self.CollisionRadius)  # 角色大小
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
            health_text = f"{self.life}/{self.total_life}"
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
            msg_surface = font.render(self.msg, True, (255,255,255))  # 白色字體
            msg_rect = msg_surface.get_rect(center=(self.posX, self.posY - img_rect.height // 2 - 3*health_bar_height))  # 名字在 deck_img 上方
            screen.blit(msg_surface, msg_rect)
    
    def get_injury(self,value):
        self.life-=value
    
    def get_heal(self,value):
        self.life+=value
    
    
if __name__=="__main__":
    pygame.init()
    print(Character("Giant"))
    # for k in sorted(list(Character_data.keys())):
    #     if k !='string':
    #         c=Character(k)
    #         # print("\n\n",c)
    #         if hasattr(c,'Damage'):
    #             print(k,f"個數:{c.summon_num}",f"damage:{c.Damage}",f"聖水:{c.elixir_cost},空中:{c.can_fly}")