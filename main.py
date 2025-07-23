import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


if __name__ == "__main__":
    print("Starting main.py")

    # Set up pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        pygame.display.flip()

        clock.tick(60)
