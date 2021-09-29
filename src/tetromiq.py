#from pathlib import Path
from board import *
from table import *


def draw_centered_surface(screen, surface, y):
    screen.blit(surface, ((WINDOW_WIDTH + GRID_WIDTH - surface.get_width()) / 2, y))


def game():
    pygame.init()
    pygame.display.set_caption("TetromiQ")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    run = True
    paused = False
    game_over = False
    fall_speed = INITIAL_FALL_SPEED
    level = 1
    # Create background.
    background = pygame.Surface(screen.get_size())
    bgcolor = (0, 0, 0)
    background.fill(bgcolor)
    # Draw the grid on top of the background.
    draw_grid(background)
    # This makes blitting faster.
    background = background.convert()
    # Username Input Box
    username = ''
    input_box = pygame.Rect(70, 230, 140, 32)
    input_box_active = False
    color_inactive = (0, 0, 255)
    color_active = (0, 255, 0)
    input_box_color = color_inactive
    # High scores
    show_high_scores = False
    high_scores = []
    high_score_table = []
    read_high_score = open(Path("../resources/Scores.txt"), "r")
    
    font = pygame.font.SysFont(None, 30)

    try:
        font = pygame.font.Font(Path("../resources/Roboto-Regular.ttf"), 20)
    except OSError:
        # If the font file is not available, the default will be used.
        pass
    next_block_text = font.render(
        "Next:", True, (255, 255, 255), bgcolor)
    score_msg_text = font.render(
        "Score:", True, (255, 255, 255), bgcolor)
    lines_msg_text = font.render(
        "Lines:", True, (255, 255, 255), bgcolor)
    game_over_text = font.render(
        "Game Over", True, (255, 220, 0), bgcolor)

    # Event constants.
    MOVEMENT_KEYS = pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN
    EVENT_UPDATE_CURRENT_BLOCK = pygame.USEREVENT + 1
    EVENT_MOVE_CURRENT_BLOCK = pygame.USEREVENT + 2
    pygame.time.set_timer(EVENT_UPDATE_CURRENT_BLOCK, fall_speed)
    pygame.time.set_timer(EVENT_MOVE_CURRENT_BLOCK, 100)

    blocks = BlocksGroup()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            elif event.type == pygame.KEYUP:
                if not paused and not game_over:
                    if event.key in MOVEMENT_KEYS:
                        blocks.stop_moving_current_block()
                    elif event.key == pygame.K_UP:
                        blocks.rotate_current_block()
                if event.key == pygame.K_p:
                    paused = not paused

            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    input_box_active = not input_box_active
                else:
                    input_box_active = False
                # Change the current color of the input box.
                input_box_color = color_active if input_box_active else color_inactive

            if event.type == pygame.KEYDOWN and input_box_active:
                if event.key == pygame.K_RETURN:
                    # Save scores and prepare table
                    prepare_score_table(read_high_score, high_scores, high_score_table, blocks.score, username)
                    show_high_scores = True
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username) < 20:
                        username += event.unicode

            # Stop moving blocks if the game is over or paused.
            if game_over or paused:
                continue

            if event.type == pygame.KEYDOWN:
                if event.key in MOVEMENT_KEYS:
                    blocks.start_moving_current_block(event.key)

            try:
                if event.type == EVENT_UPDATE_CURRENT_BLOCK:
                    blocks.update_current_block()
                elif event.type == EVENT_MOVE_CURRENT_BLOCK:
                    blocks.move_current_block()
            except TopReached:
                game_over = True

        # Draw background and grid.
        screen.blit(background, (0, 0))
        # Blocks.
        blocks.draw(screen)
        # Game information.
        draw_centered_surface(screen, next_block_text, 20)
        height_blocks = 0
        for i in range(len(blocks.next_blocks)):
            draw_centered_surface(screen, blocks.next_blocks[i].small_image,
                                  40 + 20*(i+1) + height_blocks)
            height_blocks += blocks.next_blocks[i].small_image.get_height()
        # Separate the blocks coming from the counters.
        pygame.draw.line(background, (50, 50, 50), (GRID_WIDTH, 308), (WINDOW_WIDTH, 308))
        # Place a black rectangle to hide the pieces that exceed the separation line.
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(GRID_WIDTH + 1, 309, WINDOW_WIDTH, 339))
        # Counters.
        draw_centered_surface(screen, score_msg_text, 340)
        draw_centered_surface(screen, lines_msg_text, 420)
        score_text = font.render(str(blocks.score), True, (255, 255, 255), bgcolor)
        lines_num_text = font.render(str(blocks.lines), True, (255, 255, 255), bgcolor)
        draw_centered_surface(screen, score_text, 370)
        draw_centered_surface(screen, lines_num_text, 450)

        # Game Over, Enter Username, Display High Score Table
        if game_over and not show_high_scores:
            draw_centered_surface(screen, game_over_text, 400)
            # Draw the username input box.
            enter_username_text = font.render("Enter Username", True, (255, 220, 0), bgcolor)
            username_text = font.render(username, True, input_box_color)
            draw_username_input_box(screen, enter_username_text, username_text, input_box, input_box_color)
        elif game_over and show_high_scores:
            # Draw Highscore Table
            screen.fill(bgcolor)
            table_username_head = font.render("Username", True, (255, 220, 0), bgcolor)
            table_score_head = font.render("Score", True, (255, 220, 0), bgcolor)
            draw_table_head(screen, table_username_head, table_score_head)
            table_rank = 1
            high_scores = list(dict.fromkeys(high_scores))
            high_scores = sorted(high_scores, reverse=True)
            for score_idx, score in enumerate(high_scores):
                for place_idx, place_entry in enumerate(high_score_table):
                    if score == place_entry[0]:
                        place_entry_username = font.render(place_entry[1], True, (0, 0, 210), bgcolor)
                        place_entry_score = font.render(str(place_entry[0]), True, (0, 0, 210), bgcolor)
                        draw_table_entry(screen, place_entry_username, place_entry_score, table_rank)
                        table_rank = table_rank + 1

        # Update.
        pygame.display.flip()

        # Increase falling speed
        if blocks.score >= SCORE_CHANGE_LEVEL * level:
            level += 1
            fall_speed = fall_speed - (FALL_SPEED_DECREMENT if fall_speed > MIN_FALL_SPEED else 0)
            pygame.time.set_timer(EVENT_UPDATE_CURRENT_BLOCK, 0)
            pygame.time.set_timer(EVENT_UPDATE_CURRENT_BLOCK, fall_speed)

    pygame.quit()


if __name__ == "__main__":
    game()
