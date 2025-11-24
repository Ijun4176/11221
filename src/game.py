import random
import sys
from dataclasses import dataclass
from typing import List, Tuple

import pygame

WIDTH, HEIGHT = 1280, 720
FPS = 60
GRAVITY = 0.6
PLAYER_SPEED = 5
JUMP_FORCE = -12
DASH_SPEED = 14
DASH_COOLDOWN = 60  # frames

PLATFORM_COLOR = (70, 70, 120)
PLAYER_COLOR = (70, 220, 180)
ENEMY_COLOR = (230, 120, 80)
BACKGROUND = (18, 18, 26)
TEXT_COLOR = (220, 220, 240)

pygame.init()
FONT = pygame.font.SysFont("consolas", 20)


@dataclass
class Platform:
    rect: pygame.Rect


@dataclass
class Enemy:
    rect: pygame.Rect
    direction: int = 1
    speed: int = 2
    health: int = 3

    def update(self, platforms: List[Platform], player_pos: pygame.Vector2):
        self.rect.x += self.direction * self.speed
        on_platform = False
        for platform in platforms:
            if self.rect.bottom <= platform.rect.top + 5 and self.rect.colliderect(platform.rect.inflate(0, 10)):
                on_platform = True
                break
        if not on_platform:
            self.direction *= -1
        if random.random() < 0.005:
            self.direction *= -1

        # Simple chase if player is near horizontally
        if abs(player_pos.x - self.rect.centerx) < 200:
            self.direction = 1 if player_pos.x > self.rect.centerx else -1


@dataclass
class Player:
    rect: pygame.Rect
    vel: pygame.Vector2
    on_ground: bool = False
    jumps: int = 2
    can_dash: bool = True
    dash_timer: int = 0
    facing: int = 1
    attack_cooldown: int = 0

    def handle_input(self, keys: pygame.key.ScancodeWrapper):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -PLAYER_SPEED
            self.facing = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = PLAYER_SPEED
            self.facing = 1
        else:
            self.vel.x *= 0.8
            if abs(self.vel.x) < 0.1:
                self.vel.x = 0

    def jump(self):
        if self.jumps > 0:
            self.vel.y = JUMP_FORCE
            self.jumps -= 1
            self.on_ground = False

    def dash(self):
        if self.can_dash and self.dash_timer == 0:
            self.vel.x = DASH_SPEED * self.facing
            self.can_dash = False
            self.dash_timer = DASH_COOLDOWN

    def attack_rect(self) -> pygame.Rect:
        width = 40
        height = 30
        offset_x = 30 * self.facing
        return pygame.Rect(self.rect.centerx + offset_x - width // 2, self.rect.centery - height // 2, width, height)

    def update(self, platforms: List[Platform]):
        self.vel.y += GRAVITY
        self.rect.x += int(self.vel.x)
        self._resolve_horizontal(platforms)
        self.rect.y += int(self.vel.y)
        self._resolve_vertical(platforms)

        if self.dash_timer > 0:
            self.dash_timer -= 1
        if self.on_ground:
            self.can_dash = True
            self.jumps = 2
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def _resolve_horizontal(self, platforms: List[Platform]):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel.x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel.x < 0:
                    self.rect.left = platform.rect.right
                self.vel.x = 0

    def _resolve_vertical(self, platforms: List[Platform]):
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel.y > 0:
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.rect.top = platform.rect.bottom
                self.vel.y = 0


def generate_room(x_offset: int) -> Tuple[List[Platform], List[Enemy]]:
    platforms: List[Platform] = []
    enemies: List[Enemy] = []

    floor = Platform(pygame.Rect(x_offset, HEIGHT - 80, WIDTH, 40))
    platforms.append(floor)

    for _ in range(random.randint(2, 4)):
        width = random.randint(160, 260)
        height = 20
        x = x_offset + random.randint(100, WIDTH - 200)
        y = random.randint(200, HEIGHT - 200)
        platforms.append(Platform(pygame.Rect(x, y, width, height)))

    for _ in range(random.randint(2, 5)):
        plat = random.choice(platforms)
        ex = plat.rect.centerx + random.randint(-100, 100)
        ey = plat.rect.top - 40
        enemies.append(Enemy(pygame.Rect(ex, ey, 32, 32)))

    return platforms, enemies


def draw_hud(screen, player: Player, rooms_cleared: int, seed: int):
    dash = "READY" if player.can_dash and player.dash_timer == 0 else f"COOLDOWN {player.dash_timer//FPS + 1}s"
    text = f"HP:∞  JUMPS:{player.jumps}  DASH:{dash}  ROOMS:{rooms_cleared}  SEED:{seed}"
    surf = FONT.render(text, True, TEXT_COLOR)
    screen.blit(surf, (20, 20))


def run(seed: int = None):
    seed = seed or random.randint(0, 9999)
    random.seed(seed)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    rooms: List[Tuple[List[Platform], List[Enemy]]] = []
    for i in range(4):
        platforms, enemies = generate_room(i * WIDTH)
        rooms.append((platforms, enemies))

    player = Player(rect=pygame.Rect(100, HEIGHT - 150, 36, 48), vel=pygame.Vector2(0, 0))
    camera_x = 0
    current_room = 0

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE):
                    player.jump()
                elif event.key == pygame.K_LSHIFT:
                    player.dash()
                elif event.key == pygame.K_f and player.attack_cooldown == 0:
                    player.attack_cooldown = FPS // 3

        keys = pygame.key.get_pressed()
        player.handle_input(keys)

        room_platforms: List[Platform] = []
        room_enemies: List[Enemy] = []
        for idx, (plats, enemies) in enumerate(rooms):
            if abs(idx - current_room) <= 1:
                room_platforms.extend(plats)
                room_enemies.extend(enemies)

        player.update(room_platforms)

        attack_rect = player.attack_rect() if player.attack_cooldown > 0 else None
        for enemy in room_enemies:
            enemy.update(room_platforms, pygame.Vector2(player.rect.center))
            if attack_rect and attack_rect.colliderect(enemy.rect):
                enemy.health -= 1
        for plats, enemies in rooms:
            enemies[:] = [e for e in enemies if e.health > 0]

        # Room transition
        if player.rect.centerx - camera_x > WIDTH * 0.8 and current_room < len(rooms) - 1:
            current_room += 1
        if player.rect.centerx - camera_x < WIDTH * 0.2 and current_room > 0:
            current_room -= 1

        camera_x = current_room * WIDTH

        screen.fill(BACKGROUND)
        for platform in room_platforms:
            pygame.draw.rect(screen, PLATFORM_COLOR, platform.rect.move(-camera_x, 0))
        for enemy in room_enemies:
            pygame.draw.rect(screen, ENEMY_COLOR, enemy.rect.move(-camera_x, 0))
        pygame.draw.rect(screen, PLAYER_COLOR, player.rect.move(-camera_x, 0))

        if attack_rect:
            pygame.draw.rect(screen, (255, 255, 150), attack_rect.move(-camera_x, 0), 2)

        draw_hud(screen, player, current_room, seed)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    seed_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run(seed_arg)
