import pygame
import random
import json
import copy
from datetime import datetime
from abc import ABC, abstractmethod

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Color Gates Game")

# Цвета
COLORS = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'white': (255, 255, 255),  # Для сердечек
    'black': (0, 0, 0),  # Для неактивных цветов
    'gray': (100, 100, 100),  # Для блеклых цветов
    'dim_red': (128, 0, 0),
    'dim_green': (0, 128, 0),
    'dim_blue': (0, 0, 128),
    'dim_yellow': (128, 128, 0)
}


# Класс для управления цветами
class ColorManager:
    def __init__(self):
        self.colors = ['red', 'green', 'blue', 'yellow']
        self.active_color = None

    def get_color(self, color):
        if color == self.active_color:
            return color
        else:
            return f'dim_{color}'

    def set_active_color(self, color):
        if color in self.colors:
            self.active_color = color

    def reset_colors(self):
        self.active_color = None


# Абстрактный класс GameObject
class GameObject(ABC):
    def __init__(self, color, lane):
        self.color = color
        self.lane = lane
        self.x = lane * (WIDTH // 4)
        self.y = 0

    @abstractmethod
    def move(self):
        pass

    @abstractmethod
    def draw(self, screen):
        pass


# Класс для квадратиков
class Square(GameObject):
    def __init__(self, color, lane):
        super().__init__(color, lane)
        self.speed = 5

    def move(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, COLORS[self.color], (self.x, self.y, WIDTH // 4, 50))


# Класс для сердечек
class Heart(GameObject):
    def __init__(self, lane):
        super().__init__('white', lane)
        self.speed = 5

    def move(self):
        self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, COLORS[self.color], (self.x, self.y, WIDTH // 4, 50))


# Класс для ворот
class Gate:
    def __init__(self, lane, key):
        self.lane = lane
        self.color = 'black'
        self.open = True  # Ворота всегда открыты
        self.key = key
        self.last_toggle_time = 0

    def set_color(self, color):
        self.color = color

    def draw(self, screen):
        color = COLORS[self.color] if self.open else COLORS['black']
        pygame.draw.rect(screen, color, (self.lane * (WIDTH // 4), HEIGHT - 150, WIDTH // 4, 50))
        font = pygame.font.Font(None, 36)
        text = font.render(self.key, True, (255, 255, 255))
        screen.blit(text, (self.lane * (WIDTH // 4) + 20, HEIGHT - 130))


# Функция для генерации объектов в одном такте
def generate_objects():
    # Случайный выбор: квадратик или сердечко
    if random.randint(0, 20) != 0:
        # Генерируем квадратик случайного цвета (только яркие цвета)
        color = random.choice(['red', 'green', 'blue', 'yellow'])
        lane = random.randint(0, 3)
        return [Square(color, lane)]
    else:
        # Генерируем сердечко
        lane = random.randint(0, 3)
        return [Heart(lane)]


# Класс игры
class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.objects = []
        self.gates = [Gate(i, key) for i, key in enumerate(['a', 's', 'd', 'f'])]
        self.running = True
        self.grid_y = 0
        self.grid_step = 150  # Шаг сетки равен высоте трех квадратиков (50 * 3)
        self.lives = 4  # Начальное количество жизней
        self.score = 0
        self.color_manager = ColorManager()
        self.paused = False
        self.game_over = False
        self.saving_score = False
        self.player_name = ""
        self.current_time = 0
        self.score_info_step = 30
        self.score_info_start = 50
        self.score_block_step = 20
        self.scores_height = 0
        self.level_type = "normal"  # Тип уровня: "normal", "single_color", "multi_color"
        self.speed = 20  # Скорость падения объектов
        self.scroll_offset = 0  # Смещение для скролла таблицы рекордов

    def save_score(self, name, score):
        try:
            with open('scores.json', 'r') as file:
                scores = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            scores = {}

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if name in scores:
            scores[name].append([score, current_time, self.level_type, self.speed])
        else:
            scores[name] = [[score, current_time, self.level_type, self.speed]]

        try:
            with open('scores.json', 'w') as file:
                json.dump(scores, file, indent=4)
        # except IOError as e:
        #    print(f"Ошибка при сохранении файла: {e}.")
        finally:
            pass


    def draw_high_scores(self):
        try:
            with open('scores.json', 'r') as file:
                scores = json.load(file)

            font = pygame.font.Font(None, 36)
            y = self.score_info_start - self.scroll_offset
            for player, records in scores.items():
                text = font.render(f"Игрок: {player}:", True, (255, 255, 255))
                screen.blit(text, (50, y))
                y += self.score_info_start
                for record in records:
                    if len(record) == 4:
                        score, date_time, level_type, speed = record
                        text = font.render(f"Счет: {score}, Дата: {date_time},", True, (255, 255, 255))
                        screen.blit(text, (70, y))
                        y += self.score_info_step
                        text = font.render(f"Уровень: {level_type}, Скорость: {speed}.", True, (255, 255, 255))
                        screen.blit(text, (70, y))
                        y += self.score_info_start
                y += self.score_block_step

                pygame.draw.rect(screen, "black", (0, HEIGHT - 120, WIDTH, HEIGHT))
                text = font.render("Нажмите Esc для возврата в меню.", True, (255, 255, 255))
                screen.blit(text, (50, HEIGHT - 100))
                text = font.render("Используйте колесико мышки для навигации.", True, (255, 255, 255))
                screen.blit(text, (50, HEIGHT - 50))
                pygame.display.flip()

            self.scores_height = copy.copy(y) + self.scroll_offset - (HEIGHT // 2)

        except (FileNotFoundError, json.JSONDecodeError):
            screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 36)
            text = font.render("Файл с рекордами \"scores.json\" повержден!", True, (255, 255, 255))
            screen.blit(text, (50, 80))
            text = font.render("Отредактируйте или удалите его из папки с игрой.", True, (255, 255, 255))
            screen.blit(text, (50, 80 + 50))
            pygame.draw.rect(screen, "black", (0, HEIGHT - 120, WIDTH, HEIGHT))
            text = font.render("Нажмите Esc для возврата в меню.", True, (255, 255, 255))
            screen.blit(text, (50, HEIGHT - 100))
            pygame.display.flip()


    def select_difficulty(self):
        while True:
            screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 36)
            text = font.render("Выберите уровень сложности:", True, (255, 255, 255))
            screen.blit(text, (50, 50))
            text = font.render("1. Обычный уровень.", True, (255, 255, 255))
            screen.blit(text, (70, 100))
            text = font.render("2. Разные цвета (2 блока разного цвета).", True, (255, 255, 255))
            screen.blit(text, (70, 150))
            text = font.render("Нажмите Esc для возврата в меню.", True, (255, 255, 255))
            screen.blit(text, (50, 200))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                    # self.running = False
                    # return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.level_type = "normal"
                        return
                    elif event.key == pygame.K_2:
                        self.level_type = "multi_color"
                        return
                    elif event.key == pygame.K_ESCAPE:
                        return

    def set_speed(self):
        speed_input = ""
        while True:
            screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 36)
            text = font.render("Введите скорость:", True, (255, 255, 255))
            screen.blit(text, (50, 50))
            text = font.render(f"Текущая скорость: {speed_input}.", True, (255, 255, 255))
            screen.blit(text, (70, 100))
            text = font.render("Нажмите Enter для подтверждения.", True, (255, 255, 255))
            screen.blit(text, (50, 150))
            text = font.render("Нажмите Esc для возврата в меню.", True, (255, 255, 255))
            screen.blit(text, (50, 200))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                    # self.running = False
                    # return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_KP_ENTER:
                        try:
                            speed = int(speed_input)
                            if 1 <= speed:
                                self.speed = speed
                                return
                            else:
                                speed_input = ""
                        except ValueError:
                            speed_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        speed_input = speed_input[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        return
                    elif event.unicode.isdigit():
                        speed_input += event.unicode

    def about_game(self):
        while True:
            screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 36)
            text = font.render("ОБ ИГРЕ:", True, (255, 255, 255))
            screen.blit(text, (50, 50))
            text = font.render("Открывайте ворота клавишами \"a\", \"s\", \"d\", \"f\".", True, (255, 255, 255))
            screen.blit(text, (70, 100))
            text = font.render("Красьте ворота в нужный цвет клавишами \"j\", \"k\", \"l\", \";\".", True, (255, 255, 255))
            screen.blit(text, (70, 150))
            text = font.render("Ловите каждый цветной блок.", True, (255, 255, 255))
            screen.blit(text, (70, 200))
            text = font.render("Белые блоки дают доп. жизни. Помните о раскладке!", True, (255, 255, 255))
            screen.blit(text, (70, 250))
            text = font.render("Автор игры: Андрей Кубик.", True, (255, 255, 255))
            screen.blit(text, (50, 300))
            text = font.render("Мои контакты:", True, (255, 255, 255))
            screen.blit(text, (50, 350))
            text = font.render("Вк - ЗелРубКуб: https://vk.com/progresscubezelenograd.", True, (255, 255, 255))
            screen.blit(text, (50, 400))
            text = font.render("Тг: https://t.me/AndyKybik.", True, (255, 255, 255))
            screen.blit(text, (50, 450))
            text = font.render("Ютуб: https://www.youtube.com/@AndyKybik.", True, (255, 255, 255))
            screen.blit(text, (50, 500))
            text = font.render("Нажмите Esc для возврата в меню.", True, (255, 255, 255))
            screen.blit(text, (50,550))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                    # self.running = False
                    # return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
                # self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Пауза игры
                    self.paused = not self.paused
                    self.draw_pause()
                # Если только что остановили игру
                if event.key == pygame.K_ESCAPE and self.paused == True:
                    self.paused = False
                    self.game_over = True
                # if self.saving_score:
                #     if event.key == pygame.K_KP_ENTER:
                #         self.save_score(self.player_name, self.score)
                #         self.saving_score = False
                #         self.in_menu = True
                #         self.game_over = False
                #         self.lives = 4
                #         self.score = 0
                #         self.objects = []
                #         self.grid_y = 0
                #     elif event.key == pygame.K_BACKSPACE:
                #         self.player_name = self.player_name[:-1]
                #     else:
                #         self.player_name += event.unicode

    def update(self):
        self.current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        for i, key in enumerate([pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f]):
            if keys[key] and self.current_time - self.gates[i].last_toggle_time > 200:  # Задержка 200 мс
                self.gates[i].last_toggle_time = self.current_time
                # Устанавливаем цвет ворот в зависимости от активного цвета
                self.gates[i].set_color(self.color_manager.active_color if self.color_manager.active_color else 'black')

        # Обработка выбора цвета
        if keys[pygame.K_j]:
            self.color_manager.set_active_color('red')
        elif keys[pygame.K_k]:
            self.color_manager.set_active_color('green')
        elif keys[pygame.K_l]:
            self.color_manager.set_active_color('blue')
        elif keys[pygame.K_SEMICOLON]:
            self.color_manager.set_active_color('yellow')

        # Генерация объектов с учетом сетки
        if self.grid_y % self.grid_step == 0:
            new_objects = self.generate_objects()
            self.objects.extend(new_objects)

        self.grid_y += 5

        # Удаление объектов, вышедших за пределы экрана
        self.objects = [obj for obj in self.objects if obj.y < HEIGHT]

        # Проверка столкновений и обновление жизней и очков
        for obj in self.objects:
            if obj.y + 50 >= HEIGHT - 100:  # Объект достиг ворот
                gate = self.gates[obj.lane]
                if isinstance(obj, Heart):
                    if gate.open and gate.color != 'black':  # Ворота должны быть активны
                        self.lives = min(self.lives + 1, 4)  # Восстановление жизни
                else:
                    if gate.open and gate.color == obj.color:
                        self.score += 5  # Начисление очков
                    else:
                        self.lives -= 1  # Потеря жизни
                self.objects.remove(obj)

        # Проверка на окончание игры
        if self.lives <= 0:
            self.game_over = True

    def draw(self):
        screen.fill((0, 0, 0))
        for obj in self.objects:
            obj.move()
            obj.draw(screen)
        for gate in self.gates:
            gate.draw(screen)

        # Отображение выбора цвета
        for i, color in enumerate(['red', 'green', 'blue', 'yellow']):
            color_display = COLORS[self.color_manager.get_color(color)]
            pygame.draw.rect(screen, color_display, (i * (WIDTH // 4), HEIGHT - 100, WIDTH // 4, 50))
            font = pygame.font.Font(None, 36)
            text = font.render(['j', 'k', 'l', ';'][i], True, (255, 255, 255))
            screen.blit(text, (i * (WIDTH // 4) + 20, HEIGHT - 80))

        # Отображение жизней
        for i in range(self.lives):
            pygame.draw.rect(screen, COLORS['white'], (i * (WIDTH // 4), HEIGHT - 50, WIDTH // 4, 50))

        # Отображение очков
        font = pygame.font.Font(None, 36)
        text = font.render(f"Очки: {self.score}", True, (255, 255, 255))
        screen.blit(text, (10, 10))

        text = font.render(f"Пробел - пауза", True, (255, 255, 255))
        screen.blit(text, (WIDTH - 200, 10))

        pygame.display.flip()

    def draw_menu(self):
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 74)
        text = font.render("Color Gates Game", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 200, 75))
        font = pygame.font.Font(None, 36)
        text = font.render("1. Начать игру.", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 100, (HEIGHT // 2) - 150 + 25))
        text = font.render("2. Выбрать сложность.", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 100, (HEIGHT // 2) - 100 + 25))
        text = font.render("3. Посмотреть таблицу рекордов.", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 100, (HEIGHT // 2) - 50 + 25))
        text = font.render("4. Установить скорость.", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 100, (HEIGHT // 2) + 50 - 25))
        text = font.render("5. Об игре.", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 100, (HEIGHT // 2) + 100 - 25))
        text = font.render("6. Выход.", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 100, (HEIGHT // 2) + 150 - 25))
        pygame.display.flip()

    def draw_game_over(self):
        if not self.saving_score:
            screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 74)
            text = font.render("Game Over!", True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 - 100))
            font = pygame.font.Font(None, 36)
            text = font.render(f"Счет: {self.score}.", True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2))
            text = font.render("1. Сохранить рекорд.", True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 + 50))
            text = font.render("2. Обратно в главное меню.", True, (255, 255, 255))
            screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 + 100))
            pygame.display.flip()
        # else:
        #     screen.fill((0, 0, 0))
        #     font = pygame.font.Font(None, 74)
        #     text = font.render("Введите имя игрока", True, (255, 255, 255))
        #     screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2 - 100))
        #     font = pygame.font.Font(None, 36)
        #     text = font.render(self.player_name, True, (255, 255, 255))
        #     screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2))
        #     text = font.render("Нажмите Enter для сохранения", True, (255, 255, 255))
        #     screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 + 50))
        #     pygame.display.flip()

    def draw_pause(self):
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 74)
        text = font.render("Пауза!", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 100))
        font = pygame.font.Font(None, 36)
        text = font.render("ПРОБЕЛ - Продолжить.", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2))
        text = font.render("Esc - в меню.", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 + 50))
        # text = font.render("1. Начать заново", True, (255, 255, 255))
        # screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2))
        # text = font.render("2. Закончить", True, (255, 255, 255))
        # screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 + 50))
        # text = font.render("3. Продолжить", True, (255, 255, 255))
        # screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 + 100))
        pygame.display.flip()

    def generate_objects(self):
        # Старый уровень с тремя блоками одного цвета
        # Убрал, потому что слишком просто - зажимаются все дорожки, и все
        # Для полноценного уровня надо наследовать блок-препятствие
        # Стало быть, возможно, имеет смысл как-то выключать доожки...
        # if self.level_type == "single_color":
        #     if random.randint(0, 5) != 0:
        #         color = random.choice(['red', 'green', 'blue', 'yellow'])
        #         lanes = random.sample(range(4), 3)
        #         return [Square(color, lane) for lane in lanes]
        #     else:
        #         lanes = random.sample(range(4), 3)
        #         return [Heart(lane) for lane in lanes]
        if self.level_type == "multi_color":
            if random.randint(0, 8) != 0:
                colors = random.sample(['red', 'green', 'blue', 'yellow'], 2)
                lanes = random.sample(range(4), 2)
                return [Square(colors[i], lanes[i]) for i in range(2)]
            else:
                lanes = random.sample(range(4), 2)
                return [Heart(lane) for lane in lanes]
        else:
            if random.randint(0, 11) != 0:
                color = random.choice(['red', 'green', 'blue', 'yellow'])
                lane = random.randint(0, 3)
                return [Square(color, lane)]
            else:
                lane = random.randint(0, 3)
                return [Heart(lane)]

    def scroll_records(self, button):
        scroll_offset = self.scroll_offset
        if button == 4:  # Прокрутка вверх
            if self.scroll_offset > 0:
                screen.fill((0, 0, 0))
            scroll_offset = max(0, self.scroll_offset - 20)
        elif button == 5:  # Прокрутка вниз
            if self.scroll_offset < self.scores_height:
                screen.fill((0, 0, 0))
                scroll_offset = self.scroll_offset + 20
        #else:
        #    screen.fill((0, 0, 0))

        return scroll_offset

    def menu_loop(self):
        while True:
            self.draw_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                    # self.running = False
                    # return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        return  # Начать игру
                    elif event.key == pygame.K_2:
                        self.select_difficulty()
                    elif event.key == pygame.K_3:
                        self.scroll_offset = 0
                        screen.fill((0, 0, 0))
                        while True:
                            self.draw_high_scores()
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    exit()
                                    # self.running = False
                                    # return
                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_ESCAPE:
                                        break
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    self.scroll_offset = self.scroll_records(event.button)
                            else:
                                continue
                            break
                    elif event.key == pygame.K_4:
                        self.set_speed()
                    elif event.key == pygame.K_5:
                        self.about_game()
                    elif event.key == pygame.K_6:
                        exit()

    def game_loop(self):
        self.lives = 4
        self.score = 0
        self.objects = []
        self.grid_y = 0
        self.game_over = False
        self.paused = False
        while True:
            self.handle_events()
            if not self.paused:
                self.update()
                self.draw()
                self.clock.tick(self.speed)

                if self.game_over:
                    return

    def draw_save_score_menu(self):
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 74)
        text = font.render("Введите имя игрока:", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2 - 100))
        font = pygame.font.Font(None, 36)
        text = font.render(self.player_name, True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2))
        text = font.render("Нажмите Enter для сохранения.", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 + 50))
        text = font.render("Нажмите Escape для выхода в меню.", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 + 100))
        pygame.display.flip()

    def game_over_loop(self):
        while True:
            self.draw_game_over()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                    # self.running = False
                    # return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.saving_score = True
                        self.player_name = ""
                        while self.saving_score:
                            self.draw_save_score_menu()
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    exit()
                                    # self.running = False
                                    # return
                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_ESCAPE:
                                        return
                                    elif event.key == pygame.K_KP_ENTER:
                                        self.save_score(self.player_name, self.score)
                                        self.saving_score = False
                                        return  # Возвращаемся в главный цикл
                                    elif event.key == pygame.K_BACKSPACE:
                                        self.player_name = self.player_name[:-1]
                                    else:
                                        self.player_name += event.unicode
                    elif event.key == pygame.K_2:
                        return  # Вернуться в главное меню

    def run(self):
        while self.running:
            self.menu_loop()
            self.game_loop()
            self.game_over_loop()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
