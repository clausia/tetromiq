from src.blocks import *


class QuantumBlock:
    """
    It stores a superposed block, and keeps the record of the blocks that were generated from
    the original (which was at 100%), it can save up to 4 sub-blocks, the possible configurations are:
       [ block at 50% , block at 50%, None,         None ]
       [ block at 50% , block at 25%, block at 25%, None ]
       [ block at 25% , block at 25%, block at 25%, block at 25% ]
    """

    types_blocks = {
        'SquareBlock': SquareBlock,
        'TBlock': TBlock,
        'LineBlock': LineBlock,
        'LBlock': LBlock,
        'LIBlock': LIBlock,
        'ZBlock': ZBlock,
        'ZIBlock': ZIBlock
    }

    def __init__(self, original_block, group):
        # When a set of superposed blocks is created for the first time, we will always be in the
        # case of having two parts, with 50%/50%

        block_left = self._create_superposed_block(self, original_block, group)          # tile left
        block_right = self._create_superposed_block(self, original_block, group, False)  # tile right

        block_left.is_50 = True
        block_right.is_50 = True

        block_right.current = True

        self._fit_inside_board(block_left, block_right, group)

        # The blocks are added in the order of creation, that is, in the sprite list,
        # the last block created is up to the "top"
        self.set_blocks = [block_left, None, None, block_right]

    @staticmethod
    def _create_superposed_block(quantum_block, original_block, group, left=True, color='color_50'):
        block = QuantumBlock.types_blocks[type(original_block).__name__]()
        block.color = getattr(block, color)
        block.struct = original_block.struct
        block.current = False
        block.y = original_block.y
        width_block = len(original_block.struct[0])
        block.x = original_block.x + int(width_block / 2) + (-width_block if left else 1)
        block.quantum_block = quantum_block
        block.bottom_reach = False
        block.redraw()
        group.add(block)

        return block

    @staticmethod
    def _fit_inside_board(block_left, block_right, group):
        # Check that the positions doesn't exceed the limits or collide with other blocks
        # and adjust it if necessary
        while block_right.rect.right > GRID_WIDTH:
            block_left.x -= 1
            block_right.x -= 1
        while block_left.rect.left < 0:
            block_left.x += 1
            block_right.x += 1
        while block_left.rect.bottom > GRID_HEIGHT:
            block_left.y -= 1
        while block_right.rect.bottom > GRID_HEIGHT:
            block_right.y -= 1
        while True:
            if not Block.collide(block_left, group):
                break
            block_left.y -= 1
        while True:
            if not Block.collide(block_right, group):
                break
            block_right.y -= 1

    def split_fifty_into_two(self, original_block, group):
        block_left = self._create_superposed_block(self, original_block, group, color='color_25')          # tile left
        block_right = self._create_superposed_block(self, original_block, group, False, color='color_25')  # tile right

        block_left.is_50 = False
        block_right.is_50 = False

        self._fit_inside_board(block_left, block_right, group)

        pos_original_bock = self.set_blocks.index(original_block)
        # Block with 50% only can be in the positions '0' or '3'
        if pos_original_bock == 0:
            # Its sub-blocks must go in positions '0' and '2'
            self.set_blocks[0] = block_left
            self.set_blocks[2] = block_right
        else:
            # Its sub-blocks must go in positions '1' and '3'
            self.set_blocks[1] = block_left
            self.set_blocks[3] = block_right

    @property
    def size(self):
        return sum(1 for _ in filter(None.__ne__, self.set_blocks))
