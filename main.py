import pygame
import random
import sys

# --- Константы ---
# Размеры окна и сетки
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Цвета
BOARD_BACKGROUND_COLOR = (0, 0, 0)  # Черный фон.
BORDER_COLOR = (93, 216, 228)  # Цвет рамки.
APPLE_COLOR = (255, 0, 0)  # Красный.
SNAKE_COLOR = (0, 255, 0)  # Зеленый.

# Скорость игры (кадров в секунду)
SPEED = 20

# Направления движения: (dx, dy)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Словарь для быстрого поиска нового направления
DIRECTIONS = {
    pygame.K_UP: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT
}


class GameObject:
    """Базовый класс для игровых объектов."""
    
    def __init__(self, position=None, body_color=None):
        # Если позиция не передана, ставим в центр экрана
        if position is None:
            # Вычисляем центральную ячейку
            self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        else:
            self.position = position
            
        self.body_color = body_color

    def draw(self, surface):
        """Абстрактный метод отрисовки. Должен быть переопределен."""
        # По умолчанию ничего не рисуем
        pass


class Apple(GameObject):
    """Класс яблока."""
    
    def __init__(self):
        # Вызываем родительский конструктор с красным цветом
        super().__init__(body_color=APPLE_COLOR)
        # Сразу задаем случайную позицию
        self.randomize_position()

    def randomize_position(self, occupied_cells=None):
        """
        Устанавливает случайную позицию для яблока.
        Если передан список занятых клеток, яблоко не появится на них.
        """
        if occupied_cells is None:
            occupied_cells = []

        # Создаем множество всех возможных ячеек на поле
        all_cells = set(
            (x * GRID_SIZE, y * GRID_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
        )
        
        # Убираем занятые клетки
        free_cells = list(all_cells - set(occupied_cells))
        
        # Если свободных клеток нет (змейка заполнила всё поле), 
        # то яблоко просто ставим в случайное место (игра все равно скоро закончится)
        if not free_cells:
            self.position = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
        else:
            self.position = random.choice(free_cells)

    def draw(self, surface):
        """Отрисовывает яблоко на игровом поле."""
        # Вычисляем координаты прямоугольника для рисования
        rect = pygame.Rect(
            self.position[0], self.position[1], GRID_SIZE, GRID_SIZE
        )
        pygame.draw.rect(surface, self.body_color, rect)


class Snake(GameObject):
    """Класс змейки."""
    
    def __init__(self):
        super().__init__(body_color=SNAKE_COLOR)
        
        # Начальная длина
        self.length = 1
        
        # Список сегментов. Изначально змейка состоит из одной головы в центре.
        center_x = (SCREEN_WIDTH // 2 // GRID_SIZE) * GRID_SIZE
        center_y = (SCREEN_HEIGHT // 2 // GRID_SIZE) * GRID_SIZE
        self.positions = [(center_x, center_y)]
        
        # Текущее направление
        self.direction = RIGHT
        # Следующее направление (задается при нажатии клавиш)
        self.next_direction = None
        
        # Переменная для хранения "следа" (хвоста), который нужно затереть
        self.last = None

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки (двигает её на одну клетку)."""
        # Получаем текущую голову
        head_x, head_y = self.get_head_position()
        
        # Вычисляем новые координаты
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )

        # Проверка на столкновение с собой
        # Если новая голова попадает в тело (кроме головы и шеи)
        # В начале игры змейка короткая, проверяем только если длина > 2
        if self.length > 2:
            # Проверяем, есть ли новая позиция в списке сегментов (кроме первых двух)
            if new_head in self.positions[1:]:
                self.reset()
                return

        # Вставляем новую голову в начало списка
        self.positions.insert(0, new_head)

        # Если длина не увеличилась, удаляем хвост
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            # Если длина увеличилась, хвост не удаляем, 
            # но нужно обнулить last, чтобы не затирать лишнее
            self.last = None

    def draw(self, surface):
        """Отрисовывает змейку на экране, затирая след."""
        # Затираем хвост, если он есть
        if self.last:
            last_rect = pygame.Rect(
                self.last[0], self.last[1], GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

        # Рисуем все сегменты змейки
        for position in self.positions:
            rect = pygame.Rect(position[0], position[1], GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, self.body_color, rect)

    def get_head_position(self):
        """Возвращает позицию головы змейки (первый элемент списка)."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        
        # Возвращаем в центр
        center_x = (SCREEN_WIDTH // 2 // GRID_SIZE) * GRID_SIZE
        center_y = (SCREEN_HEIGHT // 2 // GRID_SIZE) * GRID_SIZE
        self.positions = [(center_x, center_y)]
        
        # Сбрасываем направление
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(snake):
    """Обрабатывает нажатия клавиш для изменения направления змейки."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            
            # Если нажата стрелка, меняем направление
            if event.key in DIRECTIONS:
                new_direction = DIRECTIONS[event.key]
                
                # Нельзя двигаться в противоположную сторону
                # Проверяем, не является ли новое направление противоположным текущему
                opposite = (-snake.direction[0], -snake.direction[1])
                
                if new_direction != opposite:
                    snake.next_direction = new_direction


def main():
    """Основная функция игры."""
    # Инициализация Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Змейка')
    clock = pygame.time.Clock()
    
    # Создание объектов
    snake = Snake()
    apple = Apple()
    
    # Устанавливаем стартовую позицию яблока, исключая центр, где стоит змейка
    apple.randomize_position(snake.positions)
    
    # Игровой цикл
    running = True
    while running:
        # Обработка событий
        handle_keys(snake)
        
        # Обновление направления
        snake.update_direction()
        
        # Движение змейки
        snake.move()
        
        # Проверка, съела ли змейка яблоко
        if snake.get_head_position() == apple.position:
            snake.length += 1
            # Перемещаем яблоко на новое свободное место
            apple.randomize_position(snake.positions)
            
        # Отрисовка
        screen.fill(BOARD_BACKGROUND_COLOR)
        
        # Рисуем рамку (по желанию, для красоты)
        pygame.draw.rect(screen, BORDER_COLOR, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 1)
        
        snake.draw(screen)
        apple.draw(screen)
        
        # Обновление заголовка с рекордом
        pygame.display.set_caption(f'Змейка | Длина: {snake.length}')
        
        # Обновление экрана
        pygame.display.update()
        
        # Задержка для контроля скорости
        clock.tick(SPEED)


if __name__ == '__main__':
    main()