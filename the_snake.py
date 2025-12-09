"""Изгиб Питона — классическая игра «Змейка» на pygame.

Задания:
- ООП (GameObject -> Apple, Snake)
- проход сквозь стены
- рост при поедании яблока
- сброс при столкновении с собой
- докстринги, PEP 8
"""

import random
import sys
from typing import List, Optional, Tuple

import pygame
from pygame.locals import KEYDOWN, K_DOWN, K_LEFT, K_RIGHT, K_UP, QUIT

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

SPEED = 10

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

pygame.display.set_caption('Изгиб Питона')

_DEFAULT_CENTER = (
    SCREEN_WIDTH // 2,
    SCREEN_HEIGHT // 2,
)


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(
        self,
        position: Tuple[int, int] = (_DEFAULT_CENTER[0], _DEFAULT_CENTER[1]),
        body_color: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        """
        Инициализирует объект.

        Parameters
        ----------
        position : tuple[int, int]
            Координаты верхнего-левого угла объекта (кратны GRID_SIZE).
        body_color : tuple[int, int, int] | None
            RGB-цвет объекта.
        """
        self.position = position
        self.body_color = body_color

    def draw(self, surface: pygame.Surface) -> None:
        """Абстрактный метод отрисовки. Должен быть переопределён."""
        raise NotImplementedError


class Apple(GameObject):
    """Яблоко, которое должна съесть змейка."""

    def __init__(self) -> None:
        """Создаёт яблоко красного цвета в случайной позиции."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(
        self, occupied: Optional[List[Tuple[int, int]]] = None
    ) -> None:
        """
        Перемещает яблоко в случайную свободную клетку игрового поля.

        Parameters
        ----------
        occupied : Optional[list[tuple[int, int]]]
            Список занятых позиций (например, сегменты змейки) — чтобы
            яблоко не появлялось внутри неё.
        """
        if occupied is None:
            occupied = []

        while True:
            x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            pos = (x, y)
            if pos not in occupied:
                self.position = pos
                break

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает яблоко на переданной поверхности."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, (200, 0, 0), rect, 1)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    def __init__(self) -> None:
        """Инициализирует змейку в центре поля."""
        super().__init__(body_color=SNAKE_COLOR)
        center = (
            SCREEN_WIDTH // 2 // GRID_SIZE * GRID_SIZE,
            SCREEN_HEIGHT // 2 // GRID_SIZE * GRID_SIZE,
        )
        self.position = center
        self.length: int = 1
        self.positions: List[Tuple[int, int]] = [center]
        self.direction: Tuple[int, int] = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None
        self.last: Optional[Tuple[int, int]] = None

    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self) -> None:
        """
        Применяет накопленное следующее направление, если оно допустимо.

        Запрещаем разворот на 180 градусов: новое направление не может быть
        противоположно текущему.
        """
        if self.next_direction:
            opposite = (-self.direction[0], -self.direction[1])
            if self.next_direction != opposite:
                self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """
        Перемещает змейку на одну клетку в текущем направлении.

        Реализован проход сквозь стены (wrap-around).
        Если голова попадает в один из сегментов (самопересечение) — сброс.
        """
        cur_x, cur_y = self.get_head_position()
        dx, dy = self.direction
        new_x = (cur_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (cur_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        # Проверка на самопересечение (исключаем хвост и соседние сегменты)
        if new_head in self.positions[2:]:
            self.reset()
            return

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает все сегменты змейки и затирает старый хвост."""
        if self.last:
            tail_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, tail_rect)

        for pos in self.positions:
            rect = pygame.Rect(pos, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(
            self.get_head_position(),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, (0, 255, 0), head_rect)

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние после проигрыша."""
        center = (
            SCREEN_WIDTH // 2 // GRID_SIZE * GRID_SIZE,
            SCREEN_HEIGHT // 2 // GRID_SIZE * GRID_SIZE,
        )
        self.position = center
        self.length = 1
        self.positions = [center]
        self.direction = random.choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.last = None


def handle_keys(snake_obj: Snake) -> None:
    """Обрабатывает нажатия стрелок и передаёт следующее направление змейке."""
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_UP:
                snake_obj.next_direction = UP
            elif event.key == K_DOWN:
                snake_obj.next_direction = DOWN
            elif event.key == K_LEFT:
                snake_obj.next_direction = LEFT
            elif event.key == K_RIGHT:
                snake_obj.next_direction = RIGHT


def main() -> None:
    """Основная функция — инициализация и игровой цикл."""
    snake = Snake()
    apple = Apple()

    while True:
        handle_keys(snake)

        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(occupied=snake.positions)

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        apple.draw(screen)

        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
