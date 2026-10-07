import pygame
from .player import Player
from .obstacle import Obstacle

# Game Engine

WHITE = (255, 255, 255)
BROWN = (120, 80, 40)
DARK_GREEN = (30, 100, 30)
BLACK = (0, 0, 0)
RED = (180, 40, 40)


class GameEngine:

    def __init__(self, width, height, difficulty="Medium"):
        self.width = width
        self.height = height
        self.ground_y = height - 40

        # Create player
        self.player = Player(80, self.ground_y)

        # --------------------------------------------------
        # SOUND EFFECTS
        # --------------------------------------------------

        self.jump_sound = pygame.mixer.Sound(
            "sounds/jump.wav"
        )

        self.score_sound = pygame.mixer.Sound(
            "sounds/score.wav"
        )

        self.game_over_sound = pygame.mixer.Sound(
            "sounds/game_over.wav"
        )

        # --------------------------------------------------
        # DIFFICULTY SETTINGS
        # --------------------------------------------------

        self.max_speed = 12

        if difficulty == "Easy":
            self.speed = 5
            self.spawn_interval = 90

        elif difficulty == "Hard":
            self.speed = 8
            self.spawn_interval = 55

        else:
            # Medium
            self.speed = 6
            self.spawn_interval = 70

        self.difficulty = difficulty

        # Speed increases gradually
        self.speed_increase_per_frame = 0.003

        # --------------------------------------------------
        # OBSTACLES
        # --------------------------------------------------

        self._spawn_timer = 0
        self.obstacles = []

        # --------------------------------------------------
        # GAME DATA
        # --------------------------------------------------

        self.distance = 0
        self.score = 0

        # --------------------------------------------------
        # FONTS
        # --------------------------------------------------

        self.font = pygame.font.SysFont(
            "Arial",
            30
        )

        self.title_font = pygame.font.SysFont(
            "Arial",
            50,
            bold=True
        )

        self.game_over_font = pygame.font.SysFont(
            "Arial",
            28
        )

        # Game state
        self.game_over = False

    # ======================================================
    # HANDLE EVENTS
    # ======================================================

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            # Player jump
            if event.key in (
                pygame.K_SPACE,
                pygame.K_UP,
                pygame.K_w
            ):

                if not self.game_over:

                    self.player.jump()

                    # Play jump sound
                    self.jump_sound.play()

    # ======================================================
    # HANDLE INPUT
    # ======================================================

    def handle_input(self):
        pass

    # ======================================================
    # UPDATE GAME
    # ======================================================

    def update(self):

        # Stop updating after Game Over
        if self.game_over:
            return

        # --------------------------------------------------
        # INCREASE SPEED
        # --------------------------------------------------

        self.speed = min(
            self.speed + self.speed_increase_per_frame,
            self.max_speed
        )

        # --------------------------------------------------
        # UPDATE PLAYER
        # --------------------------------------------------

        self.player.update()

        # --------------------------------------------------
        # SPAWN OBSTACLES
        # --------------------------------------------------

        self._spawn_timer += 1

        if self._spawn_timer >= self.spawn_interval:

            self._spawn_timer = 0

            self.obstacles.append(
                Obstacle(
                    self.width,
                    self.ground_y,
                    self.speed
                )
            )

        # --------------------------------------------------
        # MOVE OBSTACLES + COLLISION
        # --------------------------------------------------

        for obstacle in self.obstacles:

            # Position before movement
            previous_x = obstacle.x

            # Move obstacle
            obstacle.move()

            # Update obstacle speed
            obstacle.speed = self.speed

            # Rectangle before movement
            previous_rect = pygame.Rect(
                previous_x,
                obstacle.y,
                obstacle.width,
                obstacle.height
            )

            # Rectangle after movement
            current_rect = obstacle.rect()

            # Rectangle covering the complete movement path
            movement_rect = previous_rect.union(
                current_rect
            )

            # Collision detection
            if (
                current_rect.colliderect(
                    self.player.rect()
                )
                or movement_rect.colliderect(
                    self.player.rect()
                )
            ):

                # Game Over
                self.game_over = True

                # Play Game Over sound
                self.game_over_sound.play()

                return

        # --------------------------------------------------
        # SCORE
        # --------------------------------------------------

        for obstacle in self.obstacles:

            if (
                not obstacle.scored
                and obstacle.x + obstacle.width < self.player.x
            ):

                obstacle.scored = True

                self.score += 1

                # Play score sound
                self.score_sound.play()

        # --------------------------------------------------
        # REMOVE OFF-SCREEN OBSTACLES
        # --------------------------------------------------

        self.obstacles = [
            obstacle
            for obstacle in self.obstacles
            if not obstacle.off_screen()
        ]

        # Update distance
        self.distance += self.speed

    # ======================================================
    # RENDER GAME
    # ======================================================

    def render(self, screen):

        # --------------------------------------------------
        # GROUND
        # --------------------------------------------------

        pygame.draw.line(
            screen,
            BROWN,
            (0, self.ground_y),
            (self.width, self.ground_y),
            4
        )

        # --------------------------------------------------
        # PLAYER
        # --------------------------------------------------

        pygame.draw.rect(
            screen,
            WHITE,
            self.player.rect()
        )

        # --------------------------------------------------
        # OBSTACLES
        # --------------------------------------------------

        for obstacle in self.obstacles:

            pygame.draw.rect(
                screen,
                DARK_GREEN,
                obstacle.rect()
            )

        # --------------------------------------------------
        # SCORE
        # --------------------------------------------------

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            BLACK
        )

        screen.blit(
            score_text,
            (10, 10)
        )

        # --------------------------------------------------
        # DIFFICULTY
        # --------------------------------------------------

        difficulty_text = self.font.render(
            f"Difficulty: {self.difficulty}",
            True,
            BLACK
        )

        screen.blit(
            difficulty_text,
            (10, 45)
        )

        # --------------------------------------------------
        # GAME OVER SCREEN
        # --------------------------------------------------

        if self.game_over:

            # Dark transparent overlay
            overlay = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 150)
            )

            screen.blit(
                overlay,
                (0, 0)
            )

            # ----------------------------------------------
            # GAME OVER TITLE
            # ----------------------------------------------

            title = self.title_font.render(
                "GAME OVER",
                True,
                RED
            )

            title_rect = title.get_rect(
                center=(
                    self.width // 2,
                    90
                )
            )

            screen.blit(
                title,
                title_rect
            )

            # ----------------------------------------------
            # FINAL SCORE
            # ----------------------------------------------

            final_score = self.font.render(
                f"Final Score: {self.score}",
                True,
                WHITE
            )

            score_rect = final_score.get_rect(
                center=(
                    self.width // 2,
                    145
                )
            )

            screen.blit(
                final_score,
                score_rect
            )

            # ----------------------------------------------
            # CURRENT DIFFICULTY
            # ----------------------------------------------

            difficulty_text = self.game_over_font.render(
                f"Difficulty: {self.difficulty}",
                True,
                WHITE
            )

            difficulty_rect = difficulty_text.get_rect(
                center=(
                    self.width // 2,
                    185
                )
            )

            screen.blit(
                difficulty_text,
                difficulty_rect
            )

            # ----------------------------------------------
            # EASY
            # ----------------------------------------------

            easy_text = self.game_over_font.render(
                "1 - Easy",
                True,
                WHITE
            )

            easy_rect = easy_text.get_rect(
                center=(
                    self.width // 2,
                    230
                )
            )

            screen.blit(
                easy_text,
                easy_rect
            )

            # ----------------------------------------------
            # MEDIUM
            # ----------------------------------------------

            medium_text = self.game_over_font.render(
                "2 - Medium",
                True,
                WHITE
            )

            medium_rect = medium_text.get_rect(
                center=(
                    self.width // 2,
                    265
                )
            )

            screen.blit(
                medium_text,
                medium_rect
            )

            # ----------------------------------------------
            # HARD
            # ----------------------------------------------

            hard_text = self.game_over_font.render(
                "3 - Hard",
                True,
                WHITE
            )

            hard_rect = hard_text.get_rect(
                center=(
                    self.width // 2,
                    300
                )
            )

            screen.blit(
                hard_text,
                hard_rect
            )

            # ----------------------------------------------
            # EXIT
            # ----------------------------------------------

            exit_text = self.game_over_font.render(
                "ESC - Exit",
                True,
                WHITE
            )

            exit_rect = exit_text.get_rect(
                center=(
                    self.width // 2,
                    335
                )
            )

            screen.blit(
                exit_text,
                exit_rect
            )