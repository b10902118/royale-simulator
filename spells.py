from Constant import GRID_WIDTH, GRID_HEIGHT, DELTA_TIME
import numpy as np
import pygame, os

# from arena import Arena

PURPLE = (128, 0, 128)


class Spell:
    def __init__(self, elixir, radius, target_X, target_Y, duration=-1):
        self.elixir_cost = elixir
        self.radiusX = radius / 1000 * GRID_WIDTH
        self.radiusY = radius / 1000 * GRID_HEIGHT
        self.duration = duration
        self.targetX = target_X
        self.targetY = target_Y
        self.font = pygame.font.SysFont("Arial", 15, bold=True)

    def are_ellipses_intersecting(self, ellipse_other, sample=360):
        # 橢圓1參數
        cx1, cy1, a1, b1 = self.targetX, self.targetY, self.radiusX, self.radiusY
        # 橢圓2參數
        cx2, cy2, a2, b2 = (
            ellipse_other["cx"],
            ellipse_other["cy"],
            ellipse_other["a"],
            ellipse_other["b"],
        )

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


class Arrow(Spell):
    def __init__(self, targetX=0, targetY=0, type="player"):
        super().__init__(3, 4000, targetX, targetY)
        self.name = "Arrows"
        self.speed = 800
        self.damage = 115
        self.tower_damage = self.damage * 0.4
        self.type = type

        self.deck_img = (
            pygame.image.load(f"card_img//{self.name}.webp")
            if os.path.exists(f"card_img//{self.name}.webp")
            else None
        )

        if self.type == "player":
            self.posX = 10 * GRID_WIDTH
            self.posY = 39.5 * GRID_HEIGHT
        else:
            self.posX = 10 * GRID_WIDTH
            self.posY = 13.5 * GRID_HEIGHT

        self.originX = self.posX
        self.originY = self.posY
        self.origin_radius = 0.1

        # attack num : 總共射幾次箭
        self.attack_num = 1

        self.arrow_set = [
            [self.posX, self.posY, self.origin_radius, self.origin_radius]
            for _ in range(self.attack_num)
        ]
        self.has_attacked = [False for _ in range(self.attack_num)]

        self.total_dist = (
            (self.targetX - self.originX) ** 2 + (self.targetY - self.originY) ** 2
        ) ** 0.5

        self.hit_interval = 300
        self.end_cnt = 0
        self.hit_cnt = 1
        self.timer = 0
        self.last_hit_time = 0

    def act(self, arena):
        self.timer = pygame.time.get_ticks()
        if self.timer - self.last_hit_time > self.hit_interval:
            self.last_hit_time = self.timer
            self.hit_cnt = min(self.attack_num, self.hit_cnt + 1)

        for i in range(self.end_cnt, self.hit_cnt):
            px, py, rx, ry = self.arrow_set[i]
            dist_now = ((px - self.targetX) ** 2 + (py - self.targetY) ** 2) ** 0.5
            # print((px,py),(self.targetX,self.targetY),dist_now,self.total_dist,self.total_dist-dist_now)
            if (
                dist_now < 5 and self.has_attacked[i] == False
            ):  # close to target position
                self.end_cnt = min(self.attack_num, self.end_cnt + 1)
                self.arrow_set[i][2] = self.radiusX
                self.arrow_set[i][3] = self.radiusY
                self.hit(
                    arena.enemy_queue if self.type == "player" else arena.player_queue
                )
                if self.type == "player":
                    enemy_l_tower, enemy_r_tower, enemy_main_tower = (
                        arena.enemy_left_tower,
                        arena.enemy_right_tower,
                        arena.enemy_castle,
                    )
                else:
                    enemy_l_tower, enemy_r_tower, enemy_main_tower = (
                        arena.player_left_tower,
                        arena.player_right_tower,
                        arena.player_castle,
                    )
                for t in [enemy_l_tower, enemy_r_tower, enemy_main_tower]:
                    rect = t.gameObject
                    rect_points = [
                        (rect.left, rect.top),
                        (rect.right, rect.top),
                        (rect.right, rect.bottom),
                        (rect.left, rect.bottom),
                    ]
                    for x, y in rect_points:
                        if (
                            (x - px) ** 2 / self.radiusX**2
                            + (y - py) ** 2 / self.radiusY**2
                        ) <= 1:
                            t.life -= self.tower_damage
                            self.has_attacked[i] = True
                            break

                    # 檢查橢圓的中心點與矩形最近的點之間的距離是否小於橢圓半徑
                    nearest_x = max(rect.left, min(px, rect.right))
                    nearest_y = max(rect.top, min(py, rect.bottom))
                    dx = px - nearest_x
                    dy = py - nearest_y

                    if (
                        dx**2 / self.radiusX**2 + dy**2 / self.radiusY**2
                    ) <= 1 and self.has_attacked[i] == False:
                        t.life -= self.tower_damage
                        self.has_attacked[i] = True

            else:  # fly to target
                self.arrow_set[i][2] = (1 - dist_now / self.total_dist) * self.radiusX
                self.arrow_set[i][3] = (1 - dist_now / self.total_dist) * self.radiusY
                if dist_now != 0:
                    dx = (self.targetX - px) / dist_now
                    dy = (self.targetY - py) / dist_now
                else:
                    dx = (self.targetX - px) / 100
                    dy = (self.targetY - py) / 100
                self.arrow_set[i][0] += (
                    dx * (self.speed / 100 * GRID_WIDTH) * DELTA_TIME
                )
                self.arrow_set[i][1] += (
                    dy * (self.speed / 100 * GRID_HEIGHT) * DELTA_TIME
                )

    def hit(self, enemies):
        for e in enemies:
            if hasattr(e, "summon_num"):
                ellipse_enemy = {
                    "cx": e.posX,
                    "cy": e.posY,
                    "a": e.CollisionRadius / 1000 * GRID_WIDTH,
                    "b": e.CollisionRadius / 1000 * GRID_HEIGHT,
                }
            else:
                ellipse_enemy = {
                    "cx": e.posX,
                    "cy": e.posY,
                    "a": 0.5 * e.W,
                    "b": 0.5 * e.H,
                }
            if self.are_ellipses_intersecting(ellipse_enemy):
                e.life -= self.damage

    def draw(self, screen):
        for i in range(self.end_cnt, self.hit_cnt):
            px, py, rx, ry = self.arrow_set[i]
            text_surface = self.font.render(
                self.name if self.attack_num == 1 else self.name + "_" + str(i + 1),
                True,
                (255, 255, 255),
            )
            text_rect = text_surface.get_rect(center=(px, py))
            screen.blit(text_surface, text_rect)
            pygame.draw.ellipse(
                screen, PURPLE, (px - rx, py - ry, 2 * rx, 2 * ry), width=2
            )


class Fireball(Spell):
    def __init__(self, targetX=0, targetY=0, type="player"):
        super().__init__(4, 2500, targetX, targetY)
        self.name = "FireBall"
        self.speed = 600
        self.damage = 325
        self.tower_damage = self.damage * 0.4
        self.pushback = 1800
        self.type = type

        self.deck_img = (
            pygame.image.load(f"card_img//{self.name}.webp")
            if os.path.exists(f"card_img//{self.name}.webp")
            else None
        )

        if self.type == "player":
            self.posX = 10 * GRID_WIDTH
            self.posY = 39.5 * GRID_HEIGHT
        else:
            self.posX = 10 * GRID_WIDTH
            self.posY = 13.5 * GRID_HEIGHT

        self.originX = self.posX
        self.originY = self.posY

        self.has_attacked = False

        self.total_dist = (
            (self.targetX - self.originX) ** 2 + (self.targetY - self.originY) ** 2
        ) ** 0.5

    def act(self, arena):
        px, py = self.posX, self.posY
        dist_now = ((px - self.targetX) ** 2 + (py - self.targetY) ** 2) ** 0.5
        if dist_now < 5 and self.has_attacked == False:  # close to target position
            self.has_attacked = True
            self.hit(arena.enemy_queue if self.type == "player" else arena.player_queue)
            if self.type == "player":
                enemy_l_tower, enemy_r_tower, enemy_main_tower = (
                    arena.enemy_left_tower,
                    arena.enemy_right_tower,
                    arena.enemy_castle,
                )
            else:
                enemy_l_tower, enemy_r_tower, enemy_main_tower = (
                    arena.player_left_tower,
                    arena.player_right_tower,
                    arena.player_castle,
                )
            for t in [enemy_l_tower, enemy_r_tower, enemy_main_tower]:
                rect = t.gameObject
                rect_points = [
                    (rect.left, rect.top),
                    (rect.right, rect.top),
                    (rect.right, rect.bottom),
                    (rect.left, rect.bottom),
                ]
                for x, y in rect_points:
                    if (
                        (x - px) ** 2 / self.radiusX**2
                        + (y - py) ** 2 / self.radiusY**2
                    ) <= 1:
                        t.life -= self.tower_damage
                        self.has_attacked = True
                        break

                # 檢查橢圓的中心點與矩形最近的點之間的距離是否小於橢圓半徑
                nearest_x = max(rect.left, min(px, rect.right))
                nearest_y = max(rect.top, min(py, rect.bottom))
                dx = px - nearest_x
                dy = py - nearest_y

                if (
                    dx**2 / self.radiusX**2 + dy**2 / self.radiusY**2
                ) <= 1 and self.has_attacked == False:
                    t.life -= self.tower_damage
                    self.has_attacked = True

        else:  # fly to target
            if dist_now != 0:
                dx = (self.targetX - px) / dist_now
                dy = (self.targetY - py) / dist_now
            else:
                dx = (self.targetX - px) / 100
                dy = (self.targetY - py) / 100
            self.posX += dx * (self.speed / 100 * GRID_WIDTH) * DELTA_TIME
            self.posY += dy * (self.speed / 100 * GRID_HEIGHT) * DELTA_TIME

    def hit(self, enemies):
        for e in enemies:
            if hasattr(e, "summon_num"):
                ellipse_enemy = {
                    "cx": e.posX,
                    "cy": e.posY,
                    "a": e.CollisionRadius / 1000 * GRID_WIDTH,
                    "b": e.CollisionRadius / 1000 * GRID_HEIGHT,
                }
                if self.are_ellipses_intersecting(ellipse_enemy):
                    e.life -= self.damage
                    if e.IgnorePushback == False:  ##push back
                        push_x = e.posX - self.targetX
                        push_y = e.posY - self.targetY
                        u_x = push_x / ((push_x**2 + push_y**2) ** 0.5)
                        u_y = push_y / ((push_x**2 + push_y**2) ** 0.5)
                        e.pushback(u_x, u_y, self.pushback)

            else:
                ellipse_enemy = {
                    "cx": e.posX,
                    "cy": e.posY,
                    "a": 0.5 * e.W,
                    "b": 0.5 * e.H,
                }
                if self.are_ellipses_intersecting(ellipse_enemy):
                    e.life -= self.damage

    def draw(self, screen):
        text_surface = self.font.render(self.name, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.posX, self.posY))
        screen.blit(text_surface, text_rect)
        pygame.draw.ellipse(
            screen,
            PURPLE,
            (
                self.posX - self.radiusX,
                self.posY - self.radiusY,
                2 * self.radiusX,
                2 * self.radiusY,
            ),
            width=2,
        )


class Rocket(Spell):
    def __init__(self, targetX=0, targetY=0, type="player"):
        super().__init__(6, 2000, targetX, targetY)
        self.name = "Rocket"
        self.speed = 350
        self.damage = 700
        self.tower_damage = self.damage * 0.4
        self.pushback = 1800
        self.type = type

        self.deck_img = (
            pygame.image.load(f"card_img//{self.name}.webp")
            if os.path.exists(f"card_img//{self.name}.webp")
            else None
        )

        if self.type == "player":
            self.posX = 10 * GRID_WIDTH
            self.posY = 39.5 * GRID_HEIGHT
        else:
            self.posX = 10 * GRID_WIDTH
            self.posY = 13.5 * GRID_HEIGHT

        self.originX = self.posX
        self.originY = self.posY

        self.has_attacked = False

        self.total_dist = (
            (self.targetX - self.originX) ** 2 + (self.targetY - self.originY) ** 2
        ) ** 0.5

    def act(self, arena):
        px, py = self.posX, self.posY
        dist_now = ((px - self.targetX) ** 2 + (py - self.targetY) ** 2) ** 0.5
        if dist_now < 5 and self.has_attacked == False:  # close to target position
            self.has_attacked = True
            self.hit(arena.enemy_queue if self.type == "player" else arena.player_queue)
            if self.type == "player":
                enemy_l_tower, enemy_r_tower, enemy_main_tower = (
                    arena.enemy_left_tower,
                    arena.enemy_right_tower,
                    arena.enemy_castle,
                )
            else:
                enemy_l_tower, enemy_r_tower, enemy_main_tower = (
                    arena.player_left_tower,
                    arena.player_right_tower,
                    arena.player_castle,
                )
            for t in [enemy_l_tower, enemy_r_tower, enemy_main_tower]:
                rect = t.gameObject
                rect_points = [
                    (rect.left, rect.top),
                    (rect.right, rect.top),
                    (rect.right, rect.bottom),
                    (rect.left, rect.bottom),
                ]
                for x, y in rect_points:
                    if (
                        (x - px) ** 2 / self.radiusX**2
                        + (y - py) ** 2 / self.radiusY**2
                    ) <= 1:
                        t.life -= self.tower_damage
                        self.has_attacked = True
                        break

                # 檢查橢圓的中心點與矩形最近的點之間的距離是否小於橢圓半徑
                nearest_x = max(rect.left, min(px, rect.right))
                nearest_y = max(rect.top, min(py, rect.bottom))
                dx = px - nearest_x
                dy = py - nearest_y

                if (
                    dx**2 / self.radiusX**2 + dy**2 / self.radiusY**2
                ) <= 1 and self.has_attacked == False:
                    t.life -= self.tower_damage
                    self.has_attacked = True

        else:  # fly to target
            if dist_now != 0:
                dx = (self.targetX - px) / dist_now
                dy = (self.targetY - py) / dist_now
            else:
                dx = (self.targetX - px) / 100
                dy = (self.targetY - py) / 100
            self.posX += dx * (self.speed / 100 * GRID_WIDTH) * DELTA_TIME
            self.posY += dy * (self.speed / 100 * GRID_HEIGHT) * DELTA_TIME

    def hit(self, enemies):
        for e in enemies:
            if hasattr(e, "summon_num"):
                ellipse_enemy = {
                    "cx": e.posX,
                    "cy": e.posY,
                    "a": e.CollisionRadius / 1000 * GRID_WIDTH,
                    "b": e.CollisionRadius / 1000 * GRID_HEIGHT,
                }
                if self.are_ellipses_intersecting(ellipse_enemy):
                    e.life -= self.damage
                    if e.IgnorePushback == False:  ##push back
                        push_x = e.posX - self.targetX
                        push_y = e.posY - self.targetY
                        u_x = push_x / ((push_x**2 + push_y**2) ** 0.5)
                        u_y = push_y / ((push_x**2 + push_y**2) ** 0.5)
                        e.pushback(u_x, u_y, self.pushback)

            else:
                ellipse_enemy = {
                    "cx": e.posX,
                    "cy": e.posY,
                    "a": 0.5 * e.W,
                    "b": 0.5 * e.H,
                }
                if self.are_ellipses_intersecting(ellipse_enemy):
                    e.life -= self.damage

    def draw(self, screen):
        text_surface = self.font.render(self.name, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.posX, self.posY))
        screen.blit(text_surface, text_rect)
        pygame.draw.ellipse(
            screen,
            PURPLE,
            (
                self.posX - self.radiusX,
                self.posY - self.radiusY,
                2 * self.radiusX,
                2 * self.radiusY,
            ),
            width=2,
        )


class Rage(Spell):
    def __init__(self, targetX=0, targetY=0, type="player"):
        super().__init__(2, 5000, targetX, targetY)
        self.name = "Rage"
        self.type = type
        self.timer = 0
        self.last_buff_time = 0
        self.duration = 6000
        self.buff_interval = 300
        self.deck_img = (
            pygame.image.load(f"card_img//{self.name}.webp")
            if os.path.exists(f"card_img//{self.name}.webp")
            else None
        )

    def act(self, arena):
        self.timer = pygame.time.get_ticks()
        if self.timer - self.last_buff_time > self.buff_interval:
            self.last_buff_time = self.timer
            self_queue = (
                arena.enemy_queue if self.type != "player" else arena.player_queue
            )
            for c in self_queue:
                if hasattr(c, "summon_num"):
                    ellipse_enemy = {
                        "cx": c.posX,
                        "cy": c.posY,
                        "a": c.CollisionRadius / 1000 * GRID_WIDTH,
                        "b": c.CollisionRadius / 1000 * GRID_HEIGHT,
                    }
                    if self.are_ellipses_intersecting(ellipse_enemy):
                        c.rage_buff()

                else:
                    ellipse_enemy = {
                        "cx": c.posX,
                        "cy": c.posY,
                        "a": 0.5 * c.W,
                        "b": 0.5 * c.H,
                    }
                    if self.are_ellipses_intersecting(ellipse_enemy):
                        c.rage_buff()

            if self.type != "player":
                l_tower, r_tower, main_tower = (
                    arena.enemy_left_tower,
                    arena.enemy_right_tower,
                    arena.enemy_castle,
                )
            else:
                l_tower, r_tower, main_tower = (
                    arena.player_left_tower,
                    arena.player_right_tower,
                    arena.player_castle,
                )
            for t in [l_tower, r_tower, main_tower]:
                rect = t.gameObject
                rect_points = [
                    (rect.left, rect.top),
                    (rect.right, rect.top),
                    (rect.right, rect.bottom),
                    (rect.left, rect.bottom),
                ]
                for x, y in rect_points:
                    if (
                        (x - self.targetX) ** 2 / self.radiusX**2
                        + (y - self.targetY) ** 2 / self.radiusY**2
                    ) <= 1:
                        t.rage_buff()
                        break

                # 檢查橢圓的中心點與矩形最近的點之間的距離是否小於橢圓半徑
                nearest_x = max(rect.left, min(self.targetX, rect.right))
                nearest_y = max(rect.top, min(self.targetY, rect.bottom))
                dx = self.targetX - nearest_x
                dy = self.targetY - nearest_y

                if (dx**2 / self.radiusX**2 + dy**2 / self.radiusY**2) <= 1:
                    t.rage_buff()

    def draw(self, screen):
        text_surface = self.font.render(self.name, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.targetX, self.targetY))
        screen.blit(text_surface, text_rect)
        pygame.draw.ellipse(
            screen,
            PURPLE,
            (
                self.targetX - self.radiusX,
                self.targetY - self.radiusY,
                2 * self.radiusX,
                2 * self.radiusY,
            ),
            width=2,
        )


class Poison(Spell):
    def __init__(self, targetX=0, targetY=0, type="player"):
        super().__init__(4, 3500, targetX, targetY)
        self.name = "Poison"
        self.type = type
        self.timer = 0
        self.last_buff_time = 0
        self.duration = 8000
        self.buff_interval = 1000
        self.damage = 57
        self.has_damage = False
        self.tower_damage = self.damage * 0.4
        self.deck_img = (
            pygame.image.load(f"card_img//{self.name}.webp")
            if os.path.exists(f"card_img//{self.name}.webp")
            else None
        )

    def act(self, arena):
        self.timer = pygame.time.get_ticks()
        if self.timer - self.last_buff_time > self.buff_interval:
            self.last_buff_time = self.timer
            self_queue = (
                arena.enemy_queue if self.type == "player" else arena.player_queue
            )
            for c in self_queue:
                if hasattr(c, "summon_num"):
                    ellipse_enemy = {
                        "cx": c.posX,
                        "cy": c.posY,
                        "a": c.CollisionRadius / 1000 * GRID_WIDTH,
                        "b": c.CollisionRadius / 1000 * GRID_HEIGHT,
                    }
                    if self.are_ellipses_intersecting(ellipse_enemy):
                        c.life -= self.damage

                else:
                    ellipse_enemy = {
                        "cx": c.posX,
                        "cy": c.posY,
                        "a": 0.5 * c.W,
                        "b": 0.5 * c.H,
                    }
                    if self.are_ellipses_intersecting(ellipse_enemy):
                        c.life -= self.damage

            if self.type == "player":
                l_tower, r_tower, main_tower = (
                    arena.enemy_left_tower,
                    arena.enemy_right_tower,
                    arena.enemy_castle,
                )
            else:
                l_tower, r_tower, main_tower = (
                    arena.player_left_tower,
                    arena.player_right_tower,
                    arena.player_castle,
                )
            for t in [l_tower, r_tower, main_tower]:
                rect = t.gameObject
                rect_points = [
                    (rect.left, rect.top),
                    (rect.right, rect.top),
                    (rect.right, rect.bottom),
                    (rect.left, rect.bottom),
                ]
                for x, y in rect_points:
                    if (
                        (x - self.targetX) ** 2 / self.radiusX**2
                        + (y - self.targetY) ** 2 / self.radiusY**2
                    ) <= 1:
                        t.life -= self.tower_damage
                        self.has_damage = True
                        break

                # 檢查橢圓的中心點與矩形最近的點之間的距離是否小於橢圓半徑
                nearest_x = max(rect.left, min(self.targetX, rect.right))
                nearest_y = max(rect.top, min(self.targetY, rect.bottom))
                dx = self.targetX - nearest_x
                dy = self.targetY - nearest_y

                if (
                    dx**2 / self.radiusX**2 + dy**2 / self.radiusY**2
                ) <= 1 and self.has_damage == False:
                    self.has_damage = True
                    t.life -= self.tower_damage
        else:
            self.has_damage = False

    def draw(self, screen):
        text_surface = self.font.render(self.name, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.targetX, self.targetY))
        screen.blit(text_surface, text_rect)
        pygame.draw.ellipse(
            screen,
            PURPLE,
            (
                self.targetX - self.radiusX,
                self.targetY - self.radiusY,
                2 * self.radiusX,
                2 * self.radiusY,
            ),
            width=2,
        )


class Heal(Spell):
    def __init__(self, targetX=0, targetY=0, type="player"):
        super().__init__(3, 3000, targetX, targetY)
        self.name = "Heal"
        self.type = type
        self.timer = 0
        self.last_buff_time = 0
        self.duration = 3050
        self.buff_interval = 50
        self.heal_value = 50
        self.deck_img = (
            pygame.image.load(f"card_img//{self.name}.webp")
            if os.path.exists(f"card_img//{self.name}.webp")
            else None
        )

    def act(self, arena):
        self.timer = pygame.time.get_ticks()
        if self.timer - self.last_buff_time > self.buff_interval:
            self.last_buff_time = self.timer
            self_queue = (
                arena.enemy_queue if self.type != "player" else arena.player_queue
            )
            for c in self_queue:
                if hasattr(c, "summon_num"):
                    ellipse_enemy = {
                        "cx": c.posX,
                        "cy": c.posY,
                        "a": c.CollisionRadius / 1000 * GRID_WIDTH,
                        "b": c.CollisionRadius / 1000 * GRID_HEIGHT,
                    }
                    if self.are_ellipses_intersecting(ellipse_enemy):
                        c.life = min(c.total_life, c.life + self.heal_value)

    def draw(self, screen):
        text_surface = self.font.render(self.name, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.targetX, self.targetY))
        screen.blit(text_surface, text_rect)
        pygame.draw.ellipse(
            screen,
            PURPLE,
            (
                self.targetX - self.radiusX,
                self.targetY - self.radiusY,
                2 * self.radiusX,
                2 * self.radiusY,
            ),
            width=2,
        )
