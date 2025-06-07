import pygame
import random
from assets import player_images, slime_img, goblin_img, archer_img, arrow_img
from objects import Item

# ========== キャラクター基底クラス ==========
class Character:
    def __init__(self, x, y, width, height, image, hp):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.image = image
        self.hp = hp
        self.facing = "down"

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        
    def move(self, dx, dy):
        self.x += dx
        self.y += dy

# ========== プレイヤークラス ==========
class Player(Character):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32, None, 100)
        self.attack_power = 25
        self.facing = "down"
        self.frame_index = 0
        self.animation_timer = 0
        self.images = {
            "up":    [pygame.image.load(f"images/player_up_{i}.png") for i in range(3)],
            "down":  [pygame.image.load(f"images/player_down_{i}.png") for i in range(3)],
            "left":  [pygame.image.load(f"images/player_left_{i}.png") for i in range(3)],
            "right": [pygame.image.load(f"images/player_right_{i}.png") for i in range(3)],
        }
        self.image = self.images[self.facing][self.frame_index]
        self.level = 1
        self.exp = 0
        self.exp_to_next = 30
        self.max_hp = 100  # 今後のHP成長に備えて分離
        self.status = None       # 状態異常名（"poison"など）
        self.status_counter = 0  # 効果残りターン数
        self.prev_x = x
        self.prev_y = y
        self.weapon = None  # 現在の武器（None or dict）
        self.armor = None   # 現在の防具（None or dict）
        self.inventory = Inventory()  # ←インベントリ追加

    def handle_input(self, tiles, enemies, items):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        moved = False

        if keys[pygame.K_LEFT]:
            dx = -32
            self.facing = "left"
            self.image = self.images[self.facing][self.frame_index]
            moved = True
        elif keys[pygame.K_RIGHT]:
            dx = 32
            self.facing = "right"
            self.image = self.images[self.facing][self.frame_index]
            moved = True
        elif keys[pygame.K_UP]:
            dy = -32
            self.facing = "up"
            self.image = self.images[self.facing][self.frame_index]
            moved = True
        elif keys[pygame.K_DOWN]:
            dy = 32
            self.facing = "down"
            self.image = self.images[self.facing][self.frame_index]
            moved = True

        if moved:
            next_x = self.x + dx
            next_y = self.y + dy

            if not self.collides_with_wall(next_x, next_y, tiles):
                for enemy in enemies:
                    if enemy.x == next_x and enemy.y == next_y:
                        # 移動先に敵がいたら攻撃
                        return self.attack(enemies, items)  # Noneはmain側のitemsを使わないことを意味
                self.prev_x = self.x
                self.prev_y = self.y
                self.move(dx, dy)
                self.animate()
                return True
        return False

    def animate(self):
        self.frame_index = (self.frame_index + 1) % len(self.images[self.facing])
        self.image = self.images[self.facing][self.frame_index]

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def collides_with_wall(self, next_x, next_y, tiles):
        for tile in tiles:
            if tile.is_wall():
                if (next_x < tile.x + tile.size and
                    next_x + self.width > tile.x and
                    next_y < tile.y + tile.size and
                    next_y + self.height > tile.y):
                    return True
        return False

    def is_colliding_with(self, other):
        return (
            self.x < other.x + other.width and
            self.x + self.width > other.x and
            self.y < other.y + other.height and
            self.y + self.height > other.y
        )

    def check_stairs(self, tiles):
        for tile in tiles:
            if tile.is_stairs():
                if (self.x < tile.x + tile.size and
                    self.x + self.width > tile.x and
                    self.y < tile.y + tile.size and
                    self.y + self.height > tile.y):
                    return True
        return False

    def attack(self, enemies, items=None):
        for enemy in enemies[:]:
            if is_in_front(self, enemy):
                attack_power = self.attack_power
                if self.weapon:
                    attack_power += self.weapon["power"]
                enemy.hp -= attack_power

                if enemy.hp <= 0:
                    enemy.hp = 0
                    print("敵を倒した！")

                    # 経験値獲得（敵の種類で変化）
                    if isinstance(enemy, StrongEnemy):
                        self.gain_exp(20)
                    else:
                        self.gain_exp(10)

                    if items is not None:
                        drop_chance = random.random()
                        if drop_chance < 0.5:
                            kind = random.choice(["heal", "powerup"])
                            items.append(Item(enemy.x, enemy.y, kind))
                            print(f"{kind} アイテムをドロップ！")

                    enemies.remove(enemy)
                return True
        return False

    def gain_exp(self, amount):
        self.exp += amount
        print(f"{amount}EXP獲得（合計EXP: {self.exp}）")
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            self.exp_to_next += 20
            self.max_hp += 10
            self.hp = self.max_hp
            self.attack_power += 5
            print(f"レベルアップ！ Lv{self.level} / ATK:{self.attack_power} / HP:{self.hp}")

    def update_status(self):
        if self.status == "poison":
            self.hp -= 2
            self.status_counter -= 1
            print("毒ダメージ！HP -2")
            if self.status_counter <= 0:
                self.status = None
                print("毒が治った！")

class Inventory:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item.kind)
        print(f"インベントリに {item.kind} を追加")

    def use_item(self, index, player):
        if 0 <= index < len(self.items):
            kind = self.items.pop(index)
            if kind == "heal":
                player.hp += 20
                if player.hp > player.max_hp:
                    player.hp = player.max_hp
                if player.status == "poison":
                    player.status = None
                    player.status_counter = 0
                print("回復アイテム使用！HP回復＆毒回復")
            elif kind == "powerup":
                player.attack_power += 10
                print("攻撃力アップアイテム使用！")
            elif kind == "sword":
                player.weapon = {"name": "Sword", "power": 10}
                print("剣を装備！攻撃力 +10")
            elif kind == "armor":
                player.armor = {"name": "Armor", "defense": 5}
                print("防具を装備！被ダメージ -5")

    
# ========== 敵キャラクタークラス ==========
class Enemy(Character):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32, slime_img, 50)  # 赤色、32x32、HP50
        self.direction = random.choice(["up", "down", "left", "right"])
        self.move_counter = 0  # 一定間隔で動く用カウンター

    def collides_with_wall(self, next_x, next_y, tiles):
        for tile in tiles:
            if tile.is_wall():
                if (next_x < tile.x + tile.size and
                    next_x + self.width > tile.x and
                    next_y < tile.y + tile.size and
                    next_y + self.height > tile.y):
                    return True
        return False

class StrongEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 100
        self.image = goblin_img  # 青系の色で差別化

class ArcherEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 60
        self.image = archer_img

    def can_shoot(self, player, tiles):
        if self.x == player.x:
            step = 32 if player.y > self.y else -32
            for y in range(self.y + step, player.y, step):
                if any(tile.x == self.x and tile.y == y and tile.is_wall() for tile in tiles):
                    return False
            return True
        elif self.y == player.y:
            step = 32 if player.x > self.x else -32
            for x in range(self.x + step, player.x, step):
                if any(tile.x == x and tile.y == self.y and tile.is_wall() for tile in tiles):
                    return False
            return True
        return False

class Arrow:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.prev_x = x  # ← 追加
        self.prev_y = y  # ← 追加
        self.dx = dx
        self.dy = dy
        self.image = arrow_img
        if dx == -32:  # 左
            self.image = pygame.transform.rotate(arrow_img, 180)
        elif dx == 32:  # 右
            self.image = arrow_img
        elif dy == -32:  # 上
            self.image = pygame.transform.rotate(arrow_img, 90)
        elif dy == 32:  # 下
            self.image = pygame.transform.rotate(arrow_img, -90)

    def move(self):
        self.prev_x = self.x  # ← 毎回更新
        self.prev_y = self.y
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def is_colliding_with(self, target):
        # 通常のヒット
        if self.x == target.x and self.y == target.y:
            return True
        # すれ違いのヒット（入れ替わり）
        if (self.prev_x == target.x and self.prev_y == target.y and
            self.x == target.prev_x and self.y == target.prev_y):
            return True
        return False

def is_in_front(player, enemy):
    if player.facing == "up":
        return (player.x == enemy.x and player.y - 32 == enemy.y)
    elif player.facing == "down":
        return (player.x == enemy.x and player.y + 32 == enemy.y)
    elif player.facing == "left":
        return (player.y == enemy.y and player.x - 32 == enemy.x)
    elif player.facing == "right":
        return (player.y == enemy.y and player.x + 32 == enemy.x)
    return False