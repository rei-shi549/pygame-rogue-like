import pygame
from assets import heal_img, powerup_img

class StatusBar:
    def __init__(self, screen, player, floor):
        self.screen = screen
        self.player = player
        self.floor = floor
        self.font = pygame.font.SysFont(None, 28)

    def draw(self):
        screen = self.screen
        player = self.player

        pygame.draw.rect(screen, (50, 50, 50), (0, 0, 640, 64))

        hp_ratio = player.hp / player.max_hp
        hp_bar_width = int(200 * hp_ratio)
        pygame.draw.rect(screen, (180, 0, 0), (100, 10, 200, 20))
        pygame.draw.rect(screen, (255, 0, 0), (100, 10, hp_bar_width, 20))
        screen.blit(self.font.render(f"HP: {player.hp}", True, (255, 255, 255)), (20, 10))

        screen.blit(self.font.render(f"ATK: {player.attack_power}", True, (255,255,255)), (20, 35))

        if player.weapon:
            screen.blit(pygame.image.load("images/sword.png"), (460, 0))
        if player.armor:
            screen.blit(pygame.image.load("images/armor.png"), (500, 0))

        screen.blit(self.font.render(f"Lv: {player.level}", True, (255,255,255)), (320, 10))
        screen.blit(self.font.render(f"EXP: {player.exp}/{player.exp_to_next}", True, (255,255,255)), (320, 35))

        if player.status:
            screen.blit(self.font.render(f"{player.status}", True, (255,100,100)), (120, 35))

        floor_text = self.font.render(f"Floor:{self.floor}", True, (255, 255, 0))
        floor_text_rect = floor_text.get_rect(bottomright=(630, 545))
        screen.blit(floor_text, floor_text_rect)

        for i, item_kind in enumerate(player.inventory.items[:5]):
            if item_kind == "heal":
                screen.blit(heal_img, (460 + i * 34, 32))
            elif item_kind == "powerup":
                screen.blit(powerup_img, (460 + i * 34, 32))

    def update_floor(self, new_floor):
        self.floor = new_floor
