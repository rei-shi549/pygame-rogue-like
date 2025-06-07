import pygame
from assets import heal_img, powerup_img

class Item:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.size = 32
        self.kind = kind
        if kind == "heal":
            self.image = heal_img
        elif kind == "powerup":
            self.image = powerup_img
        elif kind == "sword":
            self.image = pygame.image.load("images/sword.png")
            self.power = 10
        elif kind == "armor":
            self.image = pygame.image.load("images/armor.png")
            self.defense = 5

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def is_colliding_with(self, player):
        return (
            self.x < player.x + player.width and
            self.x + self.size > player.x and
            self.y < player.y + player.height and
            self.y + self.size > player.y
        )
