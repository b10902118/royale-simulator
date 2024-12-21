import csv, math
import pygame
import numpy as np
from Constant import GRID_WIDTH, GRID_HEIGHT, DELTA_TIME

ORANGE = (255, 165, 0)


def read_projectiles_csv(file_path):
    projectiles_data = {}
    # Define the columns we want to extract
    columns_to_extract = [
        "Speed",
        "Damage",
        "CrownTowerDamagePercent",
        "Pushback",
        "Radius",
        "AoeToAir",
        "AoeToGround",
        "OnlyEnemies",
        "BuffTime",
        "ProjectileRadius",
        "ProjectileRange",
        "MinDistance",
    ]

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Name"] != "string":
                name = row["Name"]
                # Initialize a dictionary to hold the extracted data for each projectile
                projectile_info = {}

                for col in columns_to_extract:
                    value = row[col]

                    # Handle boolean fields, setting missing values to "false"
                    if value == "" or value.lower() == "false":
                        projectile_info[col] = False
                    # Handle integer fields, setting missing values to -1
                    elif value == "" or value == "NULL":
                        projectile_info[col] = -1
                    else:
                        # Convert non-empty values to the appropriate type (boolean or integer)
                        if col in [
                            "Damage",
                            "CrownTowerDamagePercent",
                            "Pushback",
                            "Radius",
                            "ProjectileRange",
                            "MinDistance",
                            "Speed",
                        ]:  # These are integers
                            projectile_info[col] = int(value)
                        else:  # Handle boolean fields like "AoeToAir", "AoeToGround", etc.
                            projectile_info[col] = value.lower() == "true"

                # Add the processed data for this projectile to the main dictionary
                projectiles_data[name] = projectile_info

    return projectiles_data


Projectile_data = read_projectiles_csv("./logic_csv/projectiles.csv")


class Projectile:
    def __init__(self, name, type="player"):
        self.type = type
        self.name = name
        self.data = Projectile_data[name]
        self.destroyed = False
        for key, value in self.data.items():
            setattr(self, key, value)
        if self.Radius:
            self.width = self.Radius / 1000 * GRID_WIDTH
            self.height = self.Radius / 1000 * GRID_HEIGHT
        else:
            self.width = 0.2 * GRID_WIDTH
            self.height = 0.2 * GRID_HEIGHT

    def __str__(self):
        # Build a string representation of the object
        attributes = [f"{key}: {value}" for key, value in sorted(self.data.items())]
        return f"Projectile ({self.name})\n" + "\n".join(attributes)

    def initiate(self, target, X, Y):
        self.destroyed = False
        self.target = target
        self.posX = X
        self.posY = Y

    def is_ellipse_touching_line(self, type, left_x, line_y, line_length):
        # 橢圓的長軸和短軸半徑
        a = self.width / 2  # 長軸半徑
        b = self.height / 2  # 短軸半徑

        # 檢查水平線是否與橢圓在 y 軸方向重疊
        if abs(line_y - self.posY) > b:
            if self.type == "player":
                return self.posY - line_y <= b
            else:
                return line_y - self.posY <= b

        # 計算對應的橢圓交點的 x 範圍
        # 橢圓方程化簡為: (x - cx)^2 / a^2 = 1 - (line_y - cy)^2 / b^2
        y_diff = line_y - self.posY
        x_range_squared = a**2 * (1 - (y_diff**2 / b**2))

        if x_range_squared < 0:
            return False  # 無實數解，橢圓與水平線不相交

        # 計算橢圓交點的 x 範圍
        x_offset = math.sqrt(x_range_squared)
        x1 = self.posX - x_offset
        x2 = self.posX + x_offset

        # 檢查交點範圍是否與水平線範圍重疊
        line_right = left_x + line_length
        if x1 <= line_right and x2 >= left_x:
            return True

        return False

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

    def update(self, arena):
        # 目標是防禦塔
        if hasattr(self.target, "summon_num") == False:
            attach_target = self.is_ellipse_touching_line(
                self.type,
                self.target.posX - self.target.W // 2,
                self.target.posY,
                self.target.W,
            )
        else:
            # 單體攻擊
            if self.AoeToGround == False and self.AoeToAir == False:
                ellipse_self = {"cx": self.posX, "cy": self.posY, "a": 1, "b": 1}
            else:
                ellipse_self = {
                    "cx": self.posX,
                    "cy": self.posY,
                    "a": self.width,
                    "b": self.height,
                }
            ellipse_other = {
                "cx": self.target.posX,
                "cy": self.target.posY,
                "a": self.target.CollisionRadius / 1000 * GRID_WIDTH,
                "b": self.target.CollisionRadius / 1000 * GRID_HEIGHT,
            }
            attach_target = self.are_ellipses_intersecting(ellipse_self, ellipse_other)

        if attach_target:
            self.destroyed = True
            if self.AoeToGround == False and self.AoeToAir == False:  # 單體攻擊
                self.target.life -= self.Damage
                if self.name == "ice_wizardProjectile":
                    self.target.slow_down_debuff()
            else:  # AOE攻擊
                enemy_troop = (
                    arena.enemy_queue if self.type == "player" else arena.player_queue
                )
                enemy_left_tower = (
                    arena.enemy_left_tower
                    if self.type == "player"
                    else arena.player_left_tower
                )
                enemy_right_tower = (
                    arena.enemy_right_tower
                    if self.type == "player"
                    else arena.player_right_tower
                )
                enemy_main_tower = (
                    arena.enemy_castle if self.type == "player" else arena.player_castle
                )

                ground_enemys = [e for e in enemy_troop if e.can_fly == False]
                air_enemys = [e for e in enemy_troop if e.can_fly]
                if self.AoeToGround == True:
                    for g in ground_enemys:
                        if ((g.posX - self.target.posX) ** 2) / (
                            self.Radius / 1000 * GRID_WIDTH
                        ) ** 2 + ((g.posY - self.target.posY) ** 2) / (
                            self.Radius / 1000 * GRID_HEIGHT
                        ) ** 2 <= 1:
                            g.life -= self.Damage
                            if self.name == "ice_wizardProjectile":
                                g.slow_down_debuff()
                if self.AoeToAir == True:
                    for a in air_enemys:
                        if ((a.posX - self.target.posX) ** 2) / (
                            self.Radius / 1000 * GRID_WIDTH
                        ) ** 2 + ((a.posY - self.target.posY) ** 2) / (
                            self.Radius / 1000 * GRID_HEIGHT
                        ) ** 2 <= 1:
                            a.life -= self.Damage
                            if self.name == "ice_wizardProjectile":
                                a.slow_down_debuff()
                for t in [enemy_left_tower, enemy_right_tower, enemy_main_tower]:
                    if ((t.posX - self.posX) ** 2) / (
                        self.Radius / 1000 * GRID_WIDTH
                    ) ** 2 + ((t.posY - self.posY) ** 2) / (
                        self.Radius / 1000 * GRID_HEIGHT
                    ) ** 2 <= 1:
                        t.life -= self.Damage
                        if self.name == "ice_wizardProjectile":
                            t.slow_down_debuff()

        else:
            diff_x = self.target.posX - self.posX
            diff_y = self.target.posY - self.posY
            distance = math.sqrt(diff_x**2 + diff_y**2)
            if distance != 0:
                diff_x /= distance
                diff_y /= distance

            self.posX += diff_x * self.Speed / 100 * GRID_WIDTH * DELTA_TIME
            self.posY += diff_y * self.Speed / 100 * GRID_HEIGHT * DELTA_TIME

    def draw(self, screen):
        top_left_x = self.posX - self.width // 2
        top_left_y = self.posY - self.height // 2
        pygame.draw.ellipse(
            screen, ORANGE, (top_left_x, top_left_y, self.width, self.height)
        )


if "__main__" == __name__:
    pygame.init()
    p = Projectile("MusketeerProjectile")
    print(p)
