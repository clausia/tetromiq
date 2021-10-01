from blocks import *


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

        block_left = self._create_superposed_block(self, original_block)          # tile left
        block_right = self._create_superposed_block(self, original_block, False)  # tile right

        block_right.current = True

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

        # The blocks are added in the order of creation, that is, in the sprite list,
        # the last block created is up to the "top"
        self.set_blocks = [block_left, block_right, None, None]

    @staticmethod
    def _create_superposed_block(qb, original_block, left=True):
        block = QuantumBlock.types_blocks[type(original_block).__name__]()
        block.color = block.color_50
        block.struct = original_block.struct
        block.current = False
        block.y = original_block.y
        width_block = len(original_block.struct[0])
        block.x = original_block.x + int(width_block / 2) + (-width_block if left else 1)
        block.superposed = qb
        block.bottom_reach = False
        block.redraw()

        return block
