import const
import pygame
import numpy as np
import pygame_ui
import game
import network
from pygame.locals import *

#----------------------------------------------------------------------------------------------------------------------------------
def init_objects(window):

    #initiate text buttons
    start = window.get_size()[1] * 41 / 108
    incriment = window.get_size()[1] * 7 / 54
    quit_button = pygame_ui.Single_Button(window, [window.get_size()[1] / 3.6, start + incriment * 4],
                                          window.get_size()[0]/5, window.get_size()[0] / 30, "QUIT", const.COL["black"], const.COL["white"])
    
    start_button = pygame_ui.Single_Button(window, [window.get_size()[1] / 3.6, start + incriment * 2],
                                          window.get_size()[0]/5, window.get_size()[0] / 30, "START", const.COL["black"], const.COL["white"])

    back_button = pygame_ui.Single_Button(window, [window.get_size()[0]/2, window.get_size()[1] - window.get_size()[0] / 16],
                                          window.get_size()[0]/5, window.get_size()[0] / 30, "BACK", const.COL["black"], const.COL["white"])
    
    settings_button = pygame_ui.Single_Button(window, [window.get_size()[1] / 3.6, start + incriment * 3],
                                          window.get_size()[0]/5, window.get_size()[0] / 30, "SETTINGS", const.COL["black"], const.COL["white"])

    apply_button = pygame_ui.Single_Button(window, [window.get_size()[1] / 3.6, start + incriment * 3],
                                          window.get_size()[0]/5, window.get_size()[0] / 30, "APPLY", const.COL["black"], const.COL["white"])


    #Initiate Arrows
    res_up   = pygame_ui.Up_Arrow(  window, [window.get_size()[0]/2 - window.get_size()[0]/5.5, window.get_size()[1]/3], window.get_size()[1]/54, const.COL["white"], const.COL["black"])
    res_down = pygame_ui.Down_Arrow(window, [window.get_size()[0]/2 - window.get_size()[0]/5.5, window.get_size()[1]/3], window.get_size()[1]/54, const.COL["white"], const.COL["black"])
    screen_up   = pygame_ui.Up_Arrow(  window, [window.get_size()[0]/2 - window.get_size()[0]/5.5, window.get_size()[1]/2], window.get_size()[1]/54, const.COL["white"], const.COL["black"])
    screen_down = pygame_ui.Down_Arrow(window, [window.get_size()[0]/2 - window.get_size()[0]/5.5, window.get_size()[1]/2], window.get_size()[1]/54, const.COL["white"], const.COL["black"])

    #Add buttons to dictionary
    buttons = {"quit" : quit_button,
               "back" : back_button,
               "settings" : settings_button,
               "res_up" : res_up,
               "res_down" : res_down,
               "screen_up" : screen_up,
               "screen_down" : screen_down,
               "start" : start_button,
               "apply" : apply_button,
               }          

    return buttons

#--------------------------------------------------------------------------------------------------------------
def settings(window, resolution, action, buttons, mouse_used):
    resolutions = [[1280,720],
                   [1920,1080],
                   [2560,1440]]

    for i in range(len(resolutions)):
        if resolutions[i][0] == resolution[0]:
            res = i
            break

    fullscreen = False

    
    image = pygame.image.load("Assets\{}.jpg".format("brain"))
    image = pygame.transform.scale(image, (resolution[1], resolution[1]))

    used_buttons = {"back" : buttons["back"],
                    "apply" : buttons["apply"],
                    "res_up" : buttons["res_up"],
                    "res_down" : buttons["res_down"],
                    "screen_up" : buttons["screen_up"],
                    "screen_down" : buttons["screen_down"]}

    start = resolution[1] / 2
    incriment = resolution[1] * 7 / 54
    used_buttons["apply"].set_pos([resolution[0] / 5, start + incriment * 2])
    used_buttons["back"].set_pos([resolution[0] / 5, start + incriment * 3])

    
    while action == "settings":
        #Reset mouse usage
        if not pygame.mouse.get_pressed()[0]:
            mouse_used = False

        #render user interface elements
        window.fill(const.COL["black"])
        pygame_ui.draw_text(window, 'Settings', [resolution[0]/5, resolution[1]/10.8], int(resolution[1] / 10.5), const.COL["white"], 'impact', 'c')


        pygame_ui.draw_text(window, '{}x{}'.format(resolutions[res][0], resolutions[res][1]), [resolution[0]/6, resolution[1]/3], int(resolution[1] / 15), const.COL["white"], 'calibri', 'c')
        if fullscreen:
            pygame_ui.draw_text(window, 'FULLSCREEN', [resolution[0]/6, resolution[1]/2], int(resolution[1] / 15), const.COL["white"], 'calibri', 'c')
        else:
            pygame_ui.draw_text(window, 'WINDOWED', [resolution[0]/6, resolution[1]/2], int(resolution[1] / 15), const.COL["white"], 'calibri', 'c')


        #process button presses
        if buttons["back"].highlight(mouse_used):
            mouse_used = True
            action = "main"

        elif used_buttons["res_up"].highlight(mouse_used):
            mouse_used = True
            if res < 2:
                res += 1
            
        elif used_buttons["res_down"].highlight(mouse_used):
            mouse_used = True
            if res > 0:
                res -= 1
            
        elif used_buttons["screen_up"].highlight(mouse_used) or used_buttons["screen_down"].highlight(mouse_used):
            mouse_used = True
            fullscreen = not fullscreen

        elif used_buttons["apply"].highlight(mouse_used):
            resolution = resolutions[res]
            if fullscreen:
                window = pygame.display.set_mode((resolution[0], resolution[1]), pygame.FULLSCREEN)
            else:
                window = pygame.display.set_mode((resolution[0], resolution[1]))
            mouse_used = True

            #reset all sizes
            used_buttons["back"].set_size(resolution[0]/5, resolution[0] / 30)
            used_buttons["apply"].set_size(resolution[0]/5, resolution[0] / 30)
            used_buttons["res_up"].set_size(resolution[1]/54)
            used_buttons["res_down"].set_size(resolution[1]/54)
            used_buttons["screen_up"].set_size(resolution[1]/54)
            used_buttons["screen_down"].set_size(resolution[1]/54)

            #reset all positions
            used_buttons["back"].set_pos([resolution[0]/2, resolution[1] - resolution[0] / 16])
            used_buttons["apply"].set_pos([resolution[0]/2, resolution[1] - resolution[0] / 7.5])
            used_buttons["res_up"].set_pos([resolution[0]/2 - resolution[0]/7, resolution[1]/3])
            used_buttons["res_down"].set_pos([resolution[0]/2 - resolution[0]/7, resolution[1]/3])
            used_buttons["screen_up"].set_pos([resolution[0]/2 - resolution[0]/7, resolution[1]/2])
            used_buttons["screen_down"].set_pos([resolution[0]/2 - resolution[0]/7, resolution[1]/2])

            

        #render all buttons
        for button in used_buttons:
            used_buttons[button].render()

        #check if game is quit
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()

        window.blit(image, [resolution[0] - resolution[1]*1.1, 0])

        pygame.display.update()

    return action, mouse_used, resolution, window

#----------------------------------------------------------------------------------------------------------------------------------
def main_menu(window, action, buttons, mouse_used):
    used_buttons = {"settings" : buttons["settings"],
                    "quit" : buttons["quit"],
                    "start" : buttons["start"]
                    }

    image = pygame.image.load("assets\{}.jpg".format("brain"))
    image = pygame.transform.scale(image, ((window.get_size()[1]), (window.get_size()[1])))

    start = window.get_size()[1] / 2
    incriment = window.get_size()[1] * 7 / 54
    used_buttons["start"].set_pos([window.get_size()[0] / 5, start])
    used_buttons["settings"].set_pos([window.get_size()[0] / 5, start + incriment])
    used_buttons["quit"].set_pos([window.get_size()[0] / 5, start + incriment * 2])

    incriment_1 = window.get_size()[1] / 10
    
    while action == "main":
        #Reset mouse usage
        if not pygame.mouse.get_pressed()[0]:
            mouse_used = False

        window.fill(const.COL["black"])

        if buttons["settings"].highlight(mouse_used):
            mouse_used = True
            action = "settings"

        elif buttons["quit"].highlight(mouse_used):
            pygame.quit()
            quit()

        elif buttons["start"].highlight(mouse_used):
            mouse_used = True
            action = "race"
        

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()

        for button in used_buttons:
            used_buttons[button].render()
            

        window.blit(image, [window.get_size()[0] - window.get_size()[1]*1.1, 0])
        pygame_ui.draw_text(window, 'Artificial', [window.get_size()[0]/5, window.get_size()[1]/10.8], int(window.get_size()[1] / 10.5), const.COL["white"], 'impact', 'c')
        pygame_ui.draw_text(window, 'Intelligence', [window.get_size()[0]/5, window.get_size()[1]/10.8 + incriment_1], int(window.get_size()[1] / 10.5), const.COL["white"], 'impact', 'c')
        pygame_ui.draw_text(window, 'Alex Elwood | BETA (0.0.1)', [window.get_size()[0] / 1.007, window.get_size()[1]/1.02], int(window.get_size()[1] / 56), const.COL["white"], 'calibri', 'mr')
        pygame.display.update()

    return action, mouse_used

#----------------------------------------------------------------------------------------------------------------------------------
def main():

    clock = pygame.time.Clock()
    resolution = [1280, 720]
    pygame.init()
    window = pygame.display.set_mode((resolution[0], resolution[1]))
    pygame.display.set_caption('Physics')

    mouse_used = False

    buttons = init_objects(window)

    action = "race"
    while True:
        if action == "main":
            action, mouse_used = main_menu(window, action, buttons, mouse_used)
        elif action == "settings":
            action, mouse_used, window, resolution = settings(window, resolution, action, buttons, mouse_used)
        elif action == "race":
            action, mouse_used = game.race(window, clock, action, mouse_used)
        elif action == "network":
            action, mouse_used = network.network(window, clock, action, mouse_used)
        else:
            pygame.quit()
            quit()

        
            
if __name__ == "__main__":
    main()
