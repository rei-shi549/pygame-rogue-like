import pygame

# プレイヤー画像
player_images = {
    "up":    [pygame.image.load(f"images/player_up_{i}.png") for i in range(3)],
    "down":  [pygame.image.load(f"images/player_down_{i}.png") for i in range(3)],
    "left":  [pygame.image.load(f"images/player_left_{i}.png") for i in range(3)],
    "right": [pygame.image.load(f"images/player_right_{i}.png") for i in range(3)],
}

# 敵・アイテム画像
slime_img = pygame.image.load("images/slime.png")
goblin_img = pygame.image.load("images/goblin.png")
archer_img = pygame.image.load("images/archer.png")
arrow_img = pygame.image.load("images/arrow.png")
heal_img = pygame.image.load("images/heal.png")
powerup_img = pygame.image.load("images/powerup.png")
sword_img = pygame.image.load("images/sword.png")
armor_img = pygame.image.load("images/armor.png")

