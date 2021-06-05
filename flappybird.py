"""
The classic game of flappy bird with an AI playing it using NEAT python module.

@author Elvira Dzidic
Date Modified: june 5, 2021
"""
import pygame
import neat
import time
import os
import random

pygame.font.init()

WIN_WIDTH = 570  # changed to fit screen
WIN_HEIGHT = 800

GEN = 0

BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png"))),
]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

# Bird class representing the flappy bird
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

    # make the bird jump
    def jump(self):
        self.vel = -10.5  # neg velocity -> upwards
        self.tick_count = 0
        self.height = self.y

    # make the bird move
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


# Pipe class representing the pipes
class Pipe:
    GAP = 200  # space in between pipes
    VEL = 5  # how fast the pipes moves

    # initialize the pipe object
    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0  # top of pipe
        self.bottom = 0  # bottom of pipe
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)  # upside-down pipe
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False  # if the bird passed the pipe
        self.set_height()  # define top and bottom of pipe and how tall it is

    # set the hight of the pipe from the top of the screen
    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()  # locate the pipe
        self.bottom = self.height + self.GAP

    # move pipe based on velocity (vel)
    def move(self):
        self.x -= self.VEL  # every time called, the pipe moves to left

    # draw the top and bottom of the pipe
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # returns True if a point in the bird is colliding with the pipe
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


# Base class representing the floor
class Base:
    VEL = 5  # same as pipe
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    # initialize the base object
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    # move two pictures of the floor so it looks like its scrolling
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    # draws the floor by using two images that moves together
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


# draws the window for the main game loop
def draw_window(win, birds, pipes, base, score, gen):
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    # score
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    # generation
    text = STAT_FONT.render("Generation: " + str(gen), 1, (255, 255, 255, 255))
    win.blit(text, (10, 10))

    base.draw(win)

    for bird in birds:
        bird.draw(win)

    pygame.display.update()


# fitness function based on the distance the birds reach in the game
def main(genomes, config):
    global GEN
    GEN += 1
    # each position in the lists will correspond to a bird
    nets = []
    ge = []
    birds = []

    # neural network for genome
    for _, g in genomes:  # genome is a touple with genomeid and object
        net = neat.nn.FeedForwardNetwork.create(g, config)  # gnome, config file
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0  # start with fitness level 0
        ge.append(g)

    base = Base(730)  # 730 is the floor
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        clock.tick(30)  # 30 ticks every second
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if (
                len(pipes) > 1
                and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width()
            ):  # determine whether to use first or second pipe on the screen as input for neural network
                pipe_ind = 1
        else:  # no birds left
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[
                x
            ].fitness += 0.1  # give each bird a fitness for each frame it stays alive

            # send bird, top pipe and bottom pipe location to determine from network whether to jump or not
            output = nets[x].activate(
                (
                    bird.y,
                    abs(bird.y - pipes[pipe_ind].height),
                    abs(bird.y - pipes[pipe_ind].bottom),
                )
            )

            if output[0] > 0.5:
                bird.jump()

        # bird.move()
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):  # check if every pipe collide with every bird
                    ge[x].fitness -= 1  # every time a bird hits a pipe, remove fitness

                    # remove the bird
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    # when bird passes pipe - generate a new
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:  # pipe of the screen
                rem.append(pipe)  # remove the pipe

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += (
                    5  # every gnome in the list is still alive and gains fitness-score
                )
            pipes.append(Pipe(700))  # add new pipe

        # remove old pipes
        for r in rem:
            pipes.remove(r)

        # if a bird hits the ground or go too high up, remove the bird from the list
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score, GEN)


# run the NEAT algorithm to train a neural network to play flappy bird and defines all subheadings
def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    p = neat.Population(config)  # setting population

    # output
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)  # main is our fitness function, it's called 50 times


if __name__ == "__main__":
    # path to config file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
