from pathlib import Path
import pygame
from constants import *

def draw_username_input_box(screen, enter_username_text, username_text, input_box, input_box_color):
    screen.blit(enter_username_text, (int(GRID_WIDTH/5), int(GRID_HEIGHT/4)))
    # Resize the box if the text is too long.
    width = max(150, username_text.get_width() + 10)
    input_box.w = width
    # Blit the text.
    screen.blit(username_text, (input_box.x + 5, input_box.y + 5))
    # Blit the input_box rect.
    pygame.draw.rect(screen, input_box_color, input_box, 2)


def draw_table_head(screen, table_username_head, table_score_head):
    screen.blit(table_username_head, (int(GRID_WIDTH / 6), int(GRID_HEIGHT / 6)))
    screen.blit(table_score_head, (int(GRID_WIDTH / 1.1), int(GRID_HEIGHT / 6)))


def draw_table_entry(screen, place_entry_username, place_entry_score, place_idx):
    screen.blit(place_entry_username, (int(GRID_WIDTH / 6), int((GRID_HEIGHT / 6)+place_idx*TILE_SIZE)))
    screen.blit(place_entry_score, (int(GRID_WIDTH / 1.1), int((GRID_HEIGHT / 6)+place_idx*TILE_SIZE)))


def prepare_score_table(read_high_score, high_scores, high_score_table, blocks_score, username):
    for score_entry in read_high_score:
        if len(score_entry) > 2:
            edited_entry = score_entry.strip("\n")
            edited_entry = edited_entry.split("=")
            print("ee", edited_entry)
            edited_entry[0] = int(edited_entry[0])
            high_scores.append(edited_entry[0])
            high_score_table.append(edited_entry)
            print("hst", high_score_table)
    for score_idx, score in enumerate(high_scores):
        print(score_idx, "imin", score)
        if blocks_score > score and len(high_scores) == 15:
            high_score_table.pop(score_idx)
            high_scores.pop(score_idx)
            high_score_table.append([blocks_score, username])
            high_scores.append(blocks_score)
            break
    if len(high_score_table) < 15:
        high_score_table.append([blocks_score, username])
        high_scores.append(blocks_score)
    write_high_score = open(Path("../resources/Scores.txt"), "w")
    line_content = ''
    for place_entry in high_score_table:
        line_content += str(place_entry[0]) + "=" + place_entry[1] + '\n'
    write_high_score.write(line_content)