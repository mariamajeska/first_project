import pyglet
from pyglet.window import key
from pyglet.window import mouse
from random import randrange
from pathlib import Path
from pyglet.gl import gl

SNAKE_LENGHT = 3
PLAY = ['F']  # state of game setup
SIZE = 64
direction = [(0, 1)]  # initial snake direction
opposites = {"left": "right", "right": "left", "top": "bottom", "bottom": "top"}


# game reset
def reset():
    new_direction = 0, 1  # initial snake direction setup
    direction.append(new_direction)
    direction.pop(0)
    state.reset()


# backround colour setup
def init():
    gl.glClearColor(0.9, 0.9, 0.9, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)


window = pyglet.window.Window(width=1280, height=764 - 64, caption="Pyglet+OpenGL")


# loading images
TILES_DIRECTORY = Path('snake-tiles')
snake_tiles = {}
for path in TILES_DIRECTORY.glob('*.png'):
    snake_tiles[path.stem] = pyglet.image.load(path)
red_apple = pyglet.image.load('apple.png')
winner = pyglet.image.load('Winner.png')
game_over = pyglet.image.load('game_over.png')
snake_game = pyglet.image.load('icon_snake_game.png')
start = pyglet.image.load('Play2.png')
quit = pyglet.image.load('Quit2.png')
back = pyglet.image.load('Return2.png')
pause = pyglet.image.load('Pause.png')
winner.anchor_x = winner.width // 2
winner.anchor_y = winner.height // 2
game_over.anchor_x = game_over.width // 2
game_over.anchor_y = game_over.height // 2
snake_game.anchor_x = snake_game.width // 2
snake_game.anchor_y = snake_game.height // 2

# intro screen setup
intro = pyglet.graphics.Batch()
BACK = pyglet.sprite.Sprite(back)
SNAKE_GAME = pyglet.sprite.Sprite(
    snake_game, window.width // 3, window.height // 2, batch=intro)
START = pyglet.sprite.Sprite(
    start, 3 * window.width // 4, window.height // 2, batch=intro)
QUIT = pyglet.sprite.Sprite(
    quit, 3 * window.width // 4, 0.5 * window.height // 2, batch=intro)
PAUSE = pyglet.sprite.Sprite(pause, window.width // 14)
SNAKE_GAME.scale = 1.5
START.scale = 0.3
QUIT.scale = 0.3
BACK.scale = 0.2
PAUSE.scale = 0.2

# snake game setup
class GAME_STATE():
    def __init__(self):
        self.position = [(0, 1), (1, 1)]
        self.direction = direction
        self.sprites = []
        self.food = [(0, 3)]
        self.segments = []
        self.snake_alive = True
        self.moving = False
        self.draw_snake()
        self.draw_food()

    # snake segments direction setup
    def set_direction(self):
        dir2 = []
        dir1 = []
        segments = []
        for i in range(len(self.position)):
            if self.position[i] == self.position[(len(self.position)-1)]:
                dir2.append("head")
            elif self.position[i][0] < self.position[i+1][0]:
                dir2.append("right")
            elif self.position[i][0] > self.position[i+1][0]:
                dir2.append("left")
            elif self.position[i][1] < self.position[i+1][1]:
                dir2.append("top")
            elif self.position[i][1] > self.position[i+1][1]:
                dir2.append("bottom")

        if not self.snake_alive:
            dir2[dir2.index("head")] = "dead"

        for i in range(len(self.position)):
            if self.position[i] == self.position[0]:
                dir1.append("tail")
            else:
                dir1.append(opposites[dir2[i-1]])
            segment = (self.position[i], dir1[i] + '-' + dir2[i])
            segments.append(segment)
            self.segments = segments

    # drawing the snake
    def draw_snake(self):
        self.set_direction()
        batch = pyglet.graphics.Batch()
        if len(self.position) < SNAKE_LENGHT:
            for n in self.segments:
                temp = pyglet.sprite.Sprite(
                    snake_tiles[n[1]], n[0][0] * SIZE, n[0][1] * SIZE, batch=batch)
                self.sprites.append(temp)
            if not self.snake_alive:
                temp = pyglet.sprite.Sprite(
                    game_over, window.width // 2, window.height // 2, batch=batch)
        else:
            temp = pyglet.sprite.Sprite(
                winner, window.width // 2, window.height // 2, batch=batch)
        batch.draw()

    # drawing the food
    def draw_food(self):
        for x, y in self.food:
            apple = pyglet.sprite.Sprite(red_apple, x * SIZE, y * SIZE)
            apple.draw()

    # adding a new food
    def add_food(self):
        for n in range(100):
            x = randrange(window.width // SIZE)
            y = randrange(window.height // SIZE)
            food = x, y
            if food not in self.position and food not in self.food:
                self.food.append(food)
                return

    def draw(self):
        self.draw_snake()
        self.draw_food()

    def move(self, dt):
        # pause setup
        # to pause the game click the PAUSE button with mouse-left,
        # to unpause the game click the PAUSE button with mouse-right
        if PLAY[-1] == 'S':
            self.moving = True
        elif PLAY[-1] == 'P':
            self.moving = False
        elif PLAY[-1] == 'R':
            self.moving = True
        else:
            self.moving = False

        # snake movement setup
        if self.moving:
            old_x, old_y = self.position[-1]
            dir_x = self.direction[0][0]
            dir_y = self.direction[0][1]
            new_x = old_x + dir_x
            new_y = old_y + dir_y
            snake_head = new_x, new_y
        else:
            old_x, old_y = self.position[-1]
            snake_head = old_x, old_y
            return

        # snake death setup
        for sprite in self.sprites:
            if new_x < 0 or new_y < 0:
                self.snake_alive = False
            if new_x * SIZE >= window.width:
                self.snake_alive = False
            if new_y * SIZE >= window.height:
                self.snake_alive = False
            if snake_head in self.position:
                self.snake_alive = False

        if not self.snake_alive:
            return

        # growth of snake setup
        if snake_head in self.food:
            self.food.remove(snake_head)
            self.position.append((snake_head))
            self.add_food()
        else:
            self.position.append((snake_head))
            self.position.pop(0)

    def reset(self):
        self.position = [(0, 1), (1, 1)]
        self.direction = direction
        self.sprites = []
        self.food = [(0, 3)]
        self.segments = []
        self.snake_alive = True
        self.moving = True


state = GAME_STATE()


@window.event
def draw():
    window.clear()
    init()
    if PLAY[-1] == 'S':
        state.draw()
        BACK.draw()
        PAUSE.draw()
    elif PLAY[-1] == 'Q':
        exit()
    elif PLAY[-1] == 'B':
        intro.draw()
        reset()
    elif PLAY[-1] == 'P':
        state.draw()
        BACK.draw()
        PAUSE.draw()
    elif PLAY[-1] == 'R':
        state.draw()
        BACK.draw()
        PAUSE.draw()
    else:
        intro.draw()


# control of the snake movement
def on_key_press(symbol, modifier):
    if symbol == key.LEFT:
        new_direction = -1, 0
        direction.append(new_direction)
        direction.pop(0)
    if symbol == key.RIGHT:
        new_direction = 1, 0
        direction.append(new_direction)
        direction.pop(0)
    if symbol == key.UP:
        new_direction = 0, 1
        direction.append(new_direction)
        direction.pop(0)
    if symbol == key.DOWN:
        new_direction = 0, -1
        direction.append(new_direction)
        direction.pop(0)


# checking the pressed button
def on_mouse_action(x, y, sprite):
    if x in range(int(sprite.x), int(sprite.x + sprite.width)) and y in range(
        int(sprite.y), int(sprite.y + sprite.height)):
        return True
    else:
        return False


# on mouse pressing buttons
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        if on_mouse_action(x, y, START):
            PLAY.append('S')
        elif on_mouse_action(x, y, QUIT):
            PLAY.append('Q')
        elif on_mouse_action(x, y, BACK):
            PLAY.append('B')
        elif on_mouse_action(x, y, PAUSE):  # PAUSE
            PLAY.append('P')
    if button == mouse.RIGHT:
        if on_mouse_action(x, y, PAUSE):  # UNPAUSE
            PLAY.append('R')
        else:
            pass


window.push_handlers(
    on_draw=draw,
    on_key_press=on_key_press,
    on_mouse_press=on_mouse_press,
    )


def move(dt):
    state.move(dt)


pyglet.clock.schedule_interval(move, 0.4)


pyglet.app.run()
