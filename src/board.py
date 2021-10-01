from collections import OrderedDict
from blocks import *
import numpy as np
import pygame


class BlocksGroup(pygame.sprite.OrderedUpdates):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self._current_block_movement_heading = None
        self._reset_grid()
        self._ignore_next_stop = False
        self.score = 0
        self.lines = 0
        self.level = 1
        self.next_blocks = []
        # Not really moving, just to initialize the attribute
        self.stop_moving_current_block()
        # The first block to play with
        self._create_new_block()

    def _get_random_block(self):
        while len(self.next_blocks) < PREVIEW_BLOCKS:
            self.next_blocks.append(
                np.random.choice((SquareBlock, TBlock, LineBlock, LBlock, LIBlock, ZBlock, ZIBlock))())

    def _check_line_completion(self):
        """
        Check each line of the grid and remove the ones that are complete.
        """
        # Start checking from the bottom
        for i, row in enumerate(self.grid[::-1]):
            if all(row):
                self.score += 5
                self.lines += 1
                
                # Check if level changed
                if self.lines >= LINES_TO_CHANGE_LEVEL * self.level:
                    self.level += 1
        
                # Get the blocks affected by the line deletion and remove duplicates
                affected_blocks = list(OrderedDict.fromkeys(self.grid[-1 - i]))

                # Position in which the line was created
                line_position_y = NUM_ROWS - 1 - i

                for block, y_offset in affected_blocks:
                    # Remove the block tiles which belong to the completed line
                    block.struct = np.delete(block.struct, y_offset, 0)
                    if block.struct.any():
                        # Once removed, check if we have empty columns since they need to be dropped
                        block.struct, x_offset = remove_empty_columns(block.struct)
                        # Compensate the space gone with the columns to keep the block's original position
                        block.x += x_offset
                        # Force redraw
                        block.redraw()
                    else:
                        # If the struct is empty then the block is gone
                        self.remove(block)

                # Only the blocks that are above the line should be moved down one position,
                # as the line they were resting on has disappeared
                for block in self:
                    # Except the current block, since it's just falling
                    if block.current:
                        continue
                    if block.y <= line_position_y:
                        # Pull down each block one position, validate if it reaches the bottom
                        # or collides with another block
                        try:
                            block.move_down(self)
                        except BottomReached:
                            continue

                self.update_grid()
                # Since we've updated the grid, now the i counter is no longer valid, so call the
                # function again to check if there are other completed lines in the new grid
                self._check_line_completion()
                break

    def _reset_grid(self):
        self.grid = [[0 for _ in range(NUM_COLUMNS)] for _ in range(NUM_ROWS)]

    def _create_new_block(self):
        self._get_random_block()
        new_block = self.next_blocks.pop(0)
        if Block.collide(new_block, self):
            raise TopReached
        self.add(new_block)
        self.update_grid()
        self._check_line_completion()
        self._get_random_block()

    def update_grid(self):
        self._reset_grid()
        for block in self:
            for y_offset, row in enumerate(block.struct):
                for x_offset, digit in enumerate(row):
                    # Prevent replacing previous blocks
                    if digit == 0:
                        continue
                    rowid = block.y + y_offset
                    colid = block.x + x_offset
                    self.grid[rowid][colid] = (block, y_offset)

    @property
    def current_block(self):
        return self.sprites()[-1]

    def update_current_block(self):
        try:
            self.current_block.move_down(self)
        except BottomReached:
            self.stop_moving_current_block()
            self._create_new_block()
        else:
            self.update_grid()

    def move_current_block(self):
        # First check if there's something to move
        if self._current_block_movement_heading is None:
            return
        action = {
            pygame.K_DOWN: self.current_block.move_down,
            pygame.K_LEFT: self.current_block.move_left,
            pygame.K_RIGHT: self.current_block.move_right
        }
        try:
            # Each function requires the group as the first argument to check any possible collision
            action[self._current_block_movement_heading](self)
        except BottomReached:
            self.stop_moving_current_block()
            self._create_new_block()
        else:
            self.update_grid()

    def start_moving_current_block(self, key):
        if self._current_block_movement_heading is not None:
            self._ignore_next_stop = True
        self._current_block_movement_heading = key

    def stop_moving_current_block(self):
        if self._ignore_next_stop:
            self._ignore_next_stop = False
        else:
            self._current_block_movement_heading = None

    def rotate_current_block(self):
        # Prevent SquareBlocks rotation
        if not isinstance(self.current_block, SquareBlock):
            self.current_block.rotate(self)
            self.update_grid()

    def split_current_block(self):
        # Superposed current block
        if self.current_block.superposed is None:
            # If the block does not yet belong to a set of superposed blocks
            superposed_set = QuantumBlock(self.current_block)
            self.remove(self.current_block)
        else:
            pass
        for sub_block in superposed_set.set_blocks:
            if sub_block is not None:
                self.add(sub_block)
        self.update_grid()


def draw_grid(background):
    """
    Draw the background grid.
    """
    grid_color = 50, 50, 50
    # Vertical lines
    for i in range(NUM_COLUMNS + 1):
        x = TILE_SIZE * i
        pygame.draw.line(background, grid_color, (x, 0), (x, GRID_HEIGHT))
    # Horizontal lines
    for i in range(NUM_ROWS + 1):
        y = TILE_SIZE * i
        pygame.draw.line(background, grid_color, (0, y), (GRID_WIDTH, y))


def remove_empty_columns(block, _x_offset=0, _keep_counting=True):
    """
    Remove empty columns from 'block' (i.e. those filled with zeros).
    The return value is (new_block, x_offset), where x_offset is how much the x coordinate needs to be
    increased in order to maintain the block's original position.
    """
    for colid, col in enumerate(block.T):
        if col.max() == 0:
            if _keep_counting:
                _x_offset += 1
            # Remove the current column and try again
            block, _x_offset = remove_empty_columns(np.delete(block, colid, 1), _x_offset, _keep_counting)
            break
        else:
            _keep_counting = False
    return block, _x_offset
