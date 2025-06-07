# main.py
import pygame
import sys
from entities import Player
from mapdata import create_map, generate_enemies, generate_items, game_over
from mapdata import enemy_ai, collides_with_any, save_game, load_game
from ui import StatusBar
from assets import *

# メイン処理
def main():
    pygame.init()
    got_sword = False
    got_armor = False
    
    # ウィンドウサイズ設定
    screen_width = 640
    screen_height = 560
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("ローグライク風ゲーム 上級編")

    clock = pygame.time.Clock()
    floor = 1

    # プレイヤーと複数の敵を作成
    player = Player(96, 160)

    # マップを作成
    tiles = create_map()

    # アイテムランダム配置
    items = generate_items(floor, tiles, got_sword, got_armor)

    arrows = []
    
    # 敵ランダム配置
    enemies = generate_enemies(floor, tiles, player)

    status_bar = StatusBar(screen, player, floor)

    running = True
    while running:
        turn_passed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # キーを押した瞬間だけチェック
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    turn_passed = player.attack(enemies, items)
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                    idx = event.key - pygame.K_1
                    player.inventory.use_item(idx, player)
                elif event.key == pygame.K_s:
                    save_game(player, floor, got_sword, got_armor)
                elif event.key == pygame.K_l:
                    loaded_floor, loaded_got_sword, loaded_got_armor = load_game(player)
                    if loaded_floor is not None:
                        floor = loaded_floor
                        got_sword = loaded_got_sword
                        got_armor = loaded_got_armor
                        tiles = create_map()
                        items = generate_items(floor, tiles, got_sword, got_armor)
                        enemies = generate_enemies(floor, tiles, player)
                else:
                    turn_passed = player.handle_input(tiles, enemies, items)


        if turn_passed:
            player.update_status()
            # すべての敵が行動
            for enemy in enemies:
                enemy_ai(enemy, player, tiles, enemies, arrows)

            # 矢の移動と当たり判定
            for arrow in arrows[:]:
                arrow.move()
                if arrow.is_colliding_with(player):
                    player.hp -= 5
                    arrows.remove(arrow)
                    print("矢がヒット！プレイヤーHP:", player.hp)
                    continue
                elif any(tile.x == arrow.x and tile.y == arrow.y and tile.is_wall() for tile in tiles):
                    arrows.remove(arrow)
            # 敵との接触チェック
            for enemy in enemies:
                if player.is_colliding_with(enemy):
                    player.hp -= 10
                    print(f"プレイヤーにダメージ！現在HP: {player.hp}")
                    break
 
            # アイテム取得チェック
            for item in items[:]:
                if item.is_colliding_with(player):
                    if item.kind == "sword":
                        if not got_sword:
                            player.weapon = {"name": "Sword", "power": 10}
                            got_sword = True
                            print("剣を装備！与ダメージ +10")
                    elif item.kind == "armor":
                        if not got_armor:
                            player.armor = {"name": "Armor", "defense": 5}
                            got_armor = True
                            print("防具を装備！被ダメージ -5")
                    else:
                        player.inventory.add_item(item)

                    items.remove(item)

            # プレイヤーHPチェック
            if player.hp <= 0:
                print("Game Over!")
                game_over(screen)
                running = False                

            # フロア移動チェック
            if player.check_stairs(tiles):
                print(f"次のフロアへ！ → {floor+1}階")
                floor += 1
                status_bar.update_floor(floor)
                tiles = create_map()
                player.x = 96
                player.y = 96
                enemies = generate_enemies(floor, tiles, player)
                items = generate_items(floor, tiles)

        # 画面クリア
        screen.fill((0, 0, 0))

        # タイル描画
        for tile in tiles:
            tile.draw(screen)
            
        # アイテム描画
        for item in items:
            item.draw(screen)
            
        # キャラクター描画
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        # すべての矢を描画
        for arrow in arrows:
            arrow.draw(screen)

        status_bar.draw()

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# 実行
if __name__ == "__main__":
    main()
