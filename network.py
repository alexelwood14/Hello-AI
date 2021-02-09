import pygame
import math
import random
import numpy as np
import ai
import pygame_ui
from pygame.locals import *

#----------------------------------------------------------------------------------------------------------------------------------
def network(window, clock, colours, resolution, action, mouse_used):
    display_debug = True
    display_biases = False

    network = ai.Neural_Network(window, colours, resolution, 6, [12,12], 6)
    network.process([random.random(),random.random(),random.random(),random.random(),random.random(),random.random()], True)

    while action == "network":
        window.fill(colours["light_grey"])
        frame_time = clock.tick() / 1000

        #process inputs
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
           
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    if display_debug:
                        display_debug = False
                    else:
                        display_debug = True

                if event.key == pygame.K_x:
                    if display_biases:
                        network.set_display_biases(False)
                        display_biases = False
                    else:
                        network.set_display_biases(True)
                        display_biases = True

                if event.key == K_m:
                    action = "main"
                
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()


        network.render()
                    

        if display_debug:
            pygame_ui.draw_text(window, "fps: {}".format(str(int(clock.get_fps()))),
                      [resolution[0]/32, resolution[1]/14], int(resolution[0]/72), colours["white"], "calibri", "ml")
            if display_biases:
                pygame_ui.draw_text(window, "Displaying Biases",
                      [resolution[0]/32, resolution[1]/10], int(resolution[0]/72), colours["white"], "calibri", "ml")
            else:
                pygame_ui.draw_text(window, "Displaying Activations",
                      [resolution[0]/32, resolution[1]/10], int(resolution[0]/72), colours["white"], "calibri", "ml")


        pygame.display.update()
        

    return action, mouse_used

#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
