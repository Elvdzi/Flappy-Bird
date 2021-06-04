import pygame
import neat
import time
import os
import random

WIN_WIDTH = 600
WIN_HEIGHT = 800

BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png"))),
]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = PIPE_IMG = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "bg.png"))
)


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25  # tilting of the bird
    ROT_VEL = 20  # how much rotation each frame
    ANIMATION_TIME = 5

    # starting position of the bird
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0  # looking flat
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0  # which image currently showing
        self.img = self.IMGS[0]  # bird images

    def jump(self):
        self.vel = -10.5  # neg velocity -> upwards
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1  # how many movements since last jump

        d = (
            self.vel * (self.tick_count) + 1.5 * (self.tick_count) ** 2
        )  # how much moving up or down

        if d >= 16:  # limit so it does not move to far up or down
            d = 16

        if d < 0:  # how much it jumps
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:  # tilt the bird upwards
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:  # when diving down, nose is pointing downwards
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1  # keeps track of how many times game loop runs

        # checks what image to show based on img_count
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif (
            self.img_count <= self.ANIMATION_TIME * 4
        ):  # second image again - wings in middle
            self.img = self.IMGS[1]
        elif (
            self.img_count == self.ANIMATION_TIME * 4 + 1
        ):  # first image again - wings up
            self.img = self.IMGS[0]
            self.img_count = 0  # reset image count

        # not flapping wings when going downwards
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2  # jumps back up

        # rotate image around its center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center
        )
        win.blit(rotated_image, new_rect.topleft)

    # collision
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200  # space in between pipes
    VEL = 5  # how fast the pipes moves

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0  # top of pipe
        self.bottom = 0  # bottom of pipe
        self.PIPE_TOP = pygame.transfrom.flip(PIPE_IMG, False, True)  # upside-down pipe
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False  # if the bird passed the pipe
        self.set_height()  # define top and bottom of pipe and how tall it is

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()  # locate the pipe
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL  # every time called, the pipe moves to left

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (
            self.x - bird.x,
            self.top - round(bird.y),
        )  # how far away the two tophand corners are
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(
            bottom_mask, bottom_offset
        )  # point of overlap between bird and bottom pipe
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:  # if they are not none => colliding
            return True

        return False


class Base:
    VEL = 5  # same as pipe
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, bird):
    win.blit(BG_IMG, (0, 0))
    bird.draw(win)
    pygame.display.update()


def main():
    bird = Bird(200, 200)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)  # 30 ticks every second
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        bird.move()
        draw_window(win, bird)

    pygame.quit()
    quit()


main()
