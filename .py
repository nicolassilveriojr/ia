import pygame
print(pygame.ver)
import random
import math

pygame.init()

# Configurações tela e clock
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle Realms: Gun & Blade - Protótipo Avançado")
clock = pygame.time.Clock()
FPS = 60

# Cores (estilo vibrante)
WHITE = (245,245,245)
BLACK = (20,20,20)
RED = (220,20,60)
GREEN = (50,205,50)
BLUE = (30,144,255)
YELLOW = (255,215,0)
ORANGE = (255,140,0)
PURPLE = (148,0,211)
GRAY = (100,100,100)
BROWN = (139,69,19)

# Fontes
font_small = pygame.font.SysFont('Arial', 18)
font_med = pygame.font.SysFont('Arial', 28)
font_big = pygame.font.SysFont('Arial', 48)

# Variáveis globais
cu_oins = 0  # moeda
game_over = False

# Raridades
RARITY_COLORS = {
    "Common": GRAY,
    "Rare": BLUE,
    "Epic": PURPLE,
    "Exotic": ORANGE
}

class Weapon:
    def __init__(self, name, damage, fire_rate, ammo, max_ammo, rarity, weapon_type):
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate  # frames cooldown
        self.ammo = ammo
        self.max_ammo = max_ammo
        self.rarity = rarity
        self.type = weapon_type  # 'gun' or 'melee'
        self.cooldown = 0

    def shoot(self):
        if self.ammo > 0 or self.ammo == -1:
            if self.cooldown <= 0:
                if self.ammo > 0:
                    self.ammo -= 1
                self.cooldown = self.fire_rate
                return True
        return False

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Aparência voxel-style (bloco azul)
        self.image = pygame.Surface((40, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.speed = 6
        self.health = 100
        self.max_health = 100
        self.cu_oins = 0

        # Armas: 1 pistola, 1 rifle, 1 espada
        self.weapons = []
        self.weapons.append(Weapon("Common Pistol", damage=12, fire_rate=15, ammo=12, max_ammo=12, rarity="Common", weapon_type="gun"))
        self.weapons.append(Weapon("Navy Blue SCAR", damage=22, fire_rate=8, ammo=30, max_ammo=30, rarity="Rare", weapon_type="gun"))
        self.weapons.append(Weapon("Basic Sword", damage=35, fire_rate=20, ammo=-1, max_ammo=-1, rarity="Common", weapon_type="melee"))

        self.current_weapon_idx = 0
        self.invincible = 0

        # Status buffs
        self.quick_reload = 0
        self.extra_life = 0

        # Movimento
        self.vel_x = 0
        self.vel_y = 0

    def switch_weapon(self):
        self.current_weapon_idx = (self.current_weapon_idx + 1) % len(self.weapons)

    @property
    def current_weapon(self):
        return self.weapons[self.current_weapon_idx]

    def move(self, keys):
        self.vel_x = 0
        self.vel_y = 0
        if keys[pygame.K_w]: self.vel_y = -self.speed
        if keys[pygame.K_s]: self.vel_y = self.speed
        if keys[pygame.K_a]: self.vel_x = -self.speed
        if keys[pygame.K_d]: self.vel_x = self.speed

        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Mantem na tela
        self.rect.clamp_ip(screen.get_rect())

    def update(self):
        # Atualiza cooldown arma
        self.current_weapon.update()

        # Dura buffs
        if self.quick_reload > 0:
            self.quick_reload -= 1
        if self.extra_life > 0:
            self.extra_life -= 1

        # Invencibilidade depois de hit
        if self.invincible > 0:
            self.invincible -= 1

    def shoot(self):
        w = self.current_weapon
        if w.type == "gun" and w.shoot():
            # Cria bala
            bullet = Bullet(self.rect.centerx, self.rect.top, w.damage)
            all_sprites.add(bullet)
            bullets.add(bullet)

    def sword_attack(self):
        w = self.current_weapon
        if w.type == "melee" and w.cooldown <= 0:
            w.cooldown = w.fire_rate
            # Detecta inimigos próximos
            hits = pygame.sprite.spritecollide(self, enemies, False)
            for enemy in hits:
                enemy.health -= w.damage
                enemy.hurt()
                if enemy.health <= 0:
                    enemy.kill()
                    self.cu_oins += enemy.cu_oins_drop

            hits_animals = pygame.sprite.spritecollide(self, animals, False)
            for animal in hits_animals:
                animal.health -= w.damage
                if animal.health <= 0:
                    animal.kill()
                    self.cu_oins += 2  # moedas por caça

    def hurt(self, damage):
        if self.invincible == 0:
            if self.extra_life > 0:
                # Aplica redução de dano buff
                damage = damage // 2
            self.health -= damage
            self.invincible = 30  # 0.5 segundos invencível
            if self.health <= 0:
                global game_over
                game_over = True

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, damage):
        super().__init__()
        self.image = pygame.Surface((6, 12))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -12
        self.damage = damage

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

        hits = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in hits:
            enemy.health -= self.damage
            enemy.hurt()
            self.kill()
            if enemy.health <= 0:
                enemy.kill()
                player.cu_oins += enemy.cu_oins_drop

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, health=80, speed=2, cu_oins_drop=5):
        super().__init__()
        self.image = pygame.Surface((35, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.health = health
        self.max_health = health
        self.cu_oins_drop = cu_oins_drop
        self.direction = random.choice([-1, 1])
        self.hurt_timer = 0

    def hurt(self):
        self.hurt_timer = 8  # flash amarelo ao ser atingido

    def update(self):
        # Movimento simples horizontal
        self.rect.x += self.speed * self.direction
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.direction *= -1

        # Flash amarelo quando sofre dano
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            self.image.fill(YELLOW)
        else:
            self.image.fill(RED)

        # Colisão com player
        if self.rect.colliderect(player.rect):
            player.hurt(10)

class Animal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 1
        self.direction = random.choice([-1, 1])
        self.health = 40

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.direction *= -1

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.type = item_type  # 'medkit', 'quick_reload', 'extra_life'
        self.image = pygame.Surface((20, 20))
        if item_type == 'medkit':
            self.image.fill(RED)
        elif item_type == 'quick_reload':
            self.image.fill(BLUE)
        elif item_type == 'extra_life':
            self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))

    def apply(self, player):
        if self.type == 'medkit':
            player.health = min(player.health + 40, player.max_health)
        elif self.type == 'quick_reload':
            player.quick_reload = 300  # dura 5 segundos a 60fps
        elif self.type == 'extra_life':
            player.extra_life = 300
        self.kill()

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=10, capacity=2):
        super().__init__()
        self.image = pygame.Surface((60, 30))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.capacity = capacity
        self.occupied = False

    def update(self):
        if self.occupied:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.rect.y -= self.speed
            if keys[pygame.K_s]:
                self.rect.y += self.speed
            if keys[pygame.K_a]:
                self.rect.x -= self.speed
            if keys[pygame.K_d]:
                self.rect.x += self.speed

            self.rect.clamp_ip(screen.get_rect())

all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
animals = pygame.sprite.Group()
items = pygame.sprite.Group()
bullets = pygame.sprite.Group()
vehicles = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

for _ in range(7):
    e = Enemy(random.randint(100, WIDTH-100), random.randint(50, HEIGHT//2))
    all_sprites.add(e)
    enemies.add(e)

for _ in range(5):
    a = Animal(random.randint(50, WIDTH-50), random.randint(HEIGHT//2, HEIGHT-50))
    all_sprites.add(a)
    animals.add(a)

item_types = ['medkit', 'quick_reload', 'extra_life']
for _ in range(5):
    i = Item(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50), random.choice(item_types))
    all_sprites.add(i)
    items.add(i)

v1 = Vehicle(100, HEIGHT - 60)
v2 = Vehicle(700, HEIGHT - 60, speed=14)
all_sprites.add(v1, v2)
vehicles.add(v1, v2)

def draw_hud():
    # Vida
    pygame.draw.rect(screen, RED, (10, 10, 200, 20))
    pygame.draw.rect(screen, GREEN, (10, 10, 200 * (player.health/player.max_health), 20))
    health_text = font_small.render(f'Health: {player.health}/{player.max_health}', True, BLACK)
    screen.blit(health_text, (15, 12))

    # Cu-oins
    coin_text = font_small.render(f'Cu-oins: {player.cu_oins}', True, YELLOW)
    screen.blit(coin_text, (10, 40))

    # Arma atual
    weapon = player.current_weapon
    ammo_text = "∞" if weapon.ammo == -1 else str(weapon.ammo)
    w_text = font_small.render(f'Weapon: {weapon.name} [{weapon.rarity}] Ammo: {ammo_text}', True, RARITY_COLORS[weapon.rarity])
    screen.blit(w_text, (10, 70))

    # Buffs
    if player.quick_reload > 0:
        qr_text = font_small.render('Buff: Quick Reload', True, BLUE)
        screen.blit(qr_text, (10, 100))
    if player.extra_life > 0:
        el_text = font_small.render('Buff: Extra Life', True, YELLOW)
        screen.blit(el_text, (10, 120))

def draw_game_over():
    screen.fill(BLACK)
    go_text = font_big.render("GAME OVER", True, RED)
    screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 50))
    inst_text = font_med.render("Press ESC to quit", True, WHITE)
    screen.blit(inst_text, (WIDTH//2 - inst_text.get_width()//2, HEIGHT//2 + 20))
    pygame.display.flip()

running = True

while running:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_ESCAPE:
                    running = False
            else:
                if event.key == pygame.K_TAB:
                    player.switch_weapon()
                if event.key == pygame.K_SPACE:
                    if player.current_weapon.type == 'gun':
                        player.shoot()
                    else:
                        player.sword_attack()

    if not game_over:
        player.move(keys)

        all_sprites.update()

        # Colisões jogador com itens
        hit_items = pygame.sprite.spritecollide(player, items, False)
        for item in hit_items:
            item.apply(player)

        # Colisões jogador com veículos (entrada e saída)
        for v in vehicles:
            if player.rect.colliderect(v.rect) and not v.occupied:
                if keys[pygame.K_e]:  # tecla 'E' para entrar
                    v.occupied = True
                    player.rect.center = v.rect.center
                    player.speed = 0
            if v.occupied:
                if keys[pygame.K_q]:  # tecla 'Q' para sair
                    v.occupied = False
                    player.speed = 6
                    player.rect.x = v.rect.x + v.rect.width + 10  # sai do lado do veículo

    screen.fill((180, 220, 255))  # Céu azul claro
    pygame.draw.rect(screen, (30,150,30), (0, HEIGHT - 100, WIDTH, 100))  # grama

    all_sprites.draw(screen)
    draw_hud()

    if game_over:
        draw_game_over()

    pygame.display.flip()

pygame.quit()
