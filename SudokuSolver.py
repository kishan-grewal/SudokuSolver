from ast import Num, Str, parse
from email import message
from hashlib import blake2b
from hmac import new
from math import sqrt
from operator import truediv
import click
from os import system
import random
from turtle import title
import pygame as pg
from pygame.locals import *
import copy
import csv

b = ' ' #blank
N = 9
wait_time = 5 # in ms

pg.init()
board_width = 450
board_height = 450
extra_height = 10 + 50 + 10
screen = pg.display.set_mode(size = (board_width, board_height+extra_height))
pg.display.set_caption("Sudoku Solver")
line_width = 3
font_obj = pg.font.Font('freesansbold.ttf', 32)
global solved
solved = False
global imm_positions

def generate_board(board):
    global solved
    solved = False
    new_board = []
    for i in range(N):
        row = []
        for j in range(N):
            row.append(b)
        new_board.append(row)

    new_board = [[3,b,6,5,b,8,4,b,b],
                 [5,2,b,b,b,b,b,b,b],
                 [b,8,7,b,b,b,b,3,1],
                 [b,b,3,b,1,b,b,8,b],
                 [9,b,b,8,6,3,b,b,5],
                 [b,5,b,b,9,b,6,b,b],
                 [1,3,b,b,b,b,2,5,b],
                 [b,b,b,b,b,b,b,7,4],
                 [b,b,5,2,b,6,3,b,b]]
    return new_board

def import_board(board):
    global solved
    solved = False
    new_board = []
    for i in range(N):
        row = []
        for j in range(N):
            row.append(b)
        new_board.append(row)
    
    print("Enter the file name (without .csv)")
    name = input()
    csv_board = open(name + ".csv", "r")
    reader = list(csv.reader(csv_board))
    for row in range(9):
        for col in range(9):
            char = reader[row][col]
            if char == 'b':
                new_board[row][col] = b
            else:
                new_board[row][col] = int(char)

    return new_board

def board_valid(board):
    for row in range(N):
        counts = [0] * 9
        for col in range(N):
            value = board[row][col]
            if value != b:
                counts[value-1] += 1
        for count in counts:
            if count > 1:
                return False

    for col in range(N):
        counts = [0] * 9
        for row in range(N):
            value = board[row][col]
            if value != b:
                counts[value-1] += 1
        for count in counts:
            if count > 1:
                return False

    boxN = int(sqrt(N)) # 9 -> 3, 16 -> 4 (makes smaller squares)
    for h in range(boxN):
        for v in range(boxN):
            counts = [0] * 9
            for i in range(boxN):
                for j in range(boxN):
                    value = board[h*3 + i][v*3 + j]
                    if value != b:
                        counts[value-1] += 1
            for count in counts:
                if count > 1:
                    return False

    return True

def valid_board_checker(board, row, col, num):
    # check in row and column ("T check" looks like a T usually)
    for x in range(N):
        if board[row][x] == num: # check throughout that row
            return False
        if board[x][col] == num: # check throughout that column
            return False
        
 
    # check in box
    boxN = int(sqrt(N)) # 9 -> 3, 16 -> 4 (makes smaller squares)
    rowStart = boxN * (row // boxN)
    colStart = boxN * (col // boxN)  
    for i in range(boxN):
        for j in range(boxN):
            if board[rowStart + i][colStart + j] == num:
                return False
    
    return True

def nonvisual_recursive_solver(board, row, col):
    # row 9 just moved onto "10th column"
    # therefore process completed successfully
    if (row == N-1 and col == N):
        return True
    # row done so move onto next row in same recursion, start from first column
    if col == N:
        row += 1
        col = 0
    
    if board[row][col] != b:
        return nonvisual_recursive_solver(board, row, col+1)
    
    # MAIN CODE
    digits = [1,2,3,4,5,6,7,8,9]
    random_digits = [random.sample(digits, len(digits)) for _ in range(10)]
    for num in random_digits: # from 1 to 9
        # if putting this number in works
        if valid_board_checker(board, row, col, num):
            # put the number in
            board[row][col] = num

            # KEEP GOING USING SAME ALGORITHM, IF IT WORKS (process completed successfully from above) RETURN TRUE
            if nonvisual_recursive_solver(board, row, col+1): # MAIN RECURSIVE PART
                return True
        # if didn't return true, then false so make that spot blank again
        # if the if statement never ran this does nothing (spot already blank)
        board[row][col] = b
    return False

def recursive_solver(board, row, col):
    global imm_positions
    # row 9 just moved onto "10th column"
    # therefore process completed successfully
    if (row == N-1 and col == N):
        return True
    # row done so move onto next row in same recursion, start from first column
    if col == N:
        row += 1
        col = 0
    
    if board[row][col] != b:
        return recursive_solver(board, row, col+1)
    
    # MAIN CODE
    for num in range(1, N+1): # from 1 to 9
        # if putting this number in works
        if valid_board_checker(board, row, col, num):
            # put the number in
            board[row][col] = num

            # DISPLAY STUFF
            pg.time.wait(wait_time)
            draw_grid(board, row, col)
            pg.display.update()


            # KEEP GOING USING SAME ALGORITHM, IF IT WORKS (process completed successfully from above) RETURN TRUE
            if recursive_solver(board, row, col+1): # MAIN RECURSIVE PART
                return True
        # if didn't return true, then false so make that spot blank again
        # if the if statement never ran this does nothing (spot already blank)
        board[row][col] = b
    return False

def draw_grid(board, row, col):
        global solved
        global imm_positions
        background = (255, 255, 200)
        grid_line = (50, 50, 50)
        different_color = (200, 255, 255)
        
        if solved:
            screen.fill(different_color)
        else:
            screen.fill(background)  
        # fill with different color up to current row and col
        for i in range(row):
            current_row = pg.Rect(0, 50*i, board_width, 50)
            pg.draw.rect(screen, different_color, current_row)
        last_row = pg.Rect(0, 50*row, 50*(1+col), 50)
        pg.draw.rect(screen, different_color, last_row)

        for row in range(9):
            for col in range(9):
                position = (row, col)
                color = (0, 0, 0)
                if position in imm_positions:
                    color = (150, 0, 0)
                text_surface_obj = font_obj.render(str(board[row][col]), True, color)
                text_rect_obj = text_surface_obj.get_rect()
                text_rect_obj.center = (25 + 50*col, 25 + 50*row)
                screen.blit(text_surface_obj, text_rect_obj)

        for t in range(0, 10):
            pg.draw.line(screen, grid_line, (0, 50*t), (board_width, 50*t), line_width) # x from left to right, variable y therefore horizontal lines
            pg.draw.line(screen, grid_line, (50*t, 0), (50*t, board_height), line_width) # y from bottom to top, variable x therefore vertical lines

def main():
    print("\nTo solve the board manually, hover over each space and press\n"
    +"the number you wish to enter on your keyboard - enter backspace to remove the number")
    print("To reset the board, press space at any time")

    global solved 
    board = []
    board = generate_board(board)
    global imm_positions
    imm_positions = []
    for i in range(9):
        for j in range(9):
            if board[i][j] != b:
                position = (i, j)
                imm_positions.append(position)

    # solve board button
    sol_button = pg.Rect(5, 460, 220, 50)
    sol_surface = font_obj.render("Solve board", True, (0, 0, 0))
    sol_rect = sol_surface.get_rect()
    sol_rect.center = (5 + 110, 460 + 25) 
    # time "button"
    time_button = pg.Rect(225, 460, 220, 50)
    time_surface = font_obj.render("Time:", True, (0, 0, 0))
    time_rect = time_surface.get_rect()
    time_rect.center = (225 + 110, 460 + 25) 
   
    congrats_given = False
    running = True
    while running:
        time = str((pg.time.get_ticks() / 1000)//1)
        time_surface = font_obj.render("Time:"+time, True, (0, 0, 0))

        solved_board = copy.deepcopy(board)
        if board_valid(board):
            nonvisual_recursive_solver(solved_board, 0, 0)
        else:
            solved_board = -1

        draw_grid(board, 0, 0)
        pg.draw.rect(screen, (0,0,0), sol_button, line_width)
        screen.blit(sol_surface, sol_rect)
        pg.draw.rect(screen, (0,0,0), time_button, line_width)
        screen.blit(time_surface, time_rect)
        # event handlers below
        if not congrats_given:
            if board == solved_board:
                solved = True
                congrats_given = True
                print("Congrats, you have solved the board")
        pg.event.pump()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.K_0:
                board = generate_board(board)
                solved = False
            if event.type == pg.KEYDOWN:
                keys = pg.key.get_pressed()
                if keys[K_SPACE] == 1:
                    board = generate_board(board)
                    solved = False
                if pg.mouse.get_pos()[1] < 450:
                    key = -1
                    if keys[K_BACKSPACE] == 1:
                        key = b
                    if keys[K_1] == 1:
                        key = 1
                    if keys[K_2] == 1:
                        key = 2
                    if keys[K_3] == 1:
                        key = 3
                    if keys[K_4] == 1:
                        key = 4
                    if keys[K_5] == 1:
                        key = 5
                    if keys[K_6] == 1:
                        key = 6
                    if keys[K_7] == 1:
                        key = 7
                    if keys[K_8] == 1:
                        key = 8
                    if keys[K_9] == 1:
                        key = 9
                    i = pg.mouse.get_pos()[1] // 50
                    j = pg.mouse.get_pos()[0] // 50
                    if key != -1:
                        position = (i, j)
                        if position in imm_positions:
                            print("Immutable position selected")
                        else:
                            board[i][j] = key                      
            if event.type == pg.MOUSEBUTTONDOWN:
                # solve board button
                if sol_button.collidepoint(event.pos):   
                    if board_valid(board):
                        if solved:
                            print("Board is already solved/is unsolvable")
                        else:
                            recursive_solver(board, 0, 0)                           
                            solved = True
                    else:
                        print("Board is invalid")
        
        pg.display.update()
    pg.quit()


main()
