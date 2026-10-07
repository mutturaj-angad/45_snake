import pygame
from .snake import Snake
from .food import Food

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cell_size = 20
        self.grid_width = width // self.cell_size
        self.grid_height = height // self.cell_size

        self.snake = Snake(self.grid_width // 2, self.grid_height // 2, self.cell_size)
        self.food = Food(self.grid_width, self.grid_height, self.cell_size)

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_font = pygame.font.SysFont("Arial", 48)
        self.game_over_detail_font = pygame.font.SysFont("Arial", 24)

        self.moves_per_second = 8
        self._frame_counter = 0

        self.game_over = False
        self.exit_requested = False
        self.restart_speed = None

    def handle_keydown(self, key):
        if self.game_over:
            difficulty_speeds = {
                pygame.K_1: 5,
                pygame.K_2: 8,
                pygame.K_3: 12,
            }
            if key in difficulty_speeds:
                self.restart_speed = difficulty_speeds[key]
            elif key == pygame.K_ESCAPE:
                self.exit_requested = True
            return

        # Direction changes are applied immediately on key press.
        if key in (pygame.K_UP, pygame.K_w):
            self.snake.set_direction(0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.snake.set_direction(0, 1)
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.snake.set_direction(-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.snake.set_direction(1, 0)

    def handle_input(self):
        # Reserved for continuously-held-key input (not used for a
        # grid-based snake, but kept here to mirror the engine's shape).
        pass

    def update(self):
        if self.game_over:
            return

        self._frame_counter += 1
        frames_per_move = max(1, 60 // self.moves_per_second)
        if self._frame_counter < frames_per_move:
            return
        self._frame_counter = 0

        self.snake.move()

        if self.snake.collides_with_wall(self.grid_width, self.grid_height):
            self.game_over = True
            return

        if self.snake.collides_with_self():
            self.game_over = True
            return

        if self.snake.head_rect().colliderect(self.food.rect()):
            self.snake.grow()
            self.score += 1
            if not self.food.respawn(self.snake.body):
                self.game_over = True

    def render(self, screen):
        # Draw food
        pygame.draw.rect(screen, RED, self.food.rect())

        # Draw snake
        for rect in self.snake.segment_rects():
            pygame.draw.rect(screen, GREEN, rect)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            screen.blit(overlay, (0, 0))

            title = self.game_over_font.render("Game Over", True, WHITE)
            final_score = self.game_over_detail_font.render(
                f"Final score: {self.score}", True, WHITE
            )
            screen.blit(title, title.get_rect(center=(self.width // 2, self.height // 2 - 60)))
            screen.blit(final_score, final_score.get_rect(center=(self.width // 2, self.height // 2)))
            choices = self.game_over_detail_font.render(
                "1: Easy    2: Medium    3: Hard", True, WHITE
            )
            exit_prompt = self.game_over_detail_font.render(
                "Esc: Exit", True, WHITE
            )
            screen.blit(choices, choices.get_rect(center=(self.width // 2, self.height // 2 + 45)))
            screen.blit(exit_prompt, exit_prompt.get_rect(center=(self.width // 2, self.height // 2 + 80)))
