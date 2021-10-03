from pathlib import Path
import pygame
from src.constants import *


class ScoreTable:

    def __init__(self):

        # Username Input Box
        self.username = ''
        self.input_box = pygame.Rect(90, 230, 140, 32)
        self.box_start = self.input_box.x
        self.input_box_active = False
        self.color_inactive = (200, 191, 231)
        self.color_active = (0, 255, 0)
        self.input_box_color = self.color_inactive
        # High scores
        self.show_high_scores = False
        self.high_scores = []
        self.high_score_table = []
        self.read_high_score = open(Path("./resources/scores.txt"), "r")

    def prepare_score_table(self, blocks_score):
        for score_entry in self.read_high_score:
            if len(score_entry) > 2:
                edited_entry = score_entry.strip("\n")
                edited_entry = edited_entry.split("=")
                edited_entry[0] = int(edited_entry[0])
                self.high_scores.append(edited_entry[0])
                self.high_score_table.append(edited_entry)
        for score_idx, score in enumerate(self.high_scores):
            if blocks_score > score and len(self.high_scores) == 10:
                self.high_score_table.pop(score_idx)
                self.high_scores.pop(score_idx)
                self.high_score_table.append([blocks_score, self.username])
                self.high_scores.append(blocks_score)
                break
        if len(self.high_score_table) < 10:
            self.high_score_table.append([blocks_score, self.username])
            self.high_scores.append(blocks_score)
        write_high_score = open(Path("./resources/scores.txt"), "w")
        line_content = ''
        for place_entry in self.high_score_table:
            line_content += str(place_entry[0]) + "=" + place_entry[1] + '\n'
        write_high_score.write(line_content)
        self.show_high_scores = True

    def activate_input_box(self, position):
        # If the user clicked on the input_box rect.
        if self.input_box.collidepoint(position):
            self.input_box_active = not self.input_box_active
        else:
            self.input_box_active = False
        # Change the current color of the input box.
        self.input_box_color = self.color_active if self.input_box_active else self.color_inactive
        
    def type_input_in_box(self, event, blocks_score):
        if self.input_box_active:
            if event.key == pygame.K_RETURN:
                # Save scores and prepare table
                self.prepare_score_table(blocks_score)
                self.input_box_active = False
            elif event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            else:
                if len(self.username) < 15:
                    self.username += event.unicode
                    
    def draw_input_or_table(self, screen, font, bgcolor):
        # Enter Username, Display High Score Table
        if not self.show_high_scores:
            # Draw the username input box.
            enter_username_text = font.render("Player Nickname", True, (255, 128, 64), bgcolor)
            username_text = font.render(self.username, True, self.input_box_color)
            draw_username_input_box(screen, enter_username_text, username_text, self.input_box, self.input_box_color,
                                    self.box_start)
        elif self.show_high_scores:
            # Draw High score Table
            screen.fill(bgcolor)
            table_rank_head = font.render("Rank", True, (255, 128, 64), bgcolor)
            table_username_head = font.render("Player", True, (255, 128, 64), bgcolor)
            table_score_head = font.render("Score", True, (255, 128, 64), bgcolor)
            draw_table_head(screen, table_rank_head, table_username_head, table_score_head)
            table_rank = 1
            self.high_scores = list(dict.fromkeys(self.high_scores))
            self.high_scores = sorted(self.high_scores, reverse=True)
            for score_idx, score in enumerate(self.high_scores):
                for place_idx, place_entry in enumerate(self.high_score_table):
                    if score == place_entry[0]:
                        place_entry_rank = font.render(str(table_rank), True, (200, 130, 231), bgcolor)
                        place_entry_username = font.render(place_entry[1], True, (200, 130, 231), bgcolor)
                        place_entry_score = font.render(str(place_entry[0]), True, (200, 130, 231), bgcolor)
                        draw_table_entry(screen, place_entry_rank, place_entry_username, place_entry_score, table_rank)
                        table_rank = table_rank + 1


def draw_username_input_box(screen, enter_username_text, username_text, input_box, input_box_color, start):
    frame = pygame.Rect(0, 0, GRID_WIDTH, (GRID_HEIGHT + 10))
    screen.fill((0, 0, 0), frame)
    x = GRID_WIDTH/16.8
    y = GRID_HEIGHT/6.72
    x_box = GRID_WIDTH/1.12
    y_box = GRID_HEIGHT/2.8
    dif = x/4
    pygame.draw.rect(screen, (200, 191, 231), (x, y, x_box, y_box), 1)
    pygame.draw.rect(screen, (200, 191, 231), (x+dif, y+dif, (x_box - 2 * dif), (y_box - 2 * dif)), 1)
    screen.blit(enter_username_text, (int(GRID_WIDTH/3.7), int(GRID_HEIGHT/4)))
    # Resize the box if the text is too long.
    width = max(150, username_text.get_width() + 10)
    input_box.w = width
    if width > 150:
        input_box.x = start - (width - 150)/2
    else:
        input_box.x = start
    # print("width", input_box.w)
    # Blit the text.
    screen.blit(username_text, (input_box.x + 5, input_box.y + 5))
    # Blit the input_box rect.
    pygame.draw.rect(screen, input_box_color, input_box, 2)


def draw_table_head(screen, table_rank_head, table_username_head, table_score_head):
    screen.blit(table_rank_head, (int(GRID_WIDTH / 6.7), int((GRID_HEIGHT / 8) - 2.5)))
    screen.blit(table_username_head, (int(GRID_WIDTH / 2), int((GRID_HEIGHT / 8) - 2.5)))
    screen.blit(table_score_head, (int(GRID_WIDTH / 0.75), int((GRID_HEIGHT / 8) - 2.5)))


def draw_table_entry(screen, place_entry_rank, place_entry_username, place_entry_score, place_idx):
    screen.blit(place_entry_rank, (int(GRID_WIDTH / 5.5), int((GRID_HEIGHT / 7) + 1.5 * place_idx * TILE_SIZE)))
    screen.blit(place_entry_username, (int(GRID_WIDTH / 2), int((GRID_HEIGHT / 7) + 1.5 * place_idx * TILE_SIZE)))
    screen.blit(place_entry_score, (int(GRID_WIDTH / 0.73), int((GRID_HEIGHT / 7) + 1.5 * place_idx * TILE_SIZE)))
