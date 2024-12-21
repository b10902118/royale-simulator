import pygame
import numpy as np
from Constant import *  # GRID_WIDTH,GRID_HEIGHT,MAP_SIZE,DELTA_TIME,RAGE_PURPLE,SLOW_BLUE,RAGE_SLOW_MIXED
from building import Building
from character import Character
from projectile import Projectile
from spells import Spell, Arrow, Fireball, Rocket, Rage, Heal, Poison


class KingTower:
    def __init__(self, X, Y, name="Main Tower", type="blue"):
        self.name = name
        self.attack_range = 7000
        self.attack_speed = 1000
        self.damage = 50
        self.total_life = 2400
        self.life = 2400
        self.activate = False
        self.type = type
        self.posX = X * GRID_WIDTH
        self.posY = Y * GRID_HEIGHT
        self.W = KING_TOWER_WIDTH * GRID_WIDTH
        self.H = KING_TOWER_HEIGHT * GRID_HEIGHT
        self.gameObject = pygame.Rect(
            self.posX - self.W // 2, self.posY - self.H // 2, self.W, self.H
        )
        self.enemis_in_range = False
        self.font = pygame.font.SysFont("Arial", 12, bold=True)
        self.current_time = pygame.time.get_ticks()
        self.last_attack_time = 0
        self.Projectile = "KingProjectile"
        self.target = None

        self.last_rage_time = 0
        self.has_rage = False
        self.in_rage = False

        self.last_slow_time = 0
        self.has_slow = False
        self.need_slow = False

        self.original_HitSpeed = self.attack_speed

    def is_destroyed(self):
        return self.life <= 0

    def attack(self, arena, enemys):
        self.current_time = pygame.time.get_ticks()
        min_dist = 100000000
        attack_target = None
        if self.in_rage:
            if self.has_rage == False:
                self.has_rage = True
                self.attack_speed *= 0.65
            if self.current_time - self.last_rage_time > 2000:
                self.in_rage = False
                self.has_rage = False
                self.attack_speed = self.original_HitSpeed

        if self.need_slow:
            if self.has_slow == False:
                self.has_slow = True
                self.attack_speed *= 1.35
            if self.current_time - self.last_slow_time > 2000:
                self.need_slow = False
                self.has_slow = False
                self.attack_speed = self.original_HitSpeed

        for e in enemys:
            ellipse_sight = {
                "cx": self.gameObject.centerx,
                "cy": self.gameObject.centery,
                "a": self.attack_range / 1000 * GRID_WIDTH,
                "b": self.attack_range / 1000 * GRID_HEIGHT,
            }
            ellipse_enemy = {
                "cx": e.posX,
                "cy": e.posY,
                "a": 2 * e.CollisionRadius / 1000 * GRID_WIDTH,
                "b": 2 * e.CollisionRadius / 1000 * GRID_HEIGHT,
            }
            if self.are_ellipses_intersecting(ellipse_sight, ellipse_enemy):
                enemy_dist = self.calc_distance(e)
                if enemy_dist < min_dist:
                    min_dist = enemy_dist
                    attack_target = e
        # print(attack_target.name if attack_target else "None",self.current_time,self.last_attack_time)
        if attack_target != None:
            if self.target == None:
                self.target = attack_target
            else:
                if self.target.life < 0:
                    self.target = attack_target
                else:
                    attack_target = self.target
            self.enemis_in_range = True
            if self.current_time - self.last_attack_time >= self.attack_speed:
                self.last_attack_time = self.current_time
                proj = Projectile(self.Projectile, self.type)
                proj.initiate(
                    attack_target,
                    self.posX,
                    (
                        self.posY + 0.5 * self.H
                        if self.type == "blue"
                        else self.posY - 0.5 * self.H
                    ),
                )
                arena.all_projectile.append(proj)
        else:
            self.target = None
            self.enemis_in_range = False

    def calc_distance(self, enemy):
        return ((self.posX - enemy.posX) ** 2 + (self.posY - enemy.posY) ** 2) ** 0.5

    def are_ellipses_intersecting(self, ellipse1, ellipse2, sample=360):
        # 橢圓1參數
        cx1, cy1, a1, b1 = ellipse1["cx"], ellipse1["cy"], ellipse1["a"], ellipse1["b"]
        # 橢圓2參數
        cx2, cy2, a2, b2 = ellipse2["cx"], ellipse2["cy"], ellipse2["a"], ellipse2["b"]

        # 快速檢測：外接圓篩選
        distance = np.sqrt((cx2 - cx1) ** 2 + (cy2 - cy1) ** 2)
        if distance > max(a1, b1) + max(a2, b2):
            # print("No Intersection")
            return False  # 一定不相交

        theta = np.linspace(0, 2 * np.pi, sample)
        x1 = cx1 + a1 * np.cos(theta)
        y1 = cy1 + b1 * np.sin(theta)
        x2 = cx2 + a2 * np.cos(theta)
        y2 = cy2 + b2 * np.sin(theta)

        # 判斷橢圓1邊界點是否落在橢圓2內
        for x, y in zip(x1, y1):
            if ((x - cx2) ** 2) / a2**2 + ((y - cy2) ** 2) / b2**2 <= 1:
                return True  # 存在交集

        # 判斷橢圓2邊界點是否落在橢圓1內
        for x, y in zip(x2, y2):
            if ((x - cx1) ** 2) / a1**2 + ((y - cy1) ** 2) / b1**2 <= 1:
                return True  # 存在交集

        return False  # 無交集

    def rage_buff(self):
        self.last_rage_time = self.current_time
        self.in_rage = True

    def slow_down_debuff(self):
        self.last_slow_time = self.current_time
        self.need_slow = True

    def draw(self, screen, enemis_in_range=False):
        pygame.draw.rect(screen, BLUE if self.type == "blue" else RED, self.gameObject)
        # Draw health bar (background in gray and current health in corresponding color)
        health_bar_width = self.gameObject.width
        health_bar_height = 10
        # Gray background health bar
        if self.type == "blue":
            # Blue tower: health bar below the tower
            health_bar_y = self.gameObject.bottom + 3
        else:
            # Red tower: health bar above the tower
            health_bar_y = self.gameObject.top - 13

        # Draw the health bar background (gray)
        pygame.draw.rect(
            screen,
            GRAY,
            (self.gameObject.x, health_bar_y, health_bar_width, health_bar_height),
        )

        # Draw the health bar (colored based on life)
        health_percentage = self.life / self.total_life
        pygame.draw.rect(
            screen,
            LIGHT_BLUE if self.type == "blue" else LIGHT_RED,
            (
                self.gameObject.x,
                health_bar_y,
                health_bar_width * health_percentage,
                health_bar_height,
            ),
        )

        # Display the current health value in the middle of the health bar
        health_text = f"{round(self.life)}/{self.total_life}"
        if self.in_rage and self.need_slow:
            color = RAGE_SLOW_MIXED
        elif self.in_rage:
            color = RAGE_PURPLE
        elif self.need_slow:
            color = SLOW_BLUE
        else:
            color = (255, 255, 255)
        text_surface = self.font.render(health_text, True, color)  # White text
        text_rect = text_surface.get_rect(
            center=(self.gameObject.centerx, health_bar_y + health_bar_height // 2)
        )
        screen.blit(text_surface, text_rect)

        # Draw the attack range
        attack_range_long_axis = (
            (self.attack_range / 1000 + 2) * 2 * GRID_WIDTH
        )  # Long axis of the ellipse
        attack_range_short_axis = (
            (self.attack_range / 1000 + 2) * 2 * GRID_HEIGHT
        )  # Short axis of the ellipse
        attack_range_color = BLUE if self.type == "blue" else RED
        line_thickness = 3 if self.enemis_in_range else 1
        pygame.draw.ellipse(
            screen,
            attack_range_color,
            (
                self.gameObject.centerx - attack_range_long_axis / 2,
                self.gameObject.centery - attack_range_short_axis / 2,
                attack_range_long_axis,
                attack_range_short_axis,
            ),
            width=line_thickness,
        )


class PrincessTower:
    def __init__(self, X, Y, name="left tower", type="blue"):
        self.name = name
        self.attack_range = 7500
        self.attack_speed = 800
        self.damage = 50
        self.total_life = 1400
        self.life = 1400
        self.type = type
        self.posX = X * GRID_WIDTH
        self.posY = Y * GRID_HEIGHT
        self.W = PRINCESS_TOWER_WIDTH * GRID_WIDTH
        self.H = PRINCESS_TOWER_HEIGHT * GRID_HEIGHT
        self.gameObject = pygame.Rect(
            self.posX - self.W / 2, self.posY - self.H / 2, self.W, self.H
        )
        self.enemis_in_range = False
        self.font = pygame.font.SysFont("Arial", 12, bold=True)
        self.current_time = pygame.time.get_ticks()
        self.last_attack_time = 0
        self.Projectile = "TowerPrincessProjectile"
        self.target = None

        self.last_rage_time = 0
        self.has_rage = False
        self.in_rage = False

        self.last_slow_time = 0
        self.has_slow = False
        self.need_slow = False

        self.original_HitSpeed = self.attack_speed

    def is_destroyed(self):
        return self.life <= 0

    def attack(self, arena, enemys):
        self.current_time = pygame.time.get_ticks()
        min_dist = 100000000
        attack_target = None
        if self.in_rage:
            if self.has_rage == False:
                self.has_rage = True
                self.attack_speed *= 0.65
            if self.current_time - self.last_rage_time > 2000:
                self.in_rage = False
                self.has_rage = False
                self.attack_speed = self.original_HitSpeed

        if self.need_slow:
            if self.has_slow == False:
                self.has_slow = True
                self.attack_speed *= 1.35
            if self.current_time - self.last_slow_time > 2000:
                self.need_slow = False
                self.has_slow = False
                self.attack_speed = self.original_HitSpeed

        for e in enemys:
            ellipse_sight = {
                "cx": self.gameObject.centerx,
                "cy": self.gameObject.centery,
                "a": self.attack_range / 1000 * GRID_WIDTH,
                "b": self.attack_range / 1000 * GRID_HEIGHT,
            }
            ellipse_enemy = {
                "cx": e.posX,
                "cy": e.posY,
                "a": 3 * e.CollisionRadius / 1000 * GRID_WIDTH,
                "b": 3 * e.CollisionRadius / 1000 * GRID_HEIGHT,
            }
            if self.are_ellipses_intersecting(ellipse_sight, ellipse_enemy):
                enemy_dist = self.calc_distance(e)
                if enemy_dist < min_dist:
                    min_dist = enemy_dist
                    attack_target = e
        # print(attack_target.name if attack_target else "None",self.current_time,self.last_attack_time)
        if attack_target != None:
            if self.target == None:
                self.target = attack_target
            else:
                if self.target.life < 0:
                    self.target = attack_target
                else:
                    attack_target = self.target
            self.enemis_in_range = True
            if self.current_time - self.last_attack_time >= self.attack_speed:
                self.last_attack_time = self.current_time
                proj = Projectile(self.Projectile, self.type)
                proj.initiate(
                    attack_target,
                    self.posX,
                    self.posY,
                    # (
                    #    self.posY + 0.5 * self.H
                    #    if self.type == "blue"
                    #    else self.posY - 0.5 * self.H
                    # ),
                )
                arena.all_projectile.append(proj)
        else:
            self.target = None
            self.enemis_in_range = False

    def calc_distance(self, enemy):
        return ((self.posX - enemy.posX) ** 2 + (self.posY - enemy.posY) ** 2) ** 0.5

    def are_ellipses_intersecting(self, ellipse1, ellipse2, sample=360):
        # 橢圓1參數
        cx1, cy1, a1, b1 = ellipse1["cx"], ellipse1["cy"], ellipse1["a"], ellipse1["b"]
        # 橢圓2參數
        cx2, cy2, a2, b2 = ellipse2["cx"], ellipse2["cy"], ellipse2["a"], ellipse2["b"]

        # 快速檢測：外接圓篩選
        distance = np.sqrt((cx2 - cx1) ** 2 + (cy2 - cy1) ** 2)
        if distance > max(a1, b1) + max(a2, b2):
            # print("No Intersection")
            return False  # 一定不相交

        theta = np.linspace(0, 2 * np.pi, sample)
        x1 = cx1 + a1 * np.cos(theta)
        y1 = cy1 + b1 * np.sin(theta)
        x2 = cx2 + a2 * np.cos(theta)
        y2 = cy2 + b2 * np.sin(theta)

        # 判斷橢圓1邊界點是否落在橢圓2內
        for x, y in zip(x1, y1):
            if ((x - cx2) ** 2) / a2**2 + ((y - cy2) ** 2) / b2**2 <= 1:
                return True  # 存在交集

        # 判斷橢圓2邊界點是否落在橢圓1內
        for x, y in zip(x2, y2):
            if ((x - cx1) ** 2) / a1**2 + ((y - cy1) ** 2) / b1**2 <= 1:
                return True  # 存在交集

        return False  # 無交集

    def rage_buff(self):
        self.last_rage_time = self.current_time
        self.in_rage = True

    def slow_down_debuff(self):
        self.last_slow_time = self.current_time
        self.need_slow = True

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE if self.type == "blue" else RED, self.gameObject)
        # Draw health bar (background in gray and current health in corresponding color)
        health_bar_width = self.gameObject.width
        health_bar_height = 10
        # Gray background health bar
        if self.type == "blue":
            # Blue tower: health bar below the tower
            health_bar_y = self.gameObject.bottom + 3
        else:
            # Red tower: health bar above the tower
            health_bar_y = self.gameObject.top - 15

        # Draw the health bar background (gray)
        pygame.draw.rect(
            screen,
            GRAY,
            (self.gameObject.x, health_bar_y, health_bar_width, health_bar_height),
        )

        # Draw the health bar (colored based on life)
        health_percentage = self.life / self.total_life
        pygame.draw.rect(
            screen,
            LIGHT_BLUE if self.type == "blue" else LIGHT_RED,
            (
                self.gameObject.x,
                health_bar_y,
                health_bar_width * health_percentage,
                health_bar_height,
            ),
        )

        # Display the current health value in the middle of the health bar
        health_text = f"{round(self.life)}/{self.total_life}"
        if self.in_rage and self.need_slow:
            color = RAGE_SLOW_MIXED
        elif self.in_rage:
            color = RAGE_PURPLE
        elif self.need_slow:
            color = SLOW_BLUE
        else:
            color = (255, 255, 255)
        text_surface = self.font.render(health_text, True, color)  # White text
        text_rect = text_surface.get_rect(
            center=(self.gameObject.centerx, health_bar_y + health_bar_height // 2)
        )
        screen.blit(text_surface, text_rect)

        # Draw attack range
        attack_range_long_axis = (
            (self.attack_range / 1000 + 1.5) * 2 * GRID_WIDTH
        )  # Long axis of the ellipse
        attack_range_short_axis = (
            (self.attack_range / 1000 + 1.5) * 2 * GRID_HEIGHT
        )  # Short axis of the ellipse
        attack_range_color = BLUE if self.type == "blue" else RED
        line_thickness = 3 if self.enemis_in_range else 1
        pygame.draw.ellipse(
            screen,
            attack_range_color,
            (
                self.gameObject.centerx - attack_range_long_axis / 2,
                self.gameObject.centery - attack_range_short_axis / 2,
                attack_range_long_axis,
                attack_range_short_axis,
            ),
            width=line_thickness,
        )


class Bridge:
    def __init__(self, X, name="left bridge"):
        self.name = name
        self.posX = X * GRID_WIDTH
        self.posY = BRIDGE_Y * GRID_HEIGHT
        self.W = BRIDGE_WIDTH * GRID_WIDTH
        self.H = BRIDGE_HEIGHT * GRID_HEIGHT


multiple_army_pos_offset = {
    2: [[-0.5 * GRID_WIDTH, 0], [0.5 * GRID_WIDTH, 0]],
    3: [[-0.5 * GRID_WIDTH, 0], [0.5 * GRID_WIDTH, 0], [0, -GRID_HEIGHT]],
    4: [
        [-0.55 * GRID_WIDTH, -0.9 * GRID_HEIGHT],
        [0.55 * GRID_WIDTH, -0.9 * GRID_HEIGHT],
        [-0.55 * GRID_WIDTH, 0.9 * GRID_HEIGHT],
        [0.55 * GRID_WIDTH, 0.9 * GRID_HEIGHT],
    ],
    5: [
        [-0.5 * GRID_WIDTH, 0],  # 第一個部隊
        [0.5 * GRID_WIDTH, 0],  # 第二個部隊
        [-GRID_WIDTH, -0.8 * GRID_HEIGHT],  # 第三個部隊
        [GRID_WIDTH, -0.8 * GRID_HEIGHT],  # 第四個部隊
        [0, -1.6 * GRID_HEIGHT],  # 第五個部隊
    ],
    6: [
        [-0.5 * GRID_WIDTH, 0],  # 第一個部隊
        [0.5 * GRID_WIDTH, 0],  # 第二個部隊
        [-GRID_WIDTH, -0.7 * GRID_HEIGHT],  # 第三個部隊
        [GRID_WIDTH, -0.7 * GRID_HEIGHT],  # 第四個部隊
        [-0.5 * GRID_WIDTH, -1.4 * GRID_HEIGHT],  # 第五個部隊
        [0.5 * GRID_WIDTH, -1.4 * GRID_HEIGHT],  # 第六個部隊
    ],
    14: [
        [-0.5 * GRID_WIDTH, 0],  # 第一個部隊
        [0.5 * GRID_WIDTH, 0],  # 第二個部隊
        [-GRID_WIDTH, -0.5 * GRID_HEIGHT],  # 第三個部隊
        [GRID_WIDTH, -0.5 * GRID_HEIGHT],  # 第四個部隊
        [-0.75 * GRID_WIDTH, -GRID_HEIGHT],  # 第五個部隊
        [0.75 * GRID_WIDTH, -GRID_HEIGHT],  # 第六個部隊
        [-GRID_WIDTH, -1.5 * GRID_HEIGHT],  # 第七個部隊
        [GRID_WIDTH, -1.5 * GRID_HEIGHT],  # 第八個部隊
        [-0.25 * GRID_WIDTH, -2 * GRID_HEIGHT],  # 第九個部隊
        [0.25 * GRID_WIDTH, -2 * GRID_HEIGHT],  # 第十個部隊
        [-0.75 * GRID_WIDTH, -2.5 * GRID_HEIGHT],  # 第十一個部隊
        [0.75 * GRID_WIDTH, -2.5 * GRID_HEIGHT],  # 第十二個部隊
        [-GRID_WIDTH, -3 * GRID_HEIGHT],  # 第十三個部隊
        [GRID_WIDTH, -3 * GRID_HEIGHT],  # 第十四個部隊
    ],
}


def get_map_boundaries():
    # Calculate boundaries based on the grid size and map size
    left_boundary = 0  # GRID_WIDTH
    right_boundary = MAP_SIZE[0] * GRID_WIDTH  # 19 * GRID_WIDTH
    top_boundary = 0  # 10.3 * GRID_HEIGHT
    bottom_boundary = MAP_SIZE[1] * GRID_HEIGHT  # 42.5 * GRID_HEIGHT

    return left_boundary, top_boundary, right_boundary, bottom_boundary


class Arena:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

        # 玩家和敵人的主堡（4x4）
        self.player_castle = KingTower(
            PLAYER_KING_TOWER_X,
            PLAYER_KING_TOWER_Y,
            name="Player Main Tower",
            type="blue",
        )
        self.enemy_castle = KingTower(
            ENEMY_KING_TOWER_X,
            ENEMY_KING_TOWER_Y,
            name="Enemy Main Tower",
            type="red",
        )

        # 防禦塔（3x3）
        self.player_left_tower = PrincessTower(
            PLAYER_PRINCESS_TOWER_LEFT_X,
            PLAYER_PRINCESS_TOWER_LEFT_Y,
            name="Player Left Tower",
            type="blue",
        )
        self.player_right_tower = PrincessTower(
            PLAYER_PRINCESS_TOWER_RIGHT_X,
            PLAYER_PRINCESS_TOWER_RIGHT_Y,
            name="Player Right Tower",
            type="blue",
        )

        self.enemy_left_tower = PrincessTower(
            ENEMY_PRINCESS_TOWER_LEFT_X,
            ENEMY_PRINCESS_TOWER_LEFT_Y,
            name="Enemy Left Tower",
            type="red",
        )
        self.enemy_right_tower = PrincessTower(
            ENEMY_PRINCESS_TOWER_RIGHT_X,
            ENEMY_PRINCESS_TOWER_RIGHT_Y,
            name="Enemy Right Tower",
            type="red",
        )

        # 橋
        self.left_bridge = Bridge(BRIDGE_LEFT_X)
        self.right_bridge = Bridge(BRIDGE_RIGHT_X)

        # boundary
        self.left_boundary = 0
        self.right_boundary = MAP_SIZE[0] * GRID_WIDTH
        self.top_boundary = 0
        self.bottom_boundary = MAP_SIZE[1] * GRID_HEIGHT

        # player/enymy角色的queue
        self.player_queue = []
        self.enemy_queue = []

        self.all_projectile = []

        self.all_spell = []

    def Grid_to_XYpos(self, Gx, Gy):
        posx = (
            Gx * (self.right_boundary - self.left_boundary) / MAP_SIZE[0]
            + self.left_boundary
            + GRID_WIDTH / 2
        )
        posy = (
            Gy * (self.bottom_boundary - self.top_boundary) / MAP_SIZE[1]
            + self.top_boundary
            + GRID_HEIGHT / 2
        )
        return posx, posy

    def push_x(self, px):
        overlap = px - self.posX
        self.posX += overlap / 2 * DELTA_TIME

    def push_y(self, py):
        overlap = py - self.posY
        self.posY += overlap / 2 * DELTA_TIME

    def avoid_out_of_bound(self, character):
        px, py = character.posX, character.posY
        # 四周
        if px < self.left_boundary:
            character.posX = (
                self.left_boundary + character.CollisionRadius / 1000 * GRID_WIDTH
            )
        if px > self.right_boundary:
            character.posX = (
                self.right_boundary - character.CollisionRadius / 1000 * GRID_WIDTH
            )
        if py < self.top_boundary:
            character.posY = (
                self.top_boundary + character.CollisionRadius / 1000 * GRID_HEIGHT
            )
        if py > self.bottom_boundary:
            character.posY = (
                self.bottom_boundary - character.CollisionRadius / 1000 * GRID_HEIGHT
            )

        # 防禦塔，邊界
        if (
            self.Grid_to_XYpos(0, 0)[1] - 0.5 * GRID_HEIGHT
            <= py
            <= self.Grid_to_XYpos(0, 0)[1] + 0.5 * GRID_HEIGHT
            or self.Grid_to_XYpos(0, 31)[1] - 0.5 * GRID_HEIGHT
            <= py
            <= self.Grid_to_XYpos(0, 31)[1] + 0.5 * GRID_HEIGHT
        ):
            if px < self.Grid_to_XYpos(6, 0)[0]:
                character.posX = self.Grid_to_XYpos(6, 0)[0]
            if px > self.Grid_to_XYpos(11, 0)[0]:
                character.posX = self.Grid_to_XYpos(11, 0)[0]

        for t in [
            self.enemy_left_tower,
            self.enemy_right_tower,
            self.enemy_castle,
            self.player_left_tower,
            self.player_right_tower,
            self.player_castle,
        ]:
            if (
                t.gameObject.left <= px <= t.gameObject.right
                and t.gameObject.top <= py <= t.gameObject.bottom
            ):
                diffx = (px - t.gameObject.left) / t.gameObject.width
                if diffx < 0.5:
                    character.posX = (
                        t.gameObject.left
                        - character.CollisionRadius / 1000 * GRID_WIDTH
                    )
                else:
                    character.posX = (
                        t.gameObject.right
                        + character.CollisionRadius / 1000 * GRID_WIDTH
                    )

                diffy = (py - t.gameObject.top) / t.gameObject.height
                if diffy < 0.5:
                    character.posY = (
                        t.gameObject.top
                        - character.CollisionRadius / 1000 * GRID_HEIGHT
                    )
                else:
                    character.posY = (
                        t.gameObject.bottom
                        + character.CollisionRadius / 1000 * GRID_HEIGHT
                    )

        # 河流
        if character.can_fly == False and character.name != "HogRider":
            if (
                self.Grid_to_XYpos(0, 15)[1] - GRID_HEIGHT
                <= py
                <= self.Grid_to_XYpos(0, 16)[1] + GRID_HEIGHT
            ):
                character.posY = (
                    self.Grid_to_XYpos(0, 16)[1]
                    + GRID_HEIGHT
                    + 2 * character.CollisionRadius / 1000 * GRID_HEIGHT
                    if character.type == "player"
                    else self.Grid_to_XYpos(0, 15)[1]
                    - GRID_HEIGHT
                    - 2 * character.CollisionRadius / 1000 * GRID_HEIGHT
                )
                # x1=self.Grid_to_XYpos(1,15)[0]
                # x2=self.Grid_to_XYpos(3,15)[0]
                # x3=self.Grid_to_XYpos(12,15)[0]
                # x4=self.Grid_to_XYpos(14,15)[0]
                # if not ((x1-0.5*GRID_WIDTH<=px<=x2+0.5*GRID_WIDTH) or (x3-0.5*GRID_WIDTH<=px<=x4+0.5*GRID_WIDTH)):
                #     dist=[abs(px-i) for i in [x1,x2,x3,x4]]
                #     min_index=dist.index(min(dist))
                #     character.posX=dist[min_index]

    def place_card(self, card, GridX, GridY, _type="player"):
        if card != None:
            px, py = self.Grid_to_XYpos(GridX, GridY)
            print(
                f"{_type} place card:{card.name},(Gx,Gy)=({GridX},{GridY}),(posx,posy)=({px},{py})"
            )
            if type(card) == Character:
                if card.summon_num == 1:  # Single Unit
                    card.arena = self
                    card.enemy_left_tower = (
                        self.enemy_left_tower
                        if _type == "player"
                        else self.player_left_tower
                    )
                    card.enemy_right_tower = (
                        self.enemy_right_tower
                        if _type == "player"
                        else self.player_right_tower
                    )
                    card.enemy_main_tower = (
                        self.enemy_castle if _type == "player" else self.player_castle
                    )
                    card.left_bridge = self.left_bridge
                    card.right_bridge = self.right_bridge
                    card.type = _type
                    card.posX = px
                    card.posY = py
                    (
                        self.player_queue.append(card)
                        if _type == "player"
                        else self.enemy_queue.append(card)
                    )
                else:  # 一張卡多個角色
                    enemy_left_tower = (
                        self.enemy_left_tower
                        if _type == "player"
                        else self.player_left_tower
                    )
                    enemy_right_tower = (
                        self.enemy_right_tower
                        if _type == "player"
                        else self.player_right_tower
                    )
                    enemy_main_tower = (
                        self.enemy_castle if _type == "player" else self.player_castle
                    )
                    if card.name == "GoblinGang":
                        for i in [2, 3, 4]:
                            c_i = Character(
                                "Goblins",
                                self,
                                enemy_left_tower,
                                enemy_right_tower,
                                enemy_main_tower,
                                self.left_bridge,
                                self.right_bridge,
                                pos_x=px
                                + multiple_army_pos_offset[card.summon_num][i][0],
                                pos_y=py
                                + multiple_army_pos_offset[card.summon_num][i][1],
                                type=_type,
                            )
                            self.avoid_out_of_bound(c_i)
                            (
                                self.player_queue.append(c_i)
                                if _type == "player"
                                else self.enemy_queue.append(c_i)
                            )
                        for i in [0, 1]:
                            c_i = Character(
                                "SpearGoblins",
                                self,
                                enemy_left_tower,
                                enemy_right_tower,
                                enemy_main_tower,
                                self.left_bridge,
                                self.right_bridge,
                                pos_x=px
                                + multiple_army_pos_offset[card.summon_num][i][0],
                                pos_y=py
                                + multiple_army_pos_offset[card.summon_num][i][1],
                                type=_type,
                            )
                            self.avoid_out_of_bound(c_i)
                            (
                                self.player_queue.append(c_i)
                                if _type == "player"
                                else self.enemy_queue.append(c_i)
                            )

                    else:
                        for i in range(card.summon_num):
                            c_i = Character(
                                card.name,
                                self,
                                enemy_left_tower,
                                enemy_right_tower,
                                enemy_main_tower,
                                self.left_bridge,
                                self.right_bridge,
                                pos_x=px
                                + multiple_army_pos_offset[card.summon_num][i][0],
                                pos_y=py
                                + multiple_army_pos_offset[card.summon_num][i][1],
                                type=_type,
                            )
                            self.avoid_out_of_bound(c_i)
                            (
                                self.player_queue.append(c_i)
                                if _type == "player"
                                else self.enemy_queue.append(c_i)
                            )

            elif type(card) == Building:
                card.initiate(px, py)
                card.type = _type
                (
                    self.player_queue.append(card)
                    if _type == "player"
                    else self.enemy_queue.append(card)
                )

            elif issubclass(type(card), Spell):
                card.__init__(targetX=px, targetY=py, type=_type)
                self.all_spell.append(card)

    def update(self):
        # card move & attack
        for p in self.player_queue:
            (
                p.act(self.enemy_queue, self.player_queue, self)
                if type(p) == Character
                else p.act(self.enemy_queue, self)
            )
        for q in self.enemy_queue:
            (
                q.act(self.player_queue, self.enemy_queue, self)
                if type(q) == Character
                else q.act(self.player_queue, self)
            )

        for s in self.all_spell:
            s.act(self)

        # tower attack
        if self.player_castle.life < self.player_castle.total_life:
            self.player_castle.attack(self, self.enemy_queue)
        if self.enemy_castle.life < self.enemy_castle.total_life:
            self.enemy_castle.attack(self, self.player_queue)

        self.player_left_tower.attack(self, self.enemy_queue)
        self.player_right_tower.attack(self, self.enemy_queue)
        self.enemy_left_tower.attack(self, self.player_queue)
        self.enemy_right_tower.attack(self, self.player_queue)

        # remove dead army
        for p in self.player_queue:
            if p.life <= 0:
                p.dead_effect(self)
                self.player_queue.remove(p)

        for q in self.enemy_queue:
            if q.life <= 0:
                q.dead_effect(self)
                self.enemy_queue.remove(q)

        for s in self.all_spell:
            if type(s) == Arrow:
                if s.end_cnt == s.hit_cnt:
                    self.all_spell.remove(s)
            elif type(s) == Fireball or type(s) == Rocket:
                if s.has_attacked:
                    self.all_spell.remove(s)
            elif type(s) == Rage or type(s) == Heal or type(s) == Poison:
                if s.timer > s.duration:
                    self.all_spell.remove(s)

        for proj in self.all_projectile:
            proj.update(self)
            if proj.destroyed:
                self.all_projectile.remove(proj)

    def update_screen(self, screen):
        # update game window
        for p in self.player_queue:
            p.draw(screen, show_act=True)

        for q in self.enemy_queue:
            q.draw(screen, show_act=True)

        for proj in self.all_projectile:
            proj.draw(screen)

        for s in self.all_spell:
            s.draw(screen)

    def draw_castles_and_towers(self, screen):
        # 玩家和敵人的主堡
        self.player_castle.draw(screen)
        self.enemy_castle.draw(screen)

        # 玩家和敵人的防禦塔
        self.player_left_tower.draw(screen)
        self.player_right_tower.draw(screen)
        self.enemy_left_tower.draw(screen)
        self.enemy_right_tower.draw(screen)
