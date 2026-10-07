import array
import math
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
        self.food_sound = self._create_sound(880, 0.12)
        self.game_over_sound = self._create_sound(330, 0.35, 110)

        self.moves_per_second = 8
        self._frame_counter = 0

        self.game_over = False
        self.exit_requested = False
        self.restart_speed = None

    @staticmethod
    def _create_sound(start_frequency, duration, end_frequency=None):
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            sample_rate, _, channels = pygame.mixer.get_init()
            sample_count = int(sample_rate * duration)
            samples = array.array("h")
            for index in range(sample_count):
                progress = index / sample_count
                frequency = start_frequency
                if end_frequency is not None:
                    frequency += (end_frequency - start_frequency) * progress
                envelope = 1 - progress
                value = int(10000 * envelope * math.sin(
                    2 * math.pi * frequency * index / sample_rate
                ))
                samples.extend([value] * channels)
            return pygame.mixer.Sound(buffer=samples.tobytes())
        except pygame.error:
            return None

    @staticmethod
    def _play_sound(sound):
        if sound is not None:
            sound.play()

    def _end_game(self):
        if not self.game_over:
            self.game_over = True
            self._play_sound(self.game_over_sound)

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
            self._end_game()
            return

        if self.snake.collides_with_self():
            self._end_game()
            return

        if self.snake.head_rect().colliderect(self.food.rect()):
            self.snake.grow()
            self.score += 1
            self._play_sound(self.food_sound)
            if not self.food.respawn(self.snake.body):
                self._end_game()

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
            replay_prompt = self.game_over_detail_font.render(
                "Play Again: choose a difficulty", True, WHITE
            )
            choices = self.game_over_detail_font.render(
                "1: Easy    2: Medium    3: Hard", True, WHITE
            )
            exit_prompt = self.game_over_detail_font.render(
                "Esc: Exit", True, WHITE
            )
            screen.blit(replay_prompt, replay_prompt.get_rect(center=(self.width // 2, self.height // 2 + 40)))
            screen.blit(choices, choices.get_rect(center=(self.width // 2, self.height // 2 + 70)))
            screen.blit(exit_prompt, exit_prompt.get_rect(center=(self.width // 2, self.height // 2 + 100)))
