import pygame
import random

# Start pygame
pygame.init()

# Grootte van het scherm
WIDTH = 600
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Clock voor FPS
clock = pygame.time.Clock()

# Grootte van snake en appel
snake_size = 20

# Startpositie snake
snake_x = 300
snake_y = 200

# Startrichting snake
snake_dx = 0
snake_dy = 0

# Willekeurige startpositie van de appel
food_x = random.randint(0, (WIDTH - snake_size) // snake_size) * snake_size
food_y = random.randint(0, (HEIGHT - snake_size) // snake_size) * snake_size

# Snake body als lijst van segmenten; start met één segment
snake_body = [[snake_x, snake_y]]

# Lengte van de snake
snake_length = 1

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Richting aanpassen met pijltjestoetsen
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and snake_dx == 0:
                snake_dx = -snake_size
                snake_dy = 0
            elif event.key == pygame.K_RIGHT and snake_dx == 0:
                snake_dx = snake_size
                snake_dy = 0
            elif event.key == pygame.K_UP and snake_dy == 0:
                snake_dx = 0
                snake_dy = -snake_size
            elif event.key == pygame.K_DOWN and snake_dy == 0:
                snake_dx = 0
                snake_dy = snake_size

    # Snake positie updaten
    snake_x += snake_dx
    snake_y += snake_dy

    # Voeg nieuw hoofd toe aan de lijst
    snake_body.append([snake_x, snake_y])

    # Snake lengte bijhouden
    if len(snake_body) > snake_length:
        # Verwijder het laatste segment zodat snake "beweegt"
        del snake_body[0]

    # Snake raakt de appel?
    if snake_x == food_x and snake_y == food_y:
        # Snake groeit
        snake_length += 1
        # Plaats een nieuwe appel
        food_x = random.randint(0, (WIDTH - snake_size) // snake_size) * snake_size
        food_y = random.randint(0, (HEIGHT - snake_size) // snake_size) * snake_size

    # Achtergrond zwart
    screen.fill((0, 0, 0))

    # Teken de appel
    pygame.draw.rect(screen, (255, 0, 0), (food_x, food_y, snake_size, snake_size))

    # Teken de snake (alle segmenten)
    for segment in snake_body:
        pygame.draw.rect(screen, (0, 255, 0), (segment[0], segment[1], snake_size, snake_size))

    # Update scherm
    pygame.display.update()

    # Beperk FPS
    clock.tick(10)

# Stop pygame netjes
pygame.quit()