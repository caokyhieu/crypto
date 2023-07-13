import pygame
from pygame.locals import *
import sys
import random
import hashlib
import datetime

# Initialize blockchain
class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = datetime.datetime.now()

    def calculate_hash(self):
        hash_data = str(self.sender) + str(self.recipient) + str(self.amount) + str(self.timestamp)
        return hashlib.sha256(hash_data.encode()).hexdigest()

class Block:
    def __init__(self, transactions, previous_hash):
        self.timestamp = datetime.datetime.now()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        hash_data = str(self.timestamp) + str(self.transactions) + str(self.previous_hash) + str(self.nonce)
        return hashlib.sha256(hash_data.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = ''.join(['0' for _ in range(difficulty)])

        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

        print("Block mined:", self.hash)

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4
        self.pending_transactions = []

    def create_genesis_block(self):
        return Block([], "0")

    def get_last_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, recipient, amount):
        transaction = Transaction(sender, recipient, amount)
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner_address,reward):
        block = Block(self.pending_transactions, self.get_last_block().hash)
        block.mine_block(self.difficulty)
        self.chain.append(block)

        # Reward the miner
        reward_transaction = Transaction("System", miner_address, reward)
        self.pending_transactions = [reward_transaction]

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == address:
                    balance -= transaction.amount
                elif transaction.recipient == address:
                    balance += transaction.amount
        return balance

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 60

# Load textures
spaceship_texture = pygame.image.load('images/580b585b2edbce24c47b2d2a.png')
asteroid_texture = pygame.image.load('images/33922-6-asteroid.png')

# Initialize font
font = pygame.font.Font(None, 28)

# Spaceship class
class Spaceship:
    def __init__(self):
        self.texture = pygame.transform.scale(spaceship_texture, (64, 64))
        self.rect = self.texture.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 5
        self.bullets = []
    
    def move(self):
        mouse_pos = pygame.mouse.get_pos()
        self.rect.centerx = mouse_pos[0]
        self.rect.centery = mouse_pos[1]
    
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        self.bullets.append(bullet)
    
    def update(self):
        self.move()
        for bullet in self.bullets:
            bullet.update()
            if bullet.rect.bottom < 0:
                self.bullets.remove(bullet)
    
    def draw(self, screen):
        screen.blit(self.texture, self.rect)
        for bullet in self.bullets:
            bullet.draw(screen)

# Bullet class
class Bullet:
    def __init__(self, x, y):
        self.texture = pygame.Surface((4, 10))
        self.texture.fill((255, 255, 255))
        self.rect = self.texture.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
    
    def update(self):
        self.rect.y -= self.speed
    
    def draw(self, screen):
        screen.blit(self.texture, self.rect)

# Asteroid class
class Asteroid:
    def __init__(self):
        self.texture = pygame.transform.scale(asteroid_texture, (64, 64))
        self.rect = self.texture.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed = random.randrange(1, 5)
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT + 10:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed = random.randrange(1, 5)
    
    def draw(self, screen):
        screen.blit(self.texture, self.rect)

# Game initialization
def game_init():
    spaceship = Spaceship()
    asteroids = []
    for _ in range(10):
        asteroids.append(Asteroid())
    return spaceship, asteroids

# Game loop
# Game loop
def game_loop(blockchain):
    spaceship, asteroids = game_init()
    reward_given = False

    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    spaceship.shoot()

        spaceship.update()
        for asteroid in asteroids:
            asteroid.update()

        # Collision detection
        for asteroid in asteroids:
            if spaceship.rect.colliderect(asteroid.rect):
                # Game over
                print("Game Over")
                pygame.quit()
                sys.exit()

        for bullet in spaceship.bullets:
            for asteroid in asteroids:
                if bullet.rect.colliderect(asteroid.rect):
                    # Asteroid destroyed
                    spaceship.bullets.remove(bullet)
                    asteroids.remove(asteroid)
                    blockchain.mine_pending_transactions("Player",100)  # Add 100 crypto to the player's balance
                    if len(asteroids) == 0:
                        # You win!
                        if not reward_given:
                            reward_given = True
                            blockchain.mine_pending_transactions("Player",100)  # Mine pending transactions to update balance
                        print("You Win!")
                        pygame.quit()
                        sys.exit()
                    break  # Exit the loop after destroying the asteroid


        # Rendering
        screen.fill((0, 0, 0))
        spaceship.draw(screen)
        for asteroid in asteroids:
            asteroid.draw(screen)
        
        # Display current balance
        balance_text = font.render("Balance: " + str(blockchain.get_balance("Player")), True, (255, 255, 255))
        balance_rect = balance_text.get_rect()
        balance_rect.topleft = (10, 10)
        screen.blit(balance_text, balance_rect)
        
        pygame.display.flip()
        clock.tick(FPS)


# Start the game loop
blockchain = Blockchain()
blockchain.add_transaction("System", "Player", 2000)  # Initial cryptocurrency balance
game_loop(blockchain)
