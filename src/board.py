from collections import OrderedDict
from src.quantum_block import *
from src.quantum import *
import numpy as np
import pygame
from pathlib import Path


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
        self.collapsed_blocks = []
        # Not really moving, just to initialize the attribute
        self.stop_moving_current_block()
        # The first block to play with
        self._create_new_block()

    def _get_random_block(self):
        while len(self.next_blocks) < PREVIEW_BLOCKS:
            self.next_blocks.append(
                np.random.choice((SquareBlock, TBlock, LineBlock, LBlock, LIBlock, ZBlock, ZIBlock))())

    def _check_line_completion(self, effects):
        """
        Check each line of the grid and remove the ones that are complete.
        """
        # Start checking from the bottom
        for i, row in enumerate(self.grid[::-1]):
            if all(row):

                if self._verify_if_quantum_block_involved(row, i):
                    self._check_line_completion(effects)
                    break

                self.score += self._determine_increase_score(row)
                self.lines += 1
                if effects:
                    effects.play_line_created_sound()
                
                # Check if level changed
                if self.lines >= LINES_TO_CHANGE_LEVEL * self.level:
                    self.level += 1
                    if effects:
                        effects.play_level_up_sound()
        
                # Get the blocks affected by the line deletion and remove duplicates
                affected_blocks = list(OrderedDict.fromkeys(self.grid[-1 - i]))

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

                # Position in which the line was created
                line_position_y = NUM_ROWS - 1 - i

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
                self._check_line_completion(effects)
                break
    
        self.collapsed_blocks.clear()

    def _verify_if_quantum_block_involved(self, row, i):
        # Check first if there is any quantum block involved in the creation of the line,
        # because when collapsing it could be that the line is no longer created anymore
        collapsed = False
        for square in row:
            if square != 0 and square[0].quantum_block is not None:
                # The square belongs to a quantum block
                collapsed_block = collapse(square[0].quantum_block)

                for sub_block in square[0].quantum_block.set_blocks:
                    if sub_block is not None and sub_block is not collapsed_block:
                        sub_block.quantum_block = None
                        self.remove(sub_block)

                self.update_grid()
                self._move_down_blocks_above()

                collapsed_block.color = collapsed_block.color_100
                collapsed_block.redraw()
                collapsed_block.quantum_block = None

                self.collapsed_blocks.append(collapsed_block)

                collapsed = True
        return collapsed
    
    def _determine_increase_score(self, row):
        if len(self.collapsed_blocks) == 0:
            return SCORE_INCREMENT
        else:
            factor = 1
            for block in self.collapsed_blocks:
                for square in row:
                    if square != 0 and square[0] is block:
                        # If the collapsed block is part of a line, the score is increased 
                        # by a factor of 2 for pieces in superposition at 50% or 
                        # by a factor of 4 for pieces in superposition at 25%.
                        factor = factor * (2 if block.is_50 else 4)
                        break
                
            return SCORE_INCREMENT * factor


    def _move_down_blocks_above(self):
        for block in self:
            if block.current:
                continue
            while True:
                try:
                    block.move_down(self)
                except BottomReached:
                    break
        self.update_grid()

    def _reset_grid(self):
        self.grid = [[0 for _ in range(NUM_COLUMNS)] for _ in range(NUM_ROWS)]

    def _create_new_block(self, effects=None):
        self._check_line_completion(effects)
        self._get_random_block()
        new_block = self.next_blocks.pop(0)
        self.add(new_block)
        self.update_grid()
        if Block.collide(new_block, self):
            raise TopReached
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

    def update_current_block(self, effects):
        if self.current_block.quantum_block is None:  # Normal behavior of a block
            try:
                self.current_block.move_down(self)
            except BottomReached:
                self.stop_moving_current_block()
                self._create_new_block(effects)
            else:
                self.update_grid()
        else:                                      # Superposed block behavior
            self._update_current_block_quantum()

    def _update_current_block_quantum(self):
        # Move down all superposed blocks
        for block in self.current_block.quantum_block.set_blocks:
            if block is not None and not block.bottom_reach:
                try:
                    block.move_down(self)
                except BottomReached:
                    self._verify_bottom_reach_superposed_blocks(block)
                else:
                    self.update_grid()

    def move_current_block(self, effects):
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
            if self.current_block.quantum_block is None:  # Normal behavior of a block
                self.stop_moving_current_block()
                self._create_new_block(effects)
            else:
                self._verify_bottom_reach_superposed_blocks(self.current_block)
        else:
            self.update_grid()
            effects.play_piece_moved_sound()

    def start_moving_current_block(self, key):
        if self._current_block_movement_heading is not None:
            self._ignore_next_stop = True
        self._current_block_movement_heading = key

    def stop_moving_current_block(self):
        if self._ignore_next_stop:
            self._ignore_next_stop = False
        else:
            self._current_block_movement_heading = None

    def rotate_current_block(self, effects):
        # Prevent SquareBlocks rotation
        if not isinstance(self.current_block, SquareBlock):
            self.current_block.rotate(self)
            self.update_grid()
            effects.play_piece_rotated_sound()

    def split_current_block(self, effects):
        curr = self.current_block
        # Superposed current block
        if curr.quantum_block is None:
            # If the block does not yet belong to a set of superposed blocks
            self.remove(curr)
            QuantumBlock(curr, self)
        else:
            if curr.quantum_block.size < 4 and curr.is_50:
                # Can split a 50% block into two 25% sub pieces
                self.remove(curr)
                curr.quantum_block.split_fifty_into_two(curr, self)

        self.current_block.draw_highlight()
        self.update_grid()
        effects.play_piece_split_sound()

    def exchange_superposed_blocks(self, effects):
        if self.current_block.quantum_block is not None:
            pos_cur_in_quantum_block = self.current_block.quantum_block.set_blocks.index(self.current_block)
            pos_next_in_quantum_block = 0 if pos_cur_in_quantum_block == 3 else pos_cur_in_quantum_block + 1
            next_block = None
            while next_block is None:
                next_block = self.current_block.quantum_block.set_blocks[pos_next_in_quantum_block]
                pos_next_in_quantum_block = 0 if pos_next_in_quantum_block == 3 else pos_next_in_quantum_block + 1
            pos_block_in_sprites = len(self.sprites()) - self.sprites().index(next_block)
            self._swap_block_with_top(pos_block_in_sprites)
            effects.play_superposition_exchange_sound()

    def _swap_block_with_top(self, pos_block):
        try:
            top_block = self.sprites()[-1]
            swap_block = self.sprites()[-pos_block]
            top_block.current = False
            swap_block.current = True
            self.remove(top_block)
            self.remove(swap_block)
            self.add(top_block)
            self.add(swap_block)

            # redraw image block for the one that was in top
            top_block.redraw()
            # Indicate the one that it is current (on top) and therefore manipulable
            self.current_block.draw_highlight()

        except IndexError:
            # both blocks have already reached the bottom, so the swap no longer makes sense
            pass

    def _verify_bottom_reach_superposed_blocks(self, curr):
        self._validate_overlapping(curr)
        curr.bottom_reach = True
        # Current block has reached the bottom, check if any of its superpositions
        # has not reaching the bottom yet
        at_least_one = False
        for block in curr.quantum_block.set_blocks:
            if block is not None and not block.bottom_reach:
                pos_block_in_sprites = len(self.sprites()) - self.sprites().index(block)
                self._swap_block_with_top(pos_block_in_sprites)
                at_least_one = True
                break
        if not at_least_one:
            curr.redraw()
            self.stop_moving_current_block()
            self._create_new_block()

    def _validate_overlapping(self, curr):
        while Block.collide(curr, self):
            curr.y -= 1


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
