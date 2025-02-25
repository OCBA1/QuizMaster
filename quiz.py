#!/usr/bin/env python3
import pygame
import pygame_gui
from tkinter import *
import sys
import json
import random
import time
import math
import colorsys
import re
import os
import subprocess
from glob import glob
import datetime

from pygame.locals import *
from tkinter import *
from tkinter import messagebox, colorchooser

from modules.persistence import *
from modules.checker import *
from modules.searchQuiz import search_str_in_file
from modules.pygameTextInput.pygame_textinput import TextInputVisualizer
import modules.PySimpleGUI as sg

pygame.init()
pygame.font.init()
manager = pygame_gui.UIManager((1250, 700))


textinput = TextInputVisualizer()
pygame.key.set_repeat(200, 25)

print(asciiartstart)

try:
  with open(".Preferences.json", "r") as file:
      try:
          prefDict = json.load(file)
          v = prefDict["Volume"]
          if isItHalloweenTimeNow():
              colour_background = (250,100,0)
              buttons_colour =  (255,110,10)
              music = "music/music_halloween1.ogg"
          elif isItValentinesTimeNow():
              music = "music/music_valentines1.ogg"
              colour_background = (255,0,0)
              buttons_colour =  (255,10,10)
          elif isItStPatricksTimeNow():
              music = "music/music_stpatrick1.ogg"
              colour_background = (0,150,0)
              buttons_colour =  (10,175,10) 
          elif isItChristmasTimeNow():
              music = "music/music_christmas1.ogg"
              colour_background = prefDict["colour"]
              buttons_colour = prefDict["buttoncolour"]         
          else:
              music = prefDict["Music"]
              colour_background = prefDict["colour"]
              buttons_colour = prefDict["buttoncolour"] 
              celebration = False
          colour = colour_background
          button_colour = buttons_colour
      except json.JSONDecodeError:
          v = 0.5
          music_list = ['music/music1.ogg', 'music/music2.ogg', 'music/music3.ogg', 'music/music4.ogg', 'music/music5.ogg', 'music/music6.ogg']
          music = (random.choice(music_list))
          col_bg = random.uniform(0,1)
          colour_background = tuple(map(lambda x: 255.0*x, colorsys.hsv_to_rgb(col_bg,1,0.975))) 
          buttons_colour = tuple(map(lambda x: 255.0*x, colorsys.hsv_to_rgb(col_bg,1,1))) 
          colour = colour_background
          button_colour = buttons_colour
except FileNotFoundError:
    v = 0.5
    music_list = ['music/music1.ogg', 'music/music2.ogg', 'music/music3.ogg', 'music/music4.ogg', 'music/music5.ogg', 'music/music6.ogg']
    music = (random.choice(music_list))
    col_bg = random.uniform(0,1)
    colour_background = tuple(map(lambda x: 255.0*x, colorsys.hsv_to_rgb(col_bg,1,0.975))) 
    buttons_colour = tuple(map(lambda x: 255.0*x, colorsys.hsv_to_rgb(col_bg,1,1))) 
    colour = colour_background
    button_colour = buttons_colour
    
root = Tk()
width = root.winfo_screenwidth() 
height = root.winfo_screenheight()
     

SCREEN_WIDTH = width - 250
SCREEN_HEIGHT = height -150
BACKGROUND_COLOUR = colour
BUTTON_COLOUR = button_colour
BLACK = (0, 0, 0)
FONT_SIZE = 40
QUESTION_OFFSET = 50
ANSWER_OFFSET = 200
OPTION_HEIGHT = 50

class Button:
    def __init__(self, text, position, width=0, height=0):
        self.text = text
        self.position = position
        self.font = pygame.font.Font(None, FONT_SIZE)
        text_width, text_height = self.font.size(text)
        self.width = max(width, text_width + 20)
        self.height = max(height, text_height + 20) 
        self.rect = pygame.Rect(position[0], position[1], width, height)

    def draw(self, screen, color):
        pygame.draw.rect(screen, color, self.rect)
        font = pygame.font.Font(None, FONT_SIZE)
        label = font.render(self.text, True, BLACK)
        text_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
        
class Scrollbar:
    def __init__(self, position, height, total_items, items_per_page):
        self.position = position
        self.height = height
        self.total_items = total_items
        self.items_per_page = items_per_page
        self.rect = pygame.Rect(position[0], position[1], 20, height)
        self.handle_rect = pygame.Rect(position[0], position[1], 20, height * items_per_page // total_items)
        self.dragging = False
        self.offset_y = 0

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        pygame.draw.rect(screen, (100, 100, 100), self.handle_rect)

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
                self.offset_y = event.pos[1] - self.handle_rect.y
        elif event.type == MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == MOUSEMOTION:
            if self.dragging:
                new_y = event.pos[1] - self.offset_y
                new_y = max(self.rect.y, min(new_y, self.rect.y + self.rect.height - self.handle_rect.height))
                self.handle_rect.y = new_y

    def get_offset(self):
        return (self.handle_rect.y - self.rect.y) * self.total_items // self.height

def load_quiz(filename):
    with open(filename, 'r') as file:
        quizDicts = json.load(file)
        questionList = []
        for q in quizDicts["listOfQuestions"]:
            qq = QuizQuestion(**q)
            questionList.append(qq)
        titleofquiz = quizDicts["title"]
    return questionList, titleofquiz

def display_message(message, y_position, font_size, colour="BLACK"):
    font = pygame.font.Font(None, font_size)
    words = message.split()
    
    if len(message) > 60:
        text_lines = []
        line = ""
        
        for word in words:
            if font.size(line + word)[0] <= SCREEN_WIDTH:
                line += word + " "
            else:
                text_lines.append(line)
                line = word + " "
        
        if line:
            text_lines.append(line)

        for line in text_lines:
            text = font.render(line, True, colour)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2 , y_position))
            screen.blit(text, text_rect)
            y_position += text.get_height()
    else:
        text = font.render(message, True, colour)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_position))
        screen.blit(text, text_rect)
        
        y_position += text.get_height()

    return y_position


def draw_color_wheel(center, radius):
    for angle in range(360):
        for r in range(radius):
            x = center[0] + int(r * math.cos(math.radians(angle)))
            y = center[1] + int(r * math.sin(math.radians(angle)))
            color = colorsys.hsv_to_rgb(angle / 360, r / radius, 1)
            color = tuple(int(c * 255) for c in color)
            screen.set_at((x, y), color)

def get_color_from_wheel(pos, center, radius):
    dx = pos[0] - center[0]
    dy = pos[1] - center[1]
    distance = math.sqrt(dx * dx + dy * dy)
    if distance <= radius:
        angle = (math.degrees(math.atan2(dy, dx)) + 360) % 360
        saturation = distance / radius
        color = colorsys.hsv_to_rgb(angle / 360, saturation, 1)
        return tuple(int(c * 255) for c in color)
    return None
    
def end():
    print(asciiartend)
    pygame.quit()
    sys.exit()

def classic(questionList, titleofquiz, BACKGROUND_COLOUR, BUTTON_COLOUR):
    incorrect_questions = []
    running = True
    questionIndex = 0
    correctAnswers = 0
    totalQuestions = len(questionList)
    good_praise_list = [f"Well Done! You know a lot about {titleofquiz}!",f"You are an expert on {titleofquiz}!", f" You have mastered {titleofquiz}!",f"You are amazing at {titleofquiz}!",f"You truly excel in {titleofquiz}!", f"Congratulations! You're a whiz on {titleofquiz}!",f"Bravo! You've nailed {titleofquiz}!"]
    good_praise = (random.choice(good_praise_list))
    medium_praise_list = ["Good enough...",f"You have a fair amount of knowledge on {titleofquiz}!", f"Not far of mastering {titleofquiz}", f"Just abit more practice on {titleofquiz}!",f"You’re making steady progress in {titleofquiz}.", f"You're on the right track with {titleofquiz}!",f"You've got a solid grasp of {titleofquiz}.",f"A commendable effort in {titleofquiz}!",f"You've got the basics of {titleofquiz} down!",f"Keep it up! You're building a good foundation in {titleofquiz}!"
]
    medium_praise = (random.choice(medium_praise_list))
    bad_praise_list = [f"Your forte is definitely not {titleofquiz}",f"You are terrible at {titleofquiz}!", f"You have alot to learn about {titleofquiz}!", f"You might want to consider revising another topic!", f"Sorry to say, but you're pretty terrible at {titleofquiz}", f"You really struggle with {titleofquiz}!", f"You have a long way to go in mastering {titleofquiz}!", f"Not to be too hard, but it seems you're not great at {titleofquiz}!", f"Time to go back to the drawing board on {titleofquiz}!", f"You might want to consider taking another look at {titleofquiz}!", f"It's clear you're not a {titleofquiz} expert!", f"Unfortunately, you're not very good at {titleofquiz}!", f"You need to brush up on your {titleofquiz} skills!", f"Your {titleofquiz} knowledge is still in its infancy!"]
    bad_praise = (random.choice(bad_praise_list))
    for i in range(3,0,-1):
        screen.fill(BACKGROUND_COLOUR)
        display_message(titleofquiz, QUESTION_OFFSET,70)
        display_message((f"{i}!"), QUESTION_OFFSET+200,150)
        pygame.display.update()
        pygame.time.delay(1000)
    screen.fill(BACKGROUND_COLOUR)        
    display_message(("Go!"), QUESTION_OFFSET+200,150)
    pygame.display.update()
    pygame.time.delay(1000)        

    
    while running and questionIndex < totalQuestions:
        currentQuestion = questionList[questionIndex]

        user_answer = None
        time_remaining = currentQuestion.timeout
        timeColour = (0,0,0)
        
        answerOptions = [currentQuestion.correctAnswer] + currentQuestion.wrongAnswers
        random.shuffle(answerOptions)

        buttons = []
        for idx, answer in enumerate(answerOptions):
            button = Button(f"{idx + 1}. {answer}", (SCREEN_WIDTH // 2 - 150, ANSWER_OFFSET + idx * OPTION_HEIGHT), 300, 40)
            buttons.append(button)

        while running and time_remaining > 0 and user_answer is None:
            screen.fill(BACKGROUND_COLOUR)
            display_message(f"Question {questionIndex + 1} out of {totalQuestions} : {currentQuestion.question}", QUESTION_OFFSET, 50)

            for button in buttons:
                button.draw(screen, BUTTON_COLOUR if user_answer is None else BACKGROUND_COLOUR)
            button_end = Button("End Quiz", (SCREEN_WIDTH // 2+350 , SCREEN_HEIGHT // 2+200), 250, 40)  
            button_go_back = Button("Main Menu", (SCREEN_WIDTH // 2+350 , SCREEN_HEIGHT // 2+250), 250, 40)
            button_leave = Button("Quit", (SCREEN_WIDTH // 2+350 , SCREEN_HEIGHT // 2+300), 250, 40)
            display_message(f"Time remaining: {time_remaining}", SCREEN_HEIGHT - QUESTION_OFFSET, 40, timeColour)
            button_end.draw(screen, BUTTON_COLOUR)
            button_go_back.draw(screen, BUTTON_COLOUR)
            button_leave.draw(screen, BUTTON_COLOUR)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    end()
                if event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos() 
                    if button_end.is_clicked(pos):
                       time_remaining = 0
                       totalQuestions = questionIndex       
                    if button_go_back.is_clicked(pos):
                       main(music,BACKGROUND_COLOUR,BUTTON_COLOUR, v)
                    if button_leave.is_clicked(pos):
                       end()
                    pygame.time.wait(40)
                    for idx, button in enumerate(buttons):
                        if button.is_clicked(pos):
                            user_answer = idx
 
                if event.type == KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8,pygame.K_9]:
                        user_answer = event.key - pygame.K_1

            time_remaining -= 1
            if time_remaining <= 5:
                timeColour = (255,0,0)
            pygame.time.wait(1000)

        correct_answer_index = answerOptions.index(currentQuestion.correctAnswer)
        if user_answer is not None:
            if user_answer == correct_answer_index:
                correctAnswers += 1
            else:
                incorrect_questions.append(currentQuestion)

        questionIndex += 1

    while True:
        screen.fill(BACKGROUND_COLOUR)
        y_position = display_message(f"Quiz completed! You got {correctAnswers} out of {totalQuestions} questions correct.", SCREEN_HEIGHT // 2-200,40)
        try:
            if correctAnswers/totalQuestions > 0.8:
                display_message(good_praise, y_position,40)
            if correctAnswers/totalQuestions > 0.4 and correctAnswers/totalQuestions < 0.8 or correctAnswers/totalQuestions == 0.8:
                display_message(medium_praise, y_position,40)
            if correctAnswers/totalQuestions < 0.4 or correctAnswers/totalQuestions==0.4:
                display_message(bad_praise, y_position,40)
        except ZeroDivisionError:
                display_message("No questions attempted!", y_position,40)
    
        button_go_back = Button("Main Menu", (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50), 250, 40)
        button_replay = Button("Replay", (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 100), 250, 40)
        button_quit = Button("Quit", (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 150), 250, 40)
        if incorrect_questions:
          button_show_incorrect = Button("Show Incorrect Answers", (SCREEN_WIDTH // 2 - 150 , SCREEN_HEIGHT // 2), 250, 40)
          button_show_incorrect.draw(screen, BUTTON_COLOUR)
        button_go_back.draw(screen, BUTTON_COLOUR)
        button_replay.draw(screen, BUTTON_COLOUR)
        button_quit.draw(screen, BUTTON_COLOUR)        
        
        pygame.display.update()

        for event in pygame.event.get(): 
            if event.type == QUIT:
               end()
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if incorrect_questions and questionIndex > 0:
                    if button_show_incorrect.is_clicked(pos):
                      messages = []
                      for question in incorrect_questions:
                          messages.append(f"""{question.question}
Correct Answer: {question.correctAnswer}""")

                      final_message = '\n \n'.join(messages)

                      layout = [
                          [sg.Multiline(final_message, size=(100, 20), disabled=True)],
                        ]

                      window = sg.Window('Wrong Questions', layout)

                      while True:
                          event, values = window.read()
                          if event == sg.WINDOW_CLOSED:
                              window.close()
                              break
                          
                if button_go_back.is_clicked(pos):
                     return True
                if button_replay.is_clicked(pos):
                    classic(questionList, titleofquiz, BACKGROUND_COLOUR, BUTTON_COLOUR)
                if button_quit.is_clicked(pos):
                     end()
                    
def classicV2(questionList, titleofquiz, BACKGROUND_COLOUR, BUTTON_COLOUR):
    incorrect_questions = []
    running = True
    questionIndex = 0
    correctAnswers = 0
    totalQuestions = len(questionList)
    
    total_time = sum(q.timeout-3 for q in questionList)+10
    start_time = time.time()

    good_praise_list = [f"Well Done! You know a lot about {titleofquiz}!", f"You are an expert on {titleofquiz}!", f" You have mastered {titleofquiz}!", f"You are amazing at {titleofquiz}!"]
    good_praise = (random.choice(good_praise_list))
    medium_praise_list = ["Good enough...", f"You have a fair amount of knowledge on {titleofquiz}!", f"Not far off mastering {titleofquiz}", f"Just a bit more practice on {titleofquiz}!", f"You’re making good progress on {titleofquiz}!"]
    medium_praise = (random.choice(medium_praise_list))
    bad_praise_list = [f"Your forte is definitely not {titleofquiz}", f"You are terrible at {titleofquiz}!", f"You have a lot to learn about {titleofquiz}!", f"You might want to consider revising another topic!", f"{titleofquiz} is not your strong suit!"]
    bad_praise = (random.choice(bad_praise_list))
    
    for i in range(3, 0, -1):
        screen.fill(BACKGROUND_COLOUR)
        display_message(titleofquiz, QUESTION_OFFSET, 70)
        display_message((f"{i}!"), QUESTION_OFFSET + 200, 150)
        pygame.display.update()
        pygame.time.delay(1000)
    screen.fill(BACKGROUND_COLOUR)
    display_message(("Go!"), QUESTION_OFFSET + 200, 150)
    pygame.display.update()
    pygame.time.delay(1000)

    while running and questionIndex < totalQuestions:
        currentQuestion = questionList[questionIndex]

        user_answer = None

        answerOptions = [currentQuestion.correctAnswer] + currentQuestion.wrongAnswers
        random.shuffle(answerOptions)

        buttons = []
        for idx, answer in enumerate(answerOptions):
            button = Button(f"{idx + 1}. {answer}", (SCREEN_WIDTH // 2 - 150, ANSWER_OFFSET + idx * OPTION_HEIGHT), 300, 40)
            buttons.append(button)

        while running and user_answer is None:
            elapsed_time = time.time() - start_time
            time_remaining = total_time - int(elapsed_time)
            
            if time_remaining < total_time/totalQuestions:
                timeColour = (255,0,0)
            else:
                timeColour = (0,0,0)    

            if time_remaining <= 0:
                running = False
                break

            screen.fill(BACKGROUND_COLOUR)
            display_message(f"Question {questionIndex + 1} out of {totalQuestions} : {currentQuestion.question}", QUESTION_OFFSET, 50)

            for button in buttons:
                button.draw(screen, BUTTON_COLOUR if user_answer is None else BACKGROUND_COLOUR)
            button_end = Button("End Quiz", (SCREEN_WIDTH // 2 + 350, SCREEN_HEIGHT // 2 + 200), 250, 40)
            button_go_back = Button("Main Menu", (SCREEN_WIDTH // 2 + 350, SCREEN_HEIGHT // 2 + 250), 250, 40)
            button_leave = Button("Quit", (SCREEN_WIDTH // 2 + 350, SCREEN_HEIGHT // 2 + 300), 250, 40)
            display_message(f"Time remaining: {time_remaining}", SCREEN_HEIGHT - QUESTION_OFFSET, 40, timeColour)
            button_end.draw(screen, BUTTON_COLOUR)
            button_go_back.draw(screen, BUTTON_COLOUR)
            button_leave.draw(screen, BUTTON_COLOUR)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    end()
                if event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if button_end.is_clicked(pos):
                        running = False
                        break
                    if button_go_back.is_clicked(pos):
                        main(music, BACKGROUND_COLOUR, BUTTON_COLOUR, v)
                    if button_leave.is_clicked(pos):
                        end()
                    pygame.time.wait(40)
                    for idx, button in enumerate(buttons):
                        if button.is_clicked(pos):
                            user_answer = idx

                if event.type == KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                        user_answer = event.key - pygame.K_1

        correct_answer_index = answerOptions.index(currentQuestion.correctAnswer)
        if user_answer is not None:
            if user_answer == correct_answer_index:
                correctAnswers += 1
            else:
                incorrect_questions.append(currentQuestion)

        questionIndex += 1

    while True:
        screen.fill(BACKGROUND_COLOUR)
        y_position = display_message(f"Quiz completed! You got {correctAnswers} out of {totalQuestions} questions correct.", SCREEN_HEIGHT // 2 - 200, 40)
        try:
            if correctAnswers / totalQuestions > 0.8:
                display_message(good_praise, y_position, 40)
            if correctAnswers / totalQuestions > 0.4 and correctAnswers / totalQuestions < 0.8 or correctAnswers / totalQuestions == 0.8:
                display_message(medium_praise, y_position, 40)
            if correctAnswers / totalQuestions < 0.4 or correctAnswers / totalQuestions == 0.4:
                display_message(bad_praise, y_position, 40)
        except ZeroDivisionError:
            display_message("No questions attempted!", y_position, 40)

        button_go_back = Button("Main Menu", (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50), 250, 40)
        button_replay = Button("Replay", (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 100), 250, 40)
        button_quit = Button("Quit", (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 150), 250, 40)
        if incorrect_questions:
            button_show_incorrect = Button("Show Incorrect Answers", (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2), 250, 40)
            button_show_incorrect.draw(screen, BUTTON_COLOUR)
        button_go_back.draw(screen, BUTTON_COLOUR)
        button_replay.draw(screen, BUTTON_COLOUR)
        button_quit.draw(screen, BUTTON_COLOUR)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                end()
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if incorrect_questions and questionIndex > 0:
                    if button_show_incorrect.is_clicked(pos):
                        messages = []
                        for question in incorrect_questions:
                            messages.append(f"""{question.question}
Correct Answer: {question.correctAnswer}""")

                        final_message = '\n \n'.join(messages)

                        layout = [
                            [sg.Multiline(final_message, size=(100, 20), disabled=True)],
                        ]

                        window = sg.Window('Wrong Questions', layout)

                        while True:
                            event, values = window.read()
                            if event == sg.WINDOW_CLOSED:
                                window.close()
                                break

                if button_go_back.is_clicked(pos):
                    return True
                if button_replay.is_clicked(pos):
                    classicV2(questionList, titleofquiz, BACKGROUND_COLOUR, BUTTON_COLOUR)
                if button_quit.is_clicked(pos):
                    end()

def speed(questionList, titleofquiz, BACKGROUND_COLOUR, BUTTON_COLOUR):
    originalQuestions = questionList[:]
    incorrect_questions = []
    running = True
    correctAnswers = 0
    totalQuestions = len(originalQuestions)
    lives = 3

    for i in range(3,0,-1):
        screen.fill(BACKGROUND_COLOUR)
        display_message(titleofquiz, QUESTION_OFFSET,70)
        display_message((f"{i}!"), QUESTION_OFFSET+200,150)
        pygame.display.update()
        pygame.time.delay(1000)
    screen.fill(BACKGROUND_COLOUR)        
    display_message(("Go!"), QUESTION_OFFSET+200,150)
    pygame.display.update()
    pygame.time.delay(1000) 
    start_time = time.time()

    while running:
        if not questionList:
            break

        currentQuestion = questionList.pop(0)
        user_answer = None

        answerOptions = [currentQuestion.correctAnswer] + currentQuestion.wrongAnswers
        random.shuffle(answerOptions)

        buttons = []
        for idx, answer in enumerate(answerOptions):
            button = Button(f"{idx + 1}. {answer}", (SCREEN_WIDTH // 2 - 150, ANSWER_OFFSET + idx * OPTION_HEIGHT), 300, 40)
            buttons.append(button)

        while running and user_answer is None:
            screen.fill(BACKGROUND_COLOUR)
            display_message(f"Question: {currentQuestion.question}", QUESTION_OFFSET, 50)

            for button in buttons:
                button.draw(screen, BUTTON_COLOUR if user_answer is None else BACKGROUND_COLOUR)
            button_go_back = Button("Main Menu", (SCREEN_WIDTH // 2 + 350, SCREEN_HEIGHT // 2 + 250), 250, 40)
            button_leave = Button("Quit", (SCREEN_WIDTH // 2 + 350, SCREEN_HEIGHT // 2 + 300), 250, 40)
            elapsed_time = time.time() - start_time
            display_message(f"Time: {int(elapsed_time)}", SCREEN_HEIGHT - QUESTION_OFFSET, 40)
            display_message(f"Lives: {lives}", SCREEN_HEIGHT - (QUESTION_OFFSET + 40), 40)
            button_go_back.draw(screen, BUTTON_COLOUR)
            button_leave.draw(screen, BUTTON_COLOUR)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    end()
                if event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for idx, button in enumerate(buttons):
                        if button_go_back.is_clicked(pos):
                           main(music,BACKGROUND_COLOUR,BUTTON_COLOUR, v)
                        if button_leave.is_clicked(pos):
                           end()
                        if button.is_clicked(pos):
                            user_answer = idx

                if event.type == KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                        user_answer = event.key - pygame.K_1

        correct_answer_index = answerOptions.index(currentQuestion.correctAnswer)
        if user_answer is not None:
            if user_answer == correct_answer_index:
                correctAnswers += 1
                continue
            else:
                questionList.append(currentQuestion)
                lives -= 1
                if lives < 0:
                    questionList = originalQuestions[:]
                    correctAnswers = 0
                    lives = 3

    end_time = time.time()
    total_time = int(end_time - start_time)

    while True:
        screen.fill(BACKGROUND_COLOUR)
        y_position = display_message(f"Speed Run completed! You answered all questions correctly in {total_time} seconds.", SCREEN_HEIGHT // 2 - 200, 40)
        button_go_back = Button("Main Menu", (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50), 250, 40)
        button_replay = Button("Replay", (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 100), 250, 40)
        button_quit = Button("Quit", (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 150), 250, 40)
        button_go_back.draw(screen, BUTTON_COLOUR)
        button_replay.draw(screen, BUTTON_COLOUR)
        button_quit.draw(screen, BUTTON_COLOUR)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                end()
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if button_go_back.is_clicked(pos):
                    return True
                if button_replay.is_clicked(pos):
                    speed(originalQuestions[:], titleofquiz, BACKGROUND_COLOUR, BUTTON_COLOUR)
                if button_quit.is_clicked(pos):
                    end()
                   
                    
def main(music, BACKGROUND_COLOUR, BUTTON_COLOUR, v):
    running = True
    while running:
        screen.fill(BACKGROUND_COLOUR)
        button_play = Button("Play a Quiz", (SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2), 250, 60)
        button_make = Button("Make a Quiz", (SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2), 250, 60)
        button_preferences = Button("Preferences", (SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 + 100), 250, 60)
        button_quit = Button("Quit", (SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2 + 100), 250, 60)
        display_message("Welcome to QuizMaster!", SCREEN_HEIGHT // 2 - 300, 75)
        button_make.draw(screen, BUTTON_COLOUR)
        button_play.draw(screen, BUTTON_COLOUR)
        button_preferences.draw(screen, BUTTON_COLOUR)
        button_quit.draw(screen, BUTTON_COLOUR)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                end()
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if button_quit.is_clicked(pos):
                    end()
                if button_make.is_clicked(pos):
                    subprocess.Popen(["python3", "quizcreator"])
                if button_preferences.is_clicked(pos):
                    celebration = False
                    numList = re.findall(r'\d+',music)     
                    i = int(numList[0]) if numList else 1 
                    
                    volume_slider = pygame_gui.elements.ui_horizontal_slider.UIHorizontalSlider(
                        relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 150, 150), (300, 50)),
                        start_value=v,
                        value_range=(0, 1),
                        manager=manager
                    )

                    scrollbar = Scrollbar((SCREEN_WIDTH - 40, 100), SCREEN_HEIGHT - 150, 6, 4)

                    while running:
                        time_delta = pygame.time.Clock().tick(60) / 1000.0
                        screen.fill(BACKGROUND_COLOUR)
                        display_message("Preferences", 50, 75)
                        display_message("_"*125, 60, 40)
                        display_message("Volume Control", 120, 40)
                        display_message("_"*100, 130, 25)
                        
                        display_message("Colours", 330, 40)
                        display_message("_"*100, 340, 25)
                        button_colour = Button("Change Colour", (SCREEN_WIDTH // 2 - 150, 360), 300, 50)

                        display_message("Music", 485, 40)
                        display_message("_"*100, 495, 25)
                        button_music = Button("Change Music", (SCREEN_WIDTH // 2 - 150, 510), 300, 50)
                        display_message("_"*125, 550, 40)
                        button_go_back = Button("Main Menu", (SCREEN_WIDTH // 2 - 150, 600), 300, 50)
                        button_cancel = Button("Cancel", (SCREEN_WIDTH // 2 - 150, 660), 300, 50)

                        button_colour.draw(screen, BUTTON_COLOUR)
                        button_music.draw(screen, BUTTON_COLOUR)
                        button_go_back.draw(screen, BUTTON_COLOUR)
                        button_cancel.draw(screen, BUTTON_COLOUR)

                        manager.draw_ui(screen)
                        pygame.display.update()

                        for event in pygame.event.get():
                            if event.type == QUIT:
                                end()
                            if event.type == MOUSEBUTTONDOWN:
                                pos = pygame.mouse.get_pos()
                                if button_colour.is_clicked(pos):
                                    col_bg = random.uniform(0, 1)
                                    colour_background = tuple(map(lambda x: 255.0 * x, colorsys.hsv_to_rgb(col_bg, 1, 0.975)))
                                    buttons_colour = tuple(map(lambda x: 255.0 * x, colorsys.hsv_to_rgb(col_bg, 1, 1)))
                                    colour = colour_background
                                    button_colour = buttons_colour
                                    BACKGROUND_COLOUR = colour
                                    BUTTON_COLOUR = button_colour
                                if button_music.is_clicked(pos):
                                    if i < 6:
                                        i += 1
                                    else:
                                        i = 1
                                    pygame.mixer.music.fadeout(1000)
                                    pygame.mixer.music.unload()
                                    music = f'music/music{i}.ogg'
                                    if isItChristmasTimeNow():
                                        celebration = True
                                        music = ["music/music_christmas1.ogg", "music/music_christmas2.ogg"][i % 2]
                                    if isItHalloweenTimeNow():
                                        celebration = True
                                        music = ["music/music_halloween1.ogg", "music/music_halloween2.ogg"][i % 2]
                                    if isItStPatricksTimeNow():
                                        celebration = True
                                        music = "music/music_stpatricks1.ogg"
                                    if isItValentinesTimeNow():
                                        celebration = True
                                        music = "music/music_valentines1.ogg"
                                    pygame.mixer.music.load(music)
                                    pygame.mixer.music.play(-1)
                                if button_go_back.is_clicked(pos):
                                    if celebration == False:
                                        save_preferences(v, music, BACKGROUND_COLOUR, BUTTON_COLOUR)
                                    main(music, BACKGROUND_COLOUR, BUTTON_COLOUR, v)
                                if button_cancel.is_clicked(pos):
                                    main(music, BACKGROUND_COLOUR, BUTTON_COLOUR, v)
                            manager.process_events(event)
                            if event.type == pygame.USEREVENT:
                                if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                                    if event.ui_element == volume_slider:
                                        v = event.value
                                        pygame.mixer.music.set_volume(v)
                        manager.update(time_delta)

                if button_play.is_clicked(pos):
                    searchTerm = ""
                    user_answer = None
                    while True:
                        screen.fill(BACKGROUND_COLOUR)
                        display_message("Enter Quiz Keyword:", 30, 50)
                        events = pygame.event.get()
                        for event in events:
                            if event.type == QUIT:
                                end()
                        textinput.update(events)

                        screen.blit(textinput.surface, (500, 100))

                        if [ev for ev in events if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN]:
                            searchTerm = textinput.value
                            break

                        pygame.display.update()
                        pygame.time.wait(30)

                    quizfiles = glob('./quizzes/**/*.json', recursive=True)

                    quizfileSearchResults = []
                    for file in quizfiles:
                        if search_str_in_file(file, searchTerm):
                            quizfileSearchResults.append(file)

                    if not quizfileSearchResults:
                        break

                    scrollbar = Scrollbar((SCREEN_WIDTH - 40, ANSWER_OFFSET), SCREEN_HEIGHT - ANSWER_OFFSET - 50, len(quizfileSearchResults), 10)
                    buttons = []
                    for idx, quizfile in enumerate(quizfileSearchResults):
                        try:
                            with open(quizfile, "r", errors="ignore") as file:
                                quiztitle = json.load(file)["title"]
                            button = Button(quiztitle, (SCREEN_WIDTH // 2 - 150, ANSWER_OFFSET + idx * OPTION_HEIGHT), 300, 40)
                            buttons.append(button)
                        except json.decoder.JSONDecodeError as ex:
                            print(f"Error in quizfile {quizfile}! {ex}")
                            continue

                    running = True
                    while running:
                        screen.fill(BACKGROUND_COLOUR)
                        for button in buttons:
                            button.draw(screen, BUTTON_COLOUR if user_answer is None else BACKGROUND_COLOUR)
                        if len(buttons) > 12:    
                           scrollbar.draw(screen)
                        pygame.display.update()
                        for event in pygame.event.get():
                            if event.type == QUIT:
                                end()
                            if event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP or event.type == MOUSEMOTION:
                                scrollbar.handle_event(event)
                            if event.type == MOUSEBUTTONDOWN:
                                pos = pygame.mouse.get_pos()
                                for idx, button in enumerate(buttons):
                                    if button.is_clicked(pos):
                                        user_answer = idx

                        offset = scrollbar.get_offset()
                        for idx, button in enumerate(buttons):
                            button.position = (SCREEN_WIDTH // 2 - 150, 100 + (idx - offset) * OPTION_HEIGHT)
                            button.rect.topleft = button.position

                        if user_answer is not None:
                            filename = quizfileSearchResults[user_answer]

                            try:
                                questionList, titleofquiz  = load_quiz(filename)
                            except Exception as ex:
                                messagebox.showinfo(title='Error', message=f'This is not a quiz file: {ex}!')
                                continue
                            print("Questions:", questionList)
                            
                            running = True
                            while running:
                                screen.fill(BACKGROUND_COLOUR)
                                display_message("Select Game Mode:", SCREEN_HEIGHT // 2 - 300, 75)
                                button_classic = Button("Classic", (SCREEN_WIDTH // 2 - 550, SCREEN_HEIGHT // 2 - 200), 300, 60)
                                button_classicV2 = Button("Classic v2.0", (SCREEN_WIDTH // 2 - 225, SCREEN_HEIGHT // 2 - 200), 300, 60)
                                button_speed = Button("Speed Run", (SCREEN_WIDTH // 2 + 110, SCREEN_HEIGHT // 2 - 200), 300, 60)           
                                button_classic.draw(screen, BUTTON_COLOUR)
                                button_classicV2.draw(screen, BUTTON_COLOUR)
                                button_speed.draw(screen, BUTTON_COLOUR)
                                pygame.display.update()

                                for event in pygame.event.get():
                                    if event.type == QUIT:
                                        end()
                                    if event.type == MOUSEBUTTONDOWN:
                                        pos = pygame.mouse.get_pos()
                                        event_time = pygame.time.get_ticks()
                                        if button_classic.is_clicked(pos):
                                            if classic(questionList, titleofquiz, BACKGROUND_COLOUR, BUTTON_COLOUR):
                                                main(music, BACKGROUND_COLOUR, BUTTON_COLOUR, v)
                                        if button_classicV2.is_clicked(pos):
                                            if classicV2(questionList, titleofquiz, BACKGROUND_COLOUR, BUTTON_COLOUR):
                                                main(music, BACKGROUND_COLOUR, BUTTON_COLOUR, v)
                                                
                                        if button_speed.is_clicked(pos):
                                            if speed(questionList, titleofquiz, BACKGROUND_COLOUR, BUTTON_COLOUR):
                                                main(music, BACKGROUND_COLOUR, BUTTON_COLOUR, v)
                                            
if __name__ == '__main__':
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('QuizMaster')
    icon = pygame.image.load('images/logo1.png')
    pygame.mixer.init()
    pygame.mixer.music.load(music)
    pygame.mixer.music.play(-1)
    pygame.display.set_icon(icon)
    main(music, BACKGROUND_COLOUR, BUTTON_COLOUR, v)
