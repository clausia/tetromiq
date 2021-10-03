import random
import pygame
import numpy as np
from src.constants import *
from src.exceptions import *


class Block(pygame.sprite.Sprite):

    @staticmethod
    def collide(block, group):
        """
        Check if the specified block collides with some other block in the group.
        """
        for other_block in group:
            # Ignore the current block which will always collide with itself
            if block == other_block:
                continue
            if other_block.quantum_block is not None and not other_block.bottom_reach:
                continue
            if pygame.sprite.collide_mask(block, other_block) is not None:
                return True
        return False

    def __init__(self):
        super().__init__()
        self.quantum_block = None
        self.current = True
        self.struct = np.array(self.struct)
        # Initial random rotation
        if random.randint(0, 1):
            self.struct = np.rot90(self.struct)
        self._draw()

    def _draw(self, x=5, y=0):
        width = len(self.struct[0]) * TILE_SIZE
        height = len(self.struct) * TILE_SIZE
        small_width = len(self.struct[0]) * SMALL_TILE_SIZE
        small_height = len(self.struct) * SMALL_TILE_SIZE
        self.image = pygame.surface.Surface([width, height])
        self.image.set_colorkey((0, 0, 0))
        # Small image for upcoming blocks
        self.small_image = pygame.surface.Surface([small_width, small_height])
        self.small_image.set_colorkey((0, 0, 0))
        # Position and size
        self.rect = pygame.Rect(0, 0, width, height)
        self.x = x
        self.y = y
        for y, row in enumerate(self.struct):
            for x, col in enumerate(row):
                if col:
                    pygame.draw.rect(self.image, self.color,
                                     pygame.Rect(x * TILE_SIZE + 1, y * TILE_SIZE + 1,
                                                 TILE_SIZE - 2, TILE_SIZE - 2))
                    self._draw_deep(x, y)
                    pygame.draw.rect(self.small_image, self.color,
                                     pygame.Rect(x * SMALL_TILE_SIZE + 1, y * SMALL_TILE_SIZE + 1,
                                                 SMALL_TILE_SIZE - 2, SMALL_TILE_SIZE - 2))
        self._create_mask()

    def _draw_deep(self, x, y, width_highlight=1):
        pygame.draw.line(self.image, (255, 255, 255),
                         (x * TILE_SIZE + 5, y * TILE_SIZE + 5),
                         (TILE_SIZE * (x + 1) - 6, y * TILE_SIZE + 5),
                         width=width_highlight)
        pygame.draw.line(self.image, (255, 255, 255),
                         (TILE_SIZE * (x + 1) - 6, y * TILE_SIZE + 5),
                         (TILE_SIZE * (x + 1) - 6, TILE_SIZE * (y + 1) - 6),
                         width=width_highlight)

    def redraw(self):
        self._draw(self.x, self.y)

    def draw_highlight(self):
        for y, row in enumerate(self.struct):
            for x, col in enumerate(row):
                if col:
                    self._draw_deep(x, y, 3)

    def _create_mask(self):
        """
        Create the mask attribute from the main surface.
        The mask is required to check collisions. This should be called after the surface is created or update.
        """
        self.mask = pygame.mask.from_surface(self.image)

    def initial_draw(self):
        raise NotImplementedError

    @property
    def group(self):
        return self.groups()[0]

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self.rect.left = value * TILE_SIZE

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self.rect.top = value * TILE_SIZE

    def move_left(self, group):
        self.x -= 1
        # Check if we reached the left margin
        if self.x < 0 or Block.collide(self, group):
            self.x += 1

    def move_right(self, group):
        self.x += 1
        # Check if we reached the right margin or collided with another block
        if self.rect.right > GRID_WIDTH or Block.collide(self, group):
            # Rollback
            self.x -= 1

    def move_down(self, group):
        self.y += 1
        # Check if the block reached the bottom or collided with another one
        if self.rect.bottom > GRID_HEIGHT or Block.collide(self, group):
            # Rollback to the previous position
            self.y -= 1
            self.current = False
            raise BottomReached

    def rotate(self, group):
        self.image = pygame.transform.rotate(self.image, 90)
        # Once rotated we need to update the size and position
        self.rect.width = self.image.get_width()
        self.rect.height = self.image.get_height()
        self._create_mask()
        # Check the new position doesn't exceed the limits or collide with other blocks
        # and adjust it if necessary
        while self.rect.right > GRID_WIDTH:
            self.x -= 1
        while self.rect.left < 0:
            self.x += 1
        while self.rect.bottom > GRID_HEIGHT:
            self.y -= 1
        while True:
            if not Block.collide(self, group):
                break
            self.y -= 1
        self.struct = np.rot90(self.struct)


class SquareBlock(Block):
    struct = (
        (1, 1),
        (1, 1)
    )
    color_100 = (92, 142, 38)
    color_50 = (146, 208, 80)
    color_25 = (196, 229, 159)
    color = color_100


class TBlock(Block):
    struct = (
        (1, 1, 1),
        (0, 1, 0)
    )
    color_100 = (255, 51, 204)
    color_50 = (255, 139, 225)
    color_25 = (255, 205, 242)
    color = color_100


class LineBlock(Block):
    struct = (
        (1,),
        (1,),
        (1,),
        (1,)
    )
    color_100 = (0, 136, 184)
    color_50 = (5, 190, 255)
    color_25 = (113, 218, 255)
    color = color_100


class LBlock(Block):
    struct = (
        (1, 1),
        (1, 0),
        (1, 0),
    )
    color_100 = (112, 48, 160)
    color_50 = (165, 104, 210)
    color_25 = (205, 172, 230)
    color = color_100


class LIBlock(Block):
    struct = (
        (1, 1),
        (0, 1),
        (0, 1),
    )
    color_100 = (238, 138, 18)
    color_50 = (245, 186, 115)
    color_25 = (250, 222, 188)
    color = color_100


class ZBlock(Block):
    struct = (
        (0, 1),
        (1, 1),
        (1, 0),
    )
    color_100 = (172, 0, 0)
    color_50 = (255, 0, 0)
    color_25 = (255, 113, 113)
    color = color_100


class ZIBlock(Block):
    struct = (
        (1, 0),
        (1, 1),
        (0, 1),
    )
    color_100 = (0, 81, 242)
    color_50 = (91, 146, 255)
    color_25 = (171, 199, 255)
    color = color_100
