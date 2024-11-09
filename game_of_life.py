import pygame, sys, random, copy, os
from pygame.locals import *
import ctypes
from math import floor

# user32 = ctypes.windll.user32

pygame.init()

screen_res = (pygame.display.Info().current_w, pygame.display.Info().current_h)

res = [(1, 1), (2, 2), (4, 4), (8, 8), (16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512)]
res_pointer = 5
figure_pointer = 1
paused = False
do_step = False

BLOCK_SIZE = BLOCK_W, BLOCK_H = res[res_pointer]
BLOCKS = BLOCKS_COLS, BLOCKS_ROWS = int(floor(screen_res[0] / res[res_pointer][0])), int(
    floor(screen_res[1] / res[res_pointer][1]))
size = width, height = (BLOCK_W * BLOCKS[0], BLOCK_H * BLOCKS[1])

screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

volume = 0.5
speed = 1

BACKGROUND = lambda: (255, 255, 255) if int(round(0.15686275 * volume * 255)) >= 255 else (
    int(round(0.15686275 * volume * 255)), int(round(0.15686275 * volume * 255)), int(round(0.15686275 * volume * 255)))
DARK_BACKGROUND = lambda: (255, 255, 255) if int(round(0.039215 * volume * 255)) > 255 else (
    int(round(0.039215 * volume * 255)), int(round(0.039215 * volume * 255)), int(round(0.039215 * volume * 255)))
LINES = lambda: (255, 255, 255) if int(round(0.07 * volume * 255)) >= 255 else (
    int(round(0.07 * volume * 255)), int(round(0.07 * volume * 255)), int(round(0.07 * volume * 255)))
FOREGROUND = lambda: (255, 255, 255) if int(round(0.58823529 * volume * 255)) >= 255 else (
    int(round(0.58823529 * volume * 255)), int(round(0.58823529 * volume * 255)), int(round(0.58823529 * volume * 255)))
LIGHT_FOREGROUND = lambda: (255, 255, 255) if int(round(0.9411 * volume * 255)) >= 255 else (
    int(round(0.9411 * volume * 255)), int(round(0.9411 * volume * 255)), int(round(0.9411 * volume * 255)))
SELECTED_FOREGROUND = lambda: (0, 255, 255) if int(round(0.8470588 * volume * 255)) >= 255 and int(
    round(0.40588 * volume * 255)) >= 255 else (
    (0, int(round(0.40588 * volume * 255)), 255) if int(round(0.8470588 * volume * 255)) >= 255 else (
        0, int(round(0.40588 * volume * 255)), int(round(0.8470588 * volume * 255))))


def SELECTED_BACKGROUND():
    c = (0, int(round(0.2196 * volume * 255)), int(round(0.43137255 * volume * 255)))
    if c[2] > 255:
        c = (int(round(0.2457 * volume * 255) - 111), int(round(0.2196 * volume * 255)), 255)
        if c[0] > 255 or c[1] > 255:
            c = (255, 255, 255)
    return c


def SELECTED_FOREGROUND():
    if volume < 1:
        return (0, int(round(0.4196 * volume * 255)), int(round(0.83137255 * volume * 255)))
    c = (0, int(round(0.2196 * volume * 255) + 30), int(round(0.43137255 * volume * 255) + 60))
    if c[2] > 255:
        c = (int(round(0.2457 * volume * 255) - 71), int(round(0.2196 * volume * 255) + 40), 255)
        if c[0] > 255 or c[1] > 255:
            c = (255, 255, 255)
    return c


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 38, 66)

counter = 0
intro_to_the_side = 0
paint_on = False
erease_on = False
escape_on = False
draw_size = 1
select_on = False
help_on = False
x_change = False
y_change = False
intro_on = True
running = False

font = pygame.font.SysFont('consolas', int(round(screen_res[0] * 0.007)))


class Grid:

    def __init__(self, screen):
        self.screen = screen
        self.figures = [[], [], [], [], [], [], [], [], [], []]
        self.selected_grid = [[0, 0], [0, 0]]
        self.cells = []
        for _ in range(BLOCKS_COLS):
            cell = [0] * BLOCKS_ROWS
            self.cells.append(cell)
        self.empty = []
        # self.randomize()
        self.load()

    def randomize(self):
        for x in range(BLOCKS_COLS):
            for y in range(BLOCKS_ROWS):
                if random.choice([True, False]):
                    self.cells[x][y] = 1
                else:
                    self.cells[x][y] = 0

    def delete_selection(self):
        selection = copy.deepcopy(self.selected_grid)
        if selection[1][0] < selection[0][0]:
            selection = [[selection[1][0], selection[0][1]], [selection[0][0], selection[1][1]]]
        if selection[1][1] < selection[0][1]:
            selection = [[selection[0][0], selection[1][1]], [selection[1][0], selection[0][1]]]
        for j in range(1, selection[1][0] - selection[0][0]):
            for i in range(1, selection[1][1] - selection[0][1]):
                self.cells[selection[0][0] + j][selection[0][1] + i] = 0

    def insert_selection(self):
        selection = copy.deepcopy(self.selected_grid)
        if selection[1][0] < selection[0][0]:
            selection = [[selection[1][0], selection[0][1]], [selection[0][0], selection[1][1]]]
        if selection[1][1] < selection[0][1]:
            selection = [[selection[0][0], selection[1][1]], [selection[1][0], selection[0][1]]]
        for j in range(1, selection[1][0] - selection[0][0]):
            for i in range(1, selection[1][1] - selection[0][1]):
                self.cells[selection[0][0] + j][selection[0][1] + i] = 1

    def clear(self):
        for x in range(BLOCKS_COLS):
            for y in range(BLOCKS_ROWS):
                self.cells[x][y] = 0

    def is_paused(self):
        global paused
        return paused

    def full(self):
        for x in range(BLOCKS_COLS):
            for y in range(BLOCKS_ROWS):
                self.cells[x][y] = 1

    def toggle_pause(self):
        global paused
        paused = not paused

    def toggle_step(self):
        global do_step
        do_step = True

    def coo(self, point):
        x, y = point
        return x // BLOCK_W, y // BLOCK_H

    def draw_figure(self, point):
        global figure_pointer
        x, y = point
        block_x, block_y = x // BLOCK_W, y // BLOCK_H
        spalen = 0
        try:
            for j in self.figures[figure_pointer]:
                if len(j) > spalen:
                    spalen = len(j)

            for j in range(len(self.figures[figure_pointer])):
                for i in range(spalen):
                    self.cells[block_x + j][block_y + i] = self.figures[figure_pointer][j][i]
        except:
            pass

    def draw_grid(self):
        for i in range(BLOCKS_COLS):
            start_point = (i * BLOCK_W, 0)
            end_point = (i * BLOCK_W, height)
            pygame.draw.line(self.screen, LINES(), start_point, end_point, 1)
        for i in range(BLOCKS_ROWS):
            start_point = (0, i * BLOCK_H)
            end_point = (width, i * BLOCK_H)
            pygame.draw.line(self.screen, LINES(), start_point, end_point, 1)

    def draw_cells(self):
        selection = copy.deepcopy(self.selected_grid)
        if selection[1][0] < selection[0][0]:
            selection = [[selection[1][0], selection[0][1]], [selection[0][0], selection[1][1]]]
        if selection[1][1] < selection[0][1]:
            selection = [[selection[0][0], selection[1][1]], [selection[1][0], selection[0][1]]]

        for x in range(BLOCKS_COLS):
            for y in range(BLOCKS_ROWS):
                if selection[0][0] < x < selection[1][0] and selection[0][1] < y < selection[1][1]:
                    if self.cells[x][y] and not help_on:
                        x2, y2 = x * BLOCK_W, y * BLOCK_H
                        cell = pygame.Rect([x2 + 1, y2 + 1, BLOCK_W - 1, BLOCK_H - 1])
                        pygame.draw.rect(self.screen, SELECTED_FOREGROUND(), cell)
                    else:
                        x2, y2 = x * BLOCK_W, y * BLOCK_H
                        cell = pygame.Rect([x2 + 1, y2 + 1, BLOCK_W - 1, BLOCK_H - 1])
                        pygame.draw.rect(self.screen, SELECTED_BACKGROUND(), cell)
                else:
                    if self.cells[x][y] and not help_on:
                        x2, y2 = x * BLOCK_W, y * BLOCK_H
                        cell = pygame.Rect([x2 + 1, y2 + 1, BLOCK_W - 1, BLOCK_H - 1])
                        pygame.draw.rect(self.screen, FOREGROUND(), cell)

    def border_at(self, point):
        borders = 0
        x, y = point
        points = ((x + 1, y), (x + 1, y + 1), (x, y + 1), (x - 1, y + 1), (x - 1, y),
                  (x - 1, y - 1), (x, y - 1), (x + 1, y - 1))
        for x2, y2 in points:
            try:
                if 0 <= x2 < BLOCKS_COLS and 0 <= y2 < BLOCKS_ROWS:
                    if self.cells[x2][y2]:
                        borders += 1
                else:
                    continue
            except IndexError:
                pass
        return borders

    def load(self):
        if not os.path.isdir("figures/"):
            os.mkdir("figures/")
        for i in range(10):
            if not os.path.isfile("figures/figure" + str(i) + ".txt"):
                with open("figures/figure" + str(i) + ".txt", "w") as createfile:
                    createfile.write("\n")
        for i in range(10):
            loadfile = open("figures/figure" + str(i) + ".txt", "r")
            lines = loadfile.readlines()
            for line in lines:
                if line.endswith("\n"):
                    line = line[:-1]
                line = line.split(",")
                for d in range(len(line)):
                    if line[d] == "":
                        line = []
                        break
                    else:
                        line[d] = int(line[d])
                self.figures[i].append(line)

    def save(self, sto):
        global figure_pointer
        x1, y1 = self.selected_grid[0]
        x2, y2 = self.selected_grid[1]

        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1

        figure = [[]]
        for j in range(1, x2 - x1):
            figure.append([])
            for i in range(1, y2 - y1):
                figure[j].append(self.cells[x1 + j][y1 + i])
        figure = figure[1:]
        figure_pointer = sto
        self.figures[sto] = copy.deepcopy(figure)
        with open("figures/figure" + str(sto) + ".txt", "w") as stofile:
            for line in figure:
                for d in range(len(line)):
                    line[d] = str(line[d])
                stofile.write(",".join(line) + "\n")

    def paint(self, point):
        global select_on
        if select_on:
            return
        x, y = point
        block_x, block_y = x // BLOCK_W, y // BLOCK_H

        for j in range(draw_size):
            for i in range(draw_size):
                try:
                    self.cells[block_x + j][block_y + i] = 1
                except:
                    pass

    def click(self, point, param=0):
        global select_on
        if select_on:
            return
        x, y = point
        block_x, block_y = x // BLOCK_W, y // BLOCK_H

        for j in range(draw_size):
            for i in range(draw_size):
                try:
                    self.cells[block_x + j][block_y + i] = (1 if param == 1 else (
                        0 if param == 2 else (0 if self.cells[block_x + j][block_y + i] or param == 2 else 1)))
                except:
                    pass

    def erease(self, point):
        x, y = point
        block_x, block_y = x // BLOCK_W, y // BLOCK_H

        for j in range(draw_size):
            for i in range(draw_size):
                try:
                    self.cells[block_x + j][block_y + i] = 0
                except:
                    pass

    def step(self):
        global paused, do_step
        if paused and not do_step:
            return
        cells = copy.deepcopy(self.cells)
        for x in range(BLOCKS_COLS):
            for y in range(BLOCKS_ROWS):
                borders = self.border_at((x, y))
                if not self.cells[x][y]:
                    if borders == 3:
                        cells[x][y] = 1
                elif self.cells[x][y]:
                    if not 2 <= borders <= 3:
                        cells[x][y] = 0
        self.cells = cells
        do_step = False


grid = Grid(screen)
clock = pygame.time.Clock()

number_events = {K_1: 1, K_2: 2, K_3: 3, K_4: 4, K_5: 5, K_6: 6, K_7: 7, K_8: 8, K_9: 9}

while True:
    for event in pygame.event.get():
        pressed = pygame.key.get_pressed()
        pressed_m = pygame.mouse.get_pressed()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == K_SPACE:
                grid.toggle_pause()
            elif event.key == K_r:
                grid.randomize()
            elif event.key == K_c:
                grid.clear()
            elif event.key == K_f:
                grid.full()
            elif event.key == K_d:
                if paint_on:
                    paint_on = False
                else:
                    paint_on = True
                    erease_on = False
            elif event.key == K_e:
                if erease_on:
                    erease_on = False
                else:
                    erease_on = True
                    paint_on = False
            elif event.key == K_UP:
                if volume < 3.3:
                    volume += 0.1
            elif event.key == K_DOWN:
                if volume >= 0.1:
                    volume -= 0.1
            elif event.key == K_ESCAPE:
                if escape_on == 3:
                    escape_on = 0
                else:
                    escape_on += 1
            elif event.key == K_F4 and pressed[K_LALT]:
                pygame.quit()
                sys.exit()
            elif event.key == K_DELETE and pressed[K_LCTRL]:
                grid.delete_selection()
            elif event.key == K_INSERT and pressed[K_LCTRL]:
                grid.insert_selection()
            elif event.key == K_RETURN:
                grid.toggle_step()
            elif event.key == K_F1:
                help_on = True
            if event.key in number_events and not pressed[K_TAB] and not pressed[K_LALT] and not pressed[K_LCTRL]:
                draw_size = number_events[event.key]
            elif event.key in number_events and pressed[K_LALT]:
                figure_pointer = number_events[event.key]
            elif event.key in number_events and pressed[K_LCTRL]:
                grid.save(number_events[event.key])
            elif event.key in number_events and pressed[K_TAB]:
                res_pointer = number_events[event.key]
                BLOCK_SIZE = BLOCK_W, BLOCK_H = res[res_pointer]
                BLOCKS = BLOCKS_COLS, BLOCKS_ROWS = int(round(2560 / res[res_pointer][0])), int(
                    round(1600 / res[res_pointer][1]))
                size = width, height = (BLOCK_W * BLOCKS[0], BLOCK_H * BLOCKS[1])
                screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
                grid = Grid(screen)

        elif event.type == pygame.KEYUP:
            if event.key == K_LCTRL:
                grid.selected_grid = [[0, 0], [0, 0]]
                select_on = False
            if event.key == K_F1:
                help_on = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pressed[K_LALT] or event.button == 3:
                grid.draw_figure(pygame.mouse.get_pos())
            elif pressed[K_LCTRL] and event.button == 1:
                if not select_on:
                    grid.selected_grid[0] = [grid.coo(pygame.mouse.get_pos())[0] - 1,
                                             grid.coo(pygame.mouse.get_pos())[1] - 1]
                    x_change, y_change = False, False
                select_on = True
            elif event.button == 4:
                if speed - .01 * speed > 1:
                    speed -= .01 * speed
                else:
                    speed = 1
            elif event.button == 5:
                speed += .01 * speed

        elif event.type == pygame.MOUSEBUTTONUP:
            if pressed[K_LCTRL]:
                select_on = False

        if pressed_m[0]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                grid.click(pygame.mouse.get_pos())
            elif pressed[K_LSHIFT]:
                grid.click(pygame.mouse.get_pos(), 2)
            else:
                grid.click(pygame.mouse.get_pos(), 1)

        if select_on:
            grid.selected_grid[1] = [grid.coo(pygame.mouse.get_pos())[0] + 1, grid.coo(pygame.mouse.get_pos())[1] + 1]
            if grid.selected_grid[0][0] > grid.selected_grid[1][0]:
                if not x_change:
                    grid.selected_grid[0][0] += 1
                grid.selected_grid[1][0] -= 1
                x_change = True
            else:
                if x_change:
                    grid.selected_grid[0][0] -= 1
                    x_change = False
            if grid.selected_grid[0][1] > grid.selected_grid[1][1]:
                if not y_change:
                    grid.selected_grid[0][1] += 1
                grid.selected_grid[1][1] -= 1
                y_change = True
            else:
                if y_change:
                    grid.selected_grid[0][1] -= 1
                    y_change = False

    if paint_on:
        grid.paint(pygame.mouse.get_pos())
    if erease_on:
        grid.erease(pygame.mouse.get_pos())
    if escape_on:
        if escape_on == 1:
            screen.fill(WHITE)
            pygame.display.flip()
        elif escape_on == 2:
            screen.fill(BLACK)
            pygame.display.flip()
        elif escape_on == 3:
            screen.fill(BLUE)
            pygame.display.flip()
    else:
        screen.fill(BACKGROUND())
        grid.draw_grid()
        grid.draw_cells()
        # clock.tick(24)
        if intro_on and intro_to_the_side < 1:
            intro_text = "F1 drücken für Hilfe"
            screen.blit(
                font.render(intro_text[:int(round(len(intro_text) * intro_to_the_side))], True, LIGHT_FOREGROUND()),
                (int(round(screen_res[0] * 0.01)), int(round(screen_res[0] * 0.01))))
            intro_to_the_side += 0.01
        elif intro_on:
            intro_text = "F1 drücken für Hilfe"
            screen.blit(font.render(intro_text, True, LIGHT_FOREGROUND()),
                        (int(round(screen_res[0] * 0.01)), int(round(screen_res[0] * 0.01))))
        if not intro_on and intro_to_the_side > 0:
            intro_text = "F1 drücken für Hilfe"
            screen.blit(
                font.render(intro_text[:int(round(len(intro_text) * intro_to_the_side))], True, LIGHT_FOREGROUND()),
                (int(round(screen_res[0] * 0.01)), int(round(screen_res[0] * 0.01))))
            intro_to_the_side -= 0.01
        if help_on:
            figure_stored = []
            for i in range(len(grid.figures)):
                if grid.figures[i] != [[]]:
                    figure_stored.append(str(i))
            figure_stored = ", ".join(figure_stored)
            help_text = [
                'Conway\'s Game of Life',
                '____________________________________________',
                'Zeichnen Modus:     ' + (
                    "Keine" if not paint_on and not erease_on else ("Zeichnen" if paint_on else "Radieren")),
                'Zeichnen Größe:     ' + str(draw_size),
                'Block Größe:        ' + str(res[res_pointer][0]),
                'Pausiert:           ' + ("Ja" if grid.is_paused() else "Nein"),
                'Verfügbare Figuren: ' + figure_stored,
                'Figur Auswahl:      ' + str(figure_pointer),
                'Geschwindigkeit:    ' + str(int(round(100 / speed, 0))) + '%',
                '____________________________________________',
                'Optionen:',
                ' - Click li:  Zelle an/aus',
                ' - Click re:  Figur einfügen',
                ' - Mausrad:   Geschwindigkeit einstellen',
                ' - Pfeile:    Helligkeit einstellen',
                ' - Leertaste: Pausieren/Fortführen',
                ' - Enter:     Schrittweise Fortführen',
                ' - Escape:    Bildschirm Schwarz/Weiß',
                ' - r:         Muster zufällig generieren',
                ' - f:         Alles aktiv',
                ' - c:         Alles inaktiv',
                ' - d:         Zeichnen an/aus',
                ' - e:         Radieren an/aus',
                ' - F1:        Hilfe/Status einblenden',
                '',
                ' - Tab:',
                '     - 1, 2, 3...:   Blockgröße verändern',
                '',
                ' - Alt:',
                '     - 1, 2, 3...:   Figur auswählen',
                '     - Click:        Figur einfügen',
                '',
                ' - Strg:',
                '     - Click & Drag: Bereich markieren',
                '     - 1, 2, 3...:   Bereich speichern',
                '     - Entf:         Bereich deaktivieren',
                '     - Einfg:        Bereich aktivieren',
                '',
                ' - Maus:',
                '     - Halten li:    Zeichnen',
                '     -   + Shift:    Radieren',
                ''
            ]
            for i in range(len(help_text)):
                screen.blit(font.render(help_text[i], True, LIGHT_FOREGROUND()), (
                    int(round(screen_res[0] * 0.12)), int(round(screen_res[0] * 0.12)) + i * screen_res[0] * 0.01))

        counter += 1

        if counter > 1000:
            intro_on = False
        pygame.display.flip()
        if counter % round(speed * 100 - 99, 0) == 0:
            grid.step()
