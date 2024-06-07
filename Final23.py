import pygame
import sys
import time


# Initialize Pygame
pygame.init()


# Set up the screen
WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Two Player Game")
clock = pygame.time.Clock()


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# Load and scale shark animations
def load_and_scale(image_path, scale):
    image = pygame.image.load(image_path)
    return pygame.transform.scale(image, scale)


shark_swim_1 = load_and_scale('Graphic/CASEY BASE 1.png', (100, 100))
shark_swim_2 = load_and_scale('Graphic/CASEY BASE 2.png', (100, 100))
shark_swim = [shark_swim_1, shark_swim_2]


hurt_shark_1 = load_and_scale('Graphic/CASEY HURT 1.png', (100, 100))
hurt_shark_2 = load_and_scale('Graphic/CASEY HURT 2.png', (100, 100))
hurt_shark_swim = [hurt_shark_1, hurt_shark_2]


damage_shark_1 = load_and_scale('Graphic/CASEY EXTRA HURT 1.png', (100, 100))
damage_shark_2 = load_and_scale('Graphic/CASEY EXTRA HURT 2.png', (100, 100))
damage_shark_swim = [damage_shark_1, damage_shark_2]


soup_shark = load_and_scale('Graphic/CASEY NUHUH.png', (100, 100))
nuhuh_swim = [soup_shark]


# Load and scale submarine and torpedo images
submarine_image = load_and_scale('Graphic/submarine.png', (150, 75))
torpedo_image = load_and_scale('Graphic/torpedo.png', (50, 20))


shark_index = 0


shark_surf = shark_swim[shark_index]
hurt_shark_surf = hurt_shark_swim[shark_index]


shark_rect = shark_surf.get_rect()


# Define classes
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, up_key, down_key, images, hurt_images, damage_images):
        super().__init__()
        self.images = images
        self.hurt_images = hurt_images
        self.damage_images = damage_images
        self.nuhuh_images = nuhuh_swim
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.up_key = up_key
        self.down_key = down_key
        self.health = 3  # Initialize health for the player
        self.index = 0


    def update(self):
        keys = pygame.key.get_pressed()
        if keys[self.up_key]:
            self.rect.y -= self.speed
        if keys[self.down_key]:
            self.rect.y += self.speed
        # Keep player within screen bounds
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))


        # Update animation
        self.index += 0.1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[int(self.index)]


        # Update health-based animation
        if self.health == 2:
            self.images = self.hurt_images
        elif self.health == 1:
            self.images = self.damage_images
        else:
            self.images = shark_swim


    def switch_to_nuhuh(self):
        self.images = self.nuhuh_images
        self.index = 0


class Submarine(pygame.sprite.Sprite):
    def __init__(self, x, y, up_key, down_key):
        super().__init__()
        self.image = submarine_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.up_key = up_key
        self.down_key = down_key
        self.last_shot_time = 0  # Track the time of the last torpedo shot


    def update(self):
        keys = pygame.key.get_pressed()
        if keys[self.up_key]:
            self.rect.y -= self.speed
        if keys[self.down_key]:
            self.rect.y += self.speed
        # Keep submarine within screen bounds
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))


    def shoot_torpedo(self):
        current_time = time.time()
        if current_time - self.last_shot_time > 0.36:  # 0.36 second cooldown
            torpedo = Torpedo(self.rect.left, self.rect.centery, -1)
            all_sprites.add(torpedo)
            torpedos.add(torpedo)
            self.last_shot_time = current_time


class Torpedo(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = torpedo_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 7
        self.direction = direction


    def update(self):
        self.rect.x += self.speed * self.direction
        # Remove torpedos when they go off screen
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()


# Set up player sprites
player1 = Player(100, HEIGHT // 2, pygame.K_w, pygame.K_s, shark_swim, hurt_shark_swim, damage_shark_swim)
player2 = Submarine(WIDTH - 100, HEIGHT // 2, pygame.K_UP, pygame.K_DOWN)


sky_surface = pygame.image.load('Graphic/waterbackground2.png')
sky_surface2 = pygame.image.load('Graphic/waterbackground1.png')


# Set up groups
all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()
torpedos = pygame.sprite.Group()


all_sprites.add(player1, player2)
players.add(player1, player2)


# Main game loop
counter, text = 30, '30'.rjust(3)
pygame.time.set_timer(pygame.USEREVENT, 1000)
font = pygame.font.SysFont('Consolas', 30)


running = True
game_over = False
display_winner = False
game_over_time = None


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_over and display_winner:
                running = False  # Exit if the game is over and a key is pressed
            # Player 2 shoots torpedo
            if event.key == pygame.K_LEFT and not game_over:
                player2.shoot_torpedo()
        elif event.type == pygame.USEREVENT and not game_over:
            counter -= 1
            text = str(counter).rjust(3) if counter > 0 else 'SHARK WINS'


    if not game_over:
        # Update
        all_sprites.update()


        # Check for collisions between torpedos and player1
        for torpedo in pygame.sprite.spritecollide(player1, torpedos, True):
            player1.health -= 1
            if player1.health <= 0:
                game_over = True
                game_over_time = time.time()
                player1.switch_to_nuhuh()  # Switch to nuhuh_swim animation
                winning_text = "Player 2 Wins!"
                winning_surf = font.render(winning_text, True, BLACK)
                winning_rect = winning_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                display_winner = True  # Allow the winner animation to display


    # Draw
    screen.blit(sky_surface, (0, -50))
    screen.blit(sky_surface2, (400, 0))
    all_sprites.draw(screen)
    screen.blit(font.render(text, True, BLACK), (32, 48))


    if display_winner:
        screen.blit(winning_surf, winning_rect)
        if game_over and time.time() - game_over_time > 1:
            display_winner = False  # Allow the screen to stop updating after 1 second


    pygame.display.flip()
    clock.tick(60)


pygame.quit()
sys.exit()