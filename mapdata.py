import pygame
import random
import json
import os
from entities import Enemy, StrongEnemy, ArcherEnemy, Arrow
from assets import heal_img, powerup_img

from objects import Item

MAP_DATA = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,0,1],
    [1,0,1,0,0,0,0,1,0,1,0,0,0,1,0,0,0,1,0,1],
    [1,0,1,0,1,1,0,1,0,1,0,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,1],
    [1,0,1,1,0,1,1,1,0,0,1,0,0,1,1,0,1,0,0,1],
    [1,0,1,1,0,1,1,1,1,0,1,0,1,1,1,0,1,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,0,1],
    [1,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,1],
    [1,0,1,0,1,1,0,1,0,1,0,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

# タイルクラス
class Tile:
    def __init__(self, x, y, size, tile_type):
        self.x = x
        self.y = y
        self.size = size
        self.tile_type = tile_type  # 0=床, 1=壁, 2=階段
        if tile_type == 0:
            self.color = (200, 200, 200)  # 床：明るいグレー
        elif tile_type == 1:
            self.color = (100, 100, 100)  # 壁：暗いグレー
        elif tile_type == 2:
            self.color = (0, 255, 0)      # 階段：緑色

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
    
    def is_wall(self):
        return self.tile_type == 1

    def is_stairs(self):
        return self.tile_type == 2


# マップのタイルを作る
def create_map():
    tiles = []
    tile_size = 32
    for row_idx, row in enumerate(MAP_DATA):
        for col_idx, tile_type in enumerate(row):
            tile = Tile(col_idx * tile_size, row_idx * tile_size + 64, tile_size, tile_type)
            tiles.append(tile)
    return tiles

def enemy_ai(enemy, player, tiles, enemies, arrows):
    dx = player.x - enemy.x
    dy = player.y - enemy.y
    abs_dx, abs_dy = abs(dx), abs(dy)

    if isinstance(enemy, ArcherEnemy):
        if abs_dx <= 160 and abs_dy == 0 or abs_dy <= 160 and abs_dx == 0:
            if enemy.can_shoot(player, tiles):
                shoot_dx = 32 if dx > 0 else -32 if dx < 0 else 0
                shoot_dy = 32 if dy > 0 else -32 if dy < 0 else 0
                arrows.append(Arrow(enemy.x, enemy.y, shoot_dx, shoot_dy))
                print("アーチャーが矢を放った！")
                return

    # 通常の近接攻撃
    if abs_dx == 0 and abs_dy == 32 or abs_dy == 0 and abs_dx == 32:
        damage = 10
        if player.armor:
            damage = max(1, damage - player.armor["defense"])
        player.hp -= damage
        print("敵の攻撃！プレイヤーのHP:", player.hp)
        if isinstance(enemy, StrongEnemy) and random.random() < 0.2:
            player.status = "poison"
            player.status_counter = 20
            print("毒を受けた！")
        return

    # 追跡機能
    if abs_dx <= 64 and abs_dy <= 64:
        dx_step = 32 if dx > 0 else -32 if dx < 0 else 0
        dy_step = 32 if dy > 0 else -32 if dy < 0 else 0

        for step_x, step_y in [(dx_step, 0), (0, dy_step)]:
            if not collides_with_any(enemy.x + step_x, enemy.y + step_y, tiles, player, enemies):
                enemy.move(step_x, step_y)
                return
            
    # ランダム移動
    directions = [(32,0), (-32,0), (0,32), (0,-32)]
    random.shuffle(directions)
    for dx, dy in directions:
        if not collides_with_any(enemy.x + dx, enemy.y + dy, tiles, player, enemies):
            enemy.move(dx, dy)
            return
        


def game_over(screen):
    font = pygame.font.SysFont(None, 72)
    text = font.render("Game Over", True, (255, 0, 0))
    rect = text.get_rect(center=(320, 240))
    screen.fill((0, 0, 0))
    screen.blit(text, rect)
    pygame.display.update()
    pygame.time.wait(2000)

def collides_with_any(x, y, tiles, player, enemies):
    for tile in tiles:
        if tile.is_wall():
            if x < tile.x + tile.size and x + 32 > tile.x and y < tile.y + tile.size and y + 32 > tile.y:
                return True
    if x == player.x and y == player.y:
        return True
    for e in enemies:
        if e.x == x and e.y == y:
            return True
    return False

def generate_enemies(floor, tiles, player):
    tile_candidates = [tile for tile in tiles if tile.tile_type == 0]
    tile_candidates = [
        tile for tile in tile_candidates
        if not (tile.x == player.x and tile.y == player.y)
    ]
    
    enemy_count = 3 if floor == 1 else 4 if floor == 2 else 5
    selected_tiles = random.sample(tile_candidates, enemy_count)

    enemies = []
    for i, tile in enumerate(selected_tiles):
        if floor == 1:
            enemies.append(Enemy(tile.x, tile.y))
        elif floor == 2:
            if i % 2 == 0:
                enemies.append(Enemy(tile.x, tile.y))
            else:
                enemies.append(StrongEnemy(tile.x, tile.y))
        elif floor == 3:
            if i % 2 == 0:
                enemies.append(StrongEnemy(tile.x, tile.y))
            else:
                enemies.append(ArcherEnemy(tile.x, tile.y))
        else:
            enemies.append(StrongEnemy(tile.x, tile.y))
    return enemies

def generate_items(floor, tiles, got_sword=False, got_armor=False):
    items = []
    tile_candidates = [tile for tile in tiles if tile.tile_type == 0]
    random.shuffle(tile_candidates)
    index = 0

    # 回復アイテム
    heal_count = 2 if floor == 1 else 1
    for _ in range(heal_count):
        tile = tile_candidates[index]
        items.append(Item(tile.x, tile.y, "heal"))
        index += 1

    # 攻撃力アップ
    atk_count = 1 if floor < 3 else 2
    for _ in range(atk_count):
        tile = tile_candidates[index]
        items.append(Item(tile.x, tile.y, "powerup"))
        index += 1

    # armor
    if floor == 2 and not got_armor:
        tile = tile_candidates[index]
        items.append(Item(tile.x, tile.y, "armor"))
        index += 1

    # sword
    if floor == 3 and not got_sword:
        tile = tile_candidates[index]
        items.append(Item(tile.x, tile.y, "sword"))
        index += 1

    return items

def save_game(player, floor, got_sword=False, got_armor=False):
    data = {
        "x": player.x,
        "y": player.y,
        "hp": player.hp,
        "level": player.level,
        "exp": player.exp,
        "exp_to_next": player.exp_to_next,
        "max_hp": player.max_hp,
        "attack_power": player.attack_power,
        "inventory": player.inventory.items,
        "weapon": player.weapon,
        "armor": player.armor,
        "floor": floor,
        "got_sword": got_sword,
        "got_armor": got_armor
    }
    with open("save.json", "w") as f:
        json.dump(data, f)
    print("ゲームを保存しました。")
 
def load_game(player):
    if not os.path.exists("save.json"):
        print("セーブデータが見つかりません。")
        return None, False, False  # ← ここが変更点①（3つ返す）

    with open("save.json", "r") as f:
        save_data = json.load(f)

    player.x = save_data["x"]
    player.y = save_data["y"]
    player.hp = save_data["hp"]
    player.level = save_data["level"]
    player.exp = save_data["exp"]
    player.exp_to_next = save_data["exp_to_next"]
    player.max_hp = save_data["max_hp"]
    player.attack_power = save_data["attack_power"]
    player.inventory.items = save_data["inventory"]
    player.weapon = save_data["weapon"]
    player.armor = save_data["armor"]

    floor = save_data.get("floor", 1)
    got_sword = save_data.get("got_sword", False)  # ← 変更点②
    got_armor = save_data.get("got_armor", False)  # ← 変更点③
    print("ゲームをロードしました。")
    
    return floor, got_sword, got_armor
