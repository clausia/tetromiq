from pathlib import Path
from src.board import *
from src.table import *
from src.effects import *
import cv2


def draw_centered_surface(screen, surface, y):
    screen.blit(surface, ((WINDOW_WIDTH + GRID_WIDTH - surface.get_width()) / 2, y))


def game():
    pygame.init()
    pygame.display.set_caption("TetromiQ")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    game_icon = pygame.image.load(Path("./resources/tqicon.png")).convert()
    pygame.display.set_icon(game_icon)
    pygame.display.update()
    play_intro(screen)
    run = True
    paused = False
    game_over = False
    fall_speed = INITIAL_FALL_SPEED
    previous_level = 1
    # Create background.
    background = pygame.Surface(screen.get_size())
    bgcolor = (0, 0, 0)
    background.fill(bgcolor)
    # Draw the grid over the background
    draw_grid(background)
    # This makes blitting faster
    background = background.convert()
    
    font = pygame.font.SysFont("arial", 30)
    fontSymbols = pygame.font.SysFont("arial", 30)
    try:
        font = pygame.font.Font(Path("./resources/Roboto-Regular.ttf"), 20)
        fontSymbols = pygame.font.Font(Path("./resources/seguisym.ttf"), 20)
    except OSError:
        # If the font file is not available, the default will be used
        pass

    next_block_text = font.render("Next:", True, (255, 255, 255), bgcolor)
    score_msg_text = font.render("Score:", True, (255, 255, 255), bgcolor)
    lines_msg_text = font.render("Lines:", True, (255, 255, 255), bgcolor)
    level_msg_text = font.render("Level:", True, (255, 255, 255), bgcolor)
    game_over_text = font.render("Game Over", True, (255, 220, 0), bgcolor)

    # Event constants
    MOVEMENT_KEYS = pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN
    EVENT_UPDATE_CURRENT_BLOCK = pygame.USEREVENT + 1
    EVENT_MOVE_CURRENT_BLOCK = pygame.USEREVENT + 2
    pygame.time.set_timer(EVENT_UPDATE_CURRENT_BLOCK, fall_speed)
    pygame.time.set_timer(EVENT_MOVE_CURRENT_BLOCK, 100)

    effects = Effects()
    blocks = BlocksGroup()
    score_table = ScoreTable()

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
                        blocks.rotate_current_block(effects)
                    elif event.key == pygame.K_h:
                        blocks.split_current_block(effects)
                    elif event.key == pygame.K_TAB:
                        blocks.exchange_superposed_blocks(effects)
                    elif event.key == pygame.K_m:
                        effects.mute_unmute_music()
                    elif event.key == pygame.K_n:
                        effects.mute_unmute_sound()
                if event.key == pygame.K_p and not game_over:
                    paused = not paused
                    if paused:
                        pygame.mixer.pause()
                    else:
                        pygame.mixer.unpause()
                if game_over:
                    score_table.type_input_in_box(event, blocks.score)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                score_table.activate_input_box(event.pos)

            # Stop moving blocks if the game is over or paused
            if game_over or paused:
                continue

            if event.type == pygame.KEYDOWN:
                if event.key in MOVEMENT_KEYS:
                    blocks.start_moving_current_block(event.key)

            try:
                if event.type == EVENT_UPDATE_CURRENT_BLOCK:
                    blocks.update_current_block(effects)
                elif event.type == EVENT_MOVE_CURRENT_BLOCK:
                    blocks.move_current_block(effects)
            except TopReached:
                game_over = True

        # Draw background and grid
        screen.blit(background, (0, 0))
        # Draw the blocks
        blocks.draw(screen)
        # Draw game information
        draw_centered_surface(screen, next_block_text, 20)
        height_blocks = 0
        for i in range(len(blocks.next_blocks)):
            draw_centered_surface(screen, blocks.next_blocks[i].small_image, 40 + 20*(i+1) + height_blocks)
            height_blocks += blocks.next_blocks[i].small_image.get_height()
        # Separate the blocks coming from the counters by using a line
        pygame.draw.line(background, (50, 50, 50), (GRID_WIDTH, 308), (WINDOW_WIDTH, 308))
        # Place a black rectangle to hide the pieces that exceed the separation line
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(GRID_WIDTH + 1, 309, WINDOW_WIDTH, 339))
        # Counters
        draw_centered_surface(screen, score_msg_text, 340)
        draw_centered_surface(screen, lines_msg_text, 420)
        draw_centered_surface(screen, level_msg_text, 500)
        score_text = font.render(str(blocks.score), True, (255, 255, 255), bgcolor)
        lines_num_text = font.render(str(blocks.lines), True, (255, 255, 255), bgcolor)
        level_text = font.render(str(blocks.level), True, (255, 255, 255), bgcolor)
        draw_centered_surface(screen, score_text, 370)
        draw_centered_surface(screen, lines_num_text, 450)
        draw_centered_surface(screen, level_text, 530)
        if game_over:
            draw_centered_surface(screen, game_over_text, 570)
            # Draw input box or high score table
            score_table.draw_input_or_table(screen, font, bgcolor)
        
        # Bottom
        draw_bottom(screen, background, bgcolor, fontSymbols)

        fall_speed, previous_level = update_fall_speed(
            blocks, fall_speed, previous_level, EVENT_UPDATE_CURRENT_BLOCK)

        # Update
        pygame.display.flip()

    pygame.quit()


def play_intro(window):
    video = cv2.VideoCapture("./resources/intro.mp4")
    success, video_image = video.read()
    fps = video.get(cv2.CAP_PROP_FPS)

    #window = pygame.display.set_mode(video_image.shape[1::-1])
    clock = pygame.time.Clock()

    run = success
    while run:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        success, video_image = video.read()
        if success:
            video_surf = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
        else:
            run = False
        window.blit(video_surf, (-163, -240))
        pygame.display.flip()


def update_fall_speed(blocks, fall_speed, previous_level, EVENT_UPDATE_CURRENT_BLOCK):
    # change falling speed based on level
    if blocks.level > previous_level:
        previous_level = blocks.level
        if blocks.level % LEVELS_TO_SLOW_DOWN == 0:
            fall_speed = RESET_FALL_SPEED
            pygame.time.set_timer(EVENT_UPDATE_CURRENT_BLOCK, 0)
            pygame.time.set_timer(EVENT_UPDATE_CURRENT_BLOCK, fall_speed)
        else:
            fall_speed = fall_speed - (FALL_SPEED_DECREMENT if fall_speed > MIN_FALL_SPEED else 0)
            pygame.time.set_timer(EVENT_UPDATE_CURRENT_BLOCK, 0)
            pygame.time.set_timer(EVENT_UPDATE_CURRENT_BLOCK, fall_speed)

    return fall_speed, previous_level

def draw_bottom(screen, background, bgcolor, fontSymbols):
    pygame.draw.line(background, (50, 50, 50), (0, GRID_HEIGHT), (WINDOW_WIDTH, GRID_HEIGHT))
    
    # "ᐊ ᐁ ᐅ Move  ᐃ Rotate  [H] Hadamard  ⇆ Swap"
    text_movements = "\u25C0 \u25BC \u25B6 Move  \u25B2 Rotate  [H] Hadamard  \u21B9 Swap"
    bottom_msg_text1 = fontSymbols.render(text_movements, True, (255, 255, 255), bgcolor)
    screen.blit(bottom_msg_text1, ((WINDOW_WIDTH - bottom_msg_text1.get_width()) / 2, GRID_HEIGHT + 10))
    text_controls = "[P] Pause  [M] Music on/off  [N] Sound effects on/off"
    bottom_msg_text = fontSymbols.render(text_controls, True, (255, 255, 255), bgcolor)
    screen.blit(bottom_msg_text, ((WINDOW_WIDTH - bottom_msg_text.get_width()) / 2, GRID_HEIGHT + bottom_msg_text1.get_height() + 10))

