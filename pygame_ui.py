import pygame
from pygame.locals import*

def draw_text(window, text, pos, size, colour, fontName, method):
    font = pygame.font.Font(pygame.font.match_font(fontName), int(size))
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect()
    
    if method == 'mt':
        text_rect.midtop = (pos[0], pos[1])
    elif method == 'c':
        text_rect.center = (pos[0], pos[1])
    elif method == "ml":
        text_rect.midleft = (pos[0], pos[1])
    elif method == "mr":
        text_rect.midright = (pos[0], pos[1])
        
    window.blit(text_surface, text_rect)

#------------------------------------------------------------------------------------------------------------------
class Slider():
    def __init__(self, window, pos, maximum, colours, size, name):
        self.window = window
        self.name = name
        self.maximum = maximum
        self.size = size
        self.colours = colours
        self.pos = pos
        self.slider_pos = 50.0
        self.grabbed = False

    def dragging(self, mouse_down):
        if mouse_down:
            mouse_pos = pygame.mouse.get_pos()
            slider_pos = self.pos[0] + self.size * 12 * self.slider_pos / 100
            if (mouse_pos[0] <= slider_pos + self.size and mouse_pos[0] >= slider_pos and
                mouse_pos[1] <= self.pos[1] + self.size and mouse_pos[1] >= self.pos[1] - self.size) or self.grabbed:

                self.grabbed = True

                self.slider_pos = (mouse_pos[0] - self.size/2 - self.pos[0]) / self.size / 12 * 100
                if self.slider_pos > 100:
                    self.slider_pos = 100
                elif self.slider_pos < 0:
                    self.slider_pos = 0
                    
            else:
                self.grabbed = False
        else:
            self.grabbed = False

        return float(self.maximum * self.slider_pos / 100)

    def render(self):
        pygame.draw.rect(self.window, self.colours[0], [self.pos[0], self.pos[1] - self.size/2, self.size * 13, self.size])
        pygame.draw.rect(self.window, self.colours[1], [self.pos[0] + self.size * 14, self.pos[1] - self.size * 1.25, self.size * 4, self.size * 2.5])
        draw_text(self.window, self.name, [self.pos[0] + self.size * 9, self.pos[1] - self.size * 2.2], self.size * 2, self.colours[2], "Ariel", "c")
        draw_text(self.window, "{}%".format(str(int(self.slider_pos))), [self.pos[0] + self.size * 16, self.pos[1]], self.size * 2, self.colours[2], "Ariel", "c")

        pygame.draw.rect(self.window, self.colours[1], [self.pos[0] + self.size * 12 * self.slider_pos / 100, self.pos[1] - self.size, self.size, self.size * 2])

    def set_pos(self, pos):
        self.pos = pos

    def set_size(self, size):
        self.size = size

    def set_maximum(self, maximum):
        self.maximum = maximum

#----------------------------------------------------------------------------------------------------------------------------------
class Button():
    def __init__(self, window, pos, size, text_size, text, colour_1, colour_2):
        self.window = window
        self.pos = pos
        self.size = size
        self.aspect = 3.5
        self.colour_1 = colour_1
        self.colour_2 = colour_2
        self.text = text
        self.text_size = text_size
        self.highlighted = False

        self.image = pygame.Surface((self.size, self.size / self.aspect))
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos[0], self.pos[1])

    def render(self):
        if self.highlighted:
            pygame.draw.rect(self.window, self.colour_2, self.rect, int(self.size / 60))
            pygame.draw.polygon(self.window, self.colour_2,
                                [[self.rect[0], self.rect[1]], [self.rect[0], self.rect[1] + self.rect[3]],
                                 [self.rect[0] + self.rect[2], self.rect[1] + self.rect[3]], [self.rect[0] + self.rect[2], self.rect[1]]])
            draw_text(self.window, self.text, [self.pos[0], self.pos[1]],
                      self.text_size, self.colour_1, 'calibri', 'c')

        else:
            pygame.draw.rect(self.window, self.colour_2, self.rect, int(self.size / 60))
            draw_text(self.window, self.text, [self.pos[0], self.pos[1]],
                     self.text_size, self.colour_2, 'calibri', 'c')

    def collision(self):
        mouse_pos = pygame.mouse.get_pos()
        if (mouse_pos[0] >= self.rect[0] and mouse_pos[0] <= self.rect[0] + self.rect[2] and
            mouse_pos[1] >= self.rect[1] and mouse_pos[1] <= self.rect[1] + self.rect[3]):
            return True
        else:
            return False

    def set_colours(self, colour_1, colour_2):
        self.colour_1 = colour_1
        self.colour_2 = colour_2

    def set_pos(self, pos):
        self.pos = pos
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos[0], self.pos[1])

    def set_size(self, size, text_size):
        self.size = size
        self.image = pygame.Surface((self.size, self.size / self.aspect))
        self.text_size = text_size


class Radio_Button(Button):
    def __init__(self, window, pos, size, text, colour_1, colour_2):
        super().__init__(window, pos, size, text, colour_1, colour_2)

    def highlight(self, selected=""):
        if (self.collision() and pygame.mouse.get_pressed()[0]) or self.text == selected:
            self.highlighted = True
            return self.text
        else:
            self.highlighted = False
            return selected
    

class Single_Button(Button):
    def __init__(self, window, pos, size, text_size, text, colour_1, colour_2):
        super().__init__(window, pos, size, text_size, text, colour_1, colour_2)

    def highlight(self, mouse_used, selected=""):
        if self.collision():
            self.highlighted = True
            if pygame.mouse.get_pressed()[0] and not mouse_used:
                return True
        else:
            self.highlighted = False
        return False

#----------------------------------------------------------------------------------------------------------------------------------
class Image_Button():
    def __init__(self, window, pos, size, text, text_size, image, colours):
        self.window = window
        self.pos = pos
        self.size = size
        self.aspect = 3.5
        self.colours = colours
        self.image = pygame.image.load("assets\{}.jpg".format(image))
        self.image = pygame.transform.scale(self.image, self.size)
        self.text = text
        self.text_size = text_size
        self.highlighted = False

    def collision(self):
        mouse_pos = pygame.mouse.get_pos()
        if (mouse_pos[0] >= self.pos[0]- self.size[0]/2 and mouse_pos[0] <= self.pos[0] + self.size[0]/2 and
            mouse_pos[1] >= self.pos[1] - self.size[1]/2 and mouse_pos[1] <= self.pos[1] + self.size[1]/2):
            return True
        else:
            return False

    def render(self):
        self.window.blit(self.image, [self.pos[0]- self.size[0]/2, self.pos[1] - self.size[1]/2])
        draw_text(self.window, self.text, [self.pos[0], self.pos[1] + self.size[1]*0.6], self.text_size, self.colours["white"], "calibri", "c")
        if self.highlighted:
            pygame.draw.rect(self.window, self.colours["red"], [self.pos[0] - self.size[0]/2, self.pos[1] - self.size[1]/2,
                                                             self.size[0], self.size[1]], 5)
        else:
            pygame.draw.rect(self.window, self.colours["grey"], [self.pos[0] - self.size[0]/2, self.pos[1] - self.size[1]/2,
                                                             self.size[0], self.size[1]], 5)

    def highlight(self, mouse_used):
        if self.collision():
            self.highlighted = True
            if pygame.mouse.get_pressed()[0] and not mouse_used:
                return True
        else:
            self.highlighted = False
        return False
                                       

#----------------------------------------------------------------------------------------------------------------------------------
class Arrow_Button():
    def __init__(self, window, pos, size, colour_1, colour_2):
        self.window = window
        self.pos = pos
        self.size = size
        self.colour_1 = colour_1
        self.colour_2 = colour_2
        self.highlighted = False

    def highlight(self, mouse_used=False):
        if self.collision():
            self.highlighted = True
            if pygame.mouse.get_pressed()[0] and not mouse_used:
                return True
        else:
            self.highlighted = False
        return False

    def set_pos(self, pos):
        self.pos = pos

    def set_size(self, size):
        self.size = size

class Up_Arrow(Arrow_Button):
    def __init__(self, window, pos, size, colour_1, colour_2):
        super().__init__(window, pos, size, colour_1, colour_2)

    def collision(self):
        mouse_pos = pygame.mouse.get_pos()
        if (mouse_pos[0] >= self.pos[0] - self.size and mouse_pos[0] <= self.pos[0] + self.size and
            mouse_pos[1] >= self.pos[1] - self.size and mouse_pos[1] <= self.pos[1]):
            return True
        else:
            return False

    def render(self):
        if self.highlighted:
            pygame.draw.polygon(self.window, self.colour_2, [[self.pos[0] - self.size, self.pos[1] - self.size / 4],
                                                             [self.pos[0] + self.size, self.pos[1] - self.size / 4],
                                                             [self.pos[0], self.pos[1] - self.size - self.size / 4]])
            pygame.draw.lines(self.window, self.colour_1, True, [[self.pos[0] - self.size, self.pos[1] - self.size / 4],
                                                                 [self.pos[0] + self.size, self.pos[1] - self.size / 4],
                                                                 [self.pos[0], self.pos[1] - self.size - self.size / 4]], int(self.size / 10))
        else:
            pygame.draw.polygon(self.window, self.colour_1, [[self.pos[0] - self.size, self.pos[1] - self.size / 4],
                                                             [self.pos[0] + self.size, self.pos[1] - self.size / 4],
                                                             [self.pos[0], self.pos[1] - self.size - self.size / 4]])

class Down_Arrow(Arrow_Button):
    def __init__(self, window, pos, size, colour_1, colour_2):
        super().__init__(window, pos, size, colour_1, colour_2)

    def collision(self):
        mouse_pos = pygame.mouse.get_pos()
        if (mouse_pos[0] >= self.pos[0] - self.size and mouse_pos[0] <= self.pos[0] + self.size and
            mouse_pos[1] >= self.pos[1] and mouse_pos[1] <= self.pos[1] + self.size):
            return True
        else:
            return False

    def render(self):
        if self.highlighted:
            pygame.draw.polygon(self.window, self.colour_2, [[self.pos[0] - self.size, self.pos[1] + self.size / 4],
                                                             [self.pos[0] + self.size, self.pos[1] + self.size / 4],
                                                             [self.pos[0], self.pos[1] + self.size + self.size / 4]])
            pygame.draw.lines(self.window, self.colour_1, True, [[self.pos[0] - self.size, self.pos[1] + self.size / 4],
                                                                 [self.pos[0] + self.size, self.pos[1] + self.size / 4],
                                                                 [self.pos[0], self.pos[1] + self.size + self.size / 4]], int(self.size / 10))
        else:
            pygame.draw.polygon(self.window, self.colour_1, [[self.pos[0] - self.size, self.pos[1] + self.size / 4],
                                                             [self.pos[0] + self.size, self.pos[1] + self.size / 4],
                                                             [self.pos[0], self.pos[1] + self.size + self.size / 4]])
    
#----------------------------------------------------------------------------------------------------------------------------------
class Cross_Button():
    def __init__(self, window, pos, size, colour_1, colour_2):
        self.window = window
        self.pos = pos
        self.size = size
        self.colour_1 = colour_1
        self.colour_2 = colour_2
        self.highlighted = False

    def collision(self):
        mouse_pos = pygame.mouse.get_pos()
        if (mouse_pos[0] >= self.pos[0] - self.size and mouse_pos[0] <= self.pos[0] + self.size and
            mouse_pos[1] >= self.pos[1] - self.size and mouse_pos[1] <= self.pos[1] + self.size):
            return True
        else:
            return False

    def highlight(self, mouse_used):
        if self.collision():
            self.highlighted = True
            if pygame.mouse.get_pressed()[0] and not mouse_used:
                return True
        else:
            self.highlighted = False
        return False

    def render(self):
        if self.highlighted:
            pygame.draw.rect(self.window, self.colour_2, [self.pos[0] - self.size, self.pos[1] - self.size, self.size * 2, self.size * 2])
            pygame.draw.polygon(self.window, self.colour_1, [[self.pos[0] - self.size / 2, self.pos[1] - self.size / 2],
                                                             [self.pos[0] - self.size / 4, self.pos[1] - self.size / 2],
                                                             [self.pos[0], self.pos[1] - self.size / 6],
                                                             [self.pos[0] + self.size / 4, self.pos[1] - self.size / 2],
                                                             [self.pos[0] + self.size / 2, self.pos[1] - self.size / 2],
                                                             [self.pos[0] + self.size / 6, self.pos[1]],
                                                             [self.pos[0] + self.size / 2, self.pos[1] + self.size / 2],
                                                             [self.pos[0] + self.size / 4, self.pos[1] + self.size / 2],
                                                             [self.pos[0], self.pos[1] + self.size / 6],
                                                             [self.pos[0] - self.size / 4, self.pos[1] + self.size / 2],
                                                             [self.pos[0] - self.size / 2, self.pos[1] + self.size / 2],
                                                             [self.pos[0] - self.size / 6, self.pos[1]]])
        else:
            pygame.draw.rect(self.window, self.colour_1, [self.pos[0] - self.size, self.pos[1] - self.size, self.size * 2, self.size * 2])
            pygame.draw.polygon(self.window, self.colour_2, [[self.pos[0] - self.size / 2, self.pos[1] - self.size / 2],
                                                             [self.pos[0] - self.size / 4, self.pos[1] - self.size / 2],
                                                             [self.pos[0], self.pos[1] - self.size / 6],
                                                             [self.pos[0] + self.size / 4, self.pos[1] - self.size / 2],
                                                             [self.pos[0] + self.size / 2, self.pos[1] - self.size / 2],
                                                             [self.pos[0] + self.size / 6, self.pos[1]],
                                                             [self.pos[0] + self.size / 2, self.pos[1] + self.size / 2],
                                                             [self.pos[0] + self.size / 4, self.pos[1] + self.size / 2],
                                                             [self.pos[0], self.pos[1] + self.size / 6],
                                                             [self.pos[0] - self.size / 4, self.pos[1] + self.size / 2],
                                                             [self.pos[0] - self.size / 2, self.pos[1] + self.size / 2],
                                                             [self.pos[0] - self.size / 6, self.pos[1]]])

    def set_pos(self, pos):
        self.pos = pos
#----------------------------------------------------------------------------------------------------------------------------------
class Ball_Creator():
    def __init__(self, window, pos, colours, resolution):
        self.window = window
        self.pos = pos
        self.colours = colours
        self.colour = 0
        self.radius = int(resolution[1]/54)
        self.mass = 20

        self.ball_colours = [colours["yellow"], colours["orange"], colours["red"],
                        colours["light_blue"], colours["blue"], colours["green"],
                        colours["dark_green"], colours["purple"], colours["pink"]]
        
        self.delete = Cross_Button(window, [pos[0] + resolution[1]/27*14, pos[1]], resolution[1]/36, colours["red"], colours["white"])
        
        self.colour_up = Up_Arrow(window, [pos[0] - resolution[1]/2.16, pos[1]], resolution[1]/54, colours["light_grey"], colours["grey"])
        self.colour_down = Down_Arrow(window, [pos[0] - resolution[1]/2.16, pos[1]], resolution[1]/54, colours["light_grey"], colours["grey"])
        
        self.radius_up = Up_Arrow(window, [pos[0], pos[1]], resolution[1]/54, colours["light_grey"], colours["grey"])
        self.radius_down = Down_Arrow(window, [pos[0], pos[1]], resolution[1]/54, colours["light_grey"], colours["grey"])
        
        self.mass_up = Up_Arrow(window, [pos[0] + resolution[1]/54*19, pos[1]], resolution[1]/54, colours["light_grey"], colours["grey"])
        self.mass_down = Down_Arrow(window, [pos[0] + resolution[1]/54*19, pos[1]], resolution[1]/54, colours["light_grey"], colours["grey"])

    def highlight(self, mouse_used, resolution):
        if self.delete.highlight(mouse_used):
            return True, True
        
        elif self.colour_up.highlight(mouse_used):
            self.colour += 1
            if self.colour > len(self.ball_colours) - 1:
                self.colour = 0
            return True, False
        elif self.colour_down.highlight(mouse_used):
            self.colour -= 1
            if self.colour < 0:
                self.colour = len(self.ball_colours) - 1
            return True, False
                
        elif self.mass_up.highlight() and self.mass < 999:
            self.mass += 1
            return True, False
        elif self.mass_down.highlight() and self.mass > 1:
            self.mass -= 1
            return True, False
            
        elif self.radius_up.highlight() and self.radius < resolution[1]/10.8:
            self.radius += 1
            return True, False
        elif self.radius_down.highlight() and self.radius > resolution[1]/108:
            self.radius -= 1
            return True, False
        return False, False

    def render(self, resolution):
        pygame.draw.rect(self.window, self.colours["grey"], [self.pos[0] - resolution[1]/1.8, self.pos[1] - resolution[1]/27, resolution[1]/0.9, resolution[1]/13.5])
        if self.radius >= resolution[1]/216*7:
            pygame.draw.circle(self.window, self.ball_colours[self.colour], [int(self.pos[0] - resolution[1]/27*14), int(self.pos[1])], int(resolution[1]/216*7))
        else:
            pygame.draw.circle(self.window, self.ball_colours[self.colour], [int(self.pos[0] - resolution[1]/27*14), int(self.pos[1])], self.radius)
        draw_text(self.window, "RADIUS: {}".format(self.radius), [self.pos[0] - resolution[1]/108*37, self.pos[1] + 3], resolution[0]/30, self.colours["white"], "calibri", "ml")
        draw_text(self.window, "MASS: {}".format(self.mass), [self.pos[0] + resolution[1]/18, self.pos[1] + 3], resolution[0]/30, self.colours["white"], "calibri", "ml")
        self.delete.render()
        self.colour_up.render()
        self.colour_down.render()
        self.mass_up.render()
        self.mass_down.render()
        self.radius_up.render()
        self.radius_down.render()

    def get_attributes(self):
        return self.mass, self.radius, self.ball_colours[self.colour]

    def get_colour(self):
        return self.colour

    def set_mass(self, mass):
        self.mass = mass

    def set_radius(self, radius):
        self.radius = int(radius)

    def set_colour(self, colour):
        self.colour = colour

    def set_pos(self, pos, resolution):
        self.pos = pos
        self.delete.set_pos([pos[0] + resolution[1]/27*14, pos[1]])

        self.colour_up.set_pos([pos[0] - resolution[1]/2.16, pos[1]])
        self.colour_down.set_pos([pos[0] - resolution[1]/2.16, pos[1]])

        self.radius_up.set_pos([pos[0], pos[1]])
        self.radius_down.set_pos([pos[0], pos[1]])

        self.mass_up.set_pos([pos[0] + resolution[1]/54*19, pos[1]])
        self.mass_down.set_pos([pos[0] + resolution[1]/54*19, pos[1]])

class Add_Creator():
    def __init__(self, window, pos, colours):
        self.window = window
        self.pos = pos
        self.colours = colours
        self.highlighted = False

    def collision(self, resolution):
        mouse_pos = pygame.mouse.get_pos()
        if (mouse_pos[0] >= self.pos[0] - resolution[1]/1.8 and mouse_pos[0] <= self.pos[0] + resolution[1]/1.8 and
            mouse_pos[1] >= self.pos[1] - resolution[1]/27 and mouse_pos[1] <= self.pos[1] + resolution[1]/27):
            return True
        else:
            return False

    def render(self, resolution):
        if self.highlighted:
            pygame.draw.rect(self.window, self.colours["light_grey"], [self.pos[0] - resolution[1]/1.8, self.pos[1] - resolution[1]/27, resolution[1]/0.9, resolution[1]/13.5])
            pygame.draw.rect(self.window, self.colours["grey"], [self.pos[0] - resolution[1]/1.8, self.pos[1] - resolution[1]/27, resolution[1]/0.9, resolution[1]/13.5], 4)

        else:
            pygame.draw.rect(self.window, self.colours["grey"], [self.pos[0] - resolution[1]/1.8, self.pos[1] - resolution[1]/27, resolution[1]/0.9, resolution[1]/13.5])


        size_1 = resolution[1]/36
        size_2 = resolution[1]/1080*7
        pygame.draw.polygon(self.window, self.colours["green"], [[self.pos[0] - size_2, self.pos[1] - size_1],
                                                                 [self.pos[0] + size_2, self.pos[1] - size_1],
                                                                 [self.pos[0] + size_2, self.pos[1] - size_2],
                                                                 [self.pos[0] + size_1, self.pos[1] - size_2],
                                                                 [self.pos[0] + size_1, self.pos[1] + size_2],
                                                                 [self.pos[0] + size_2, self.pos[1] + size_2],
                                                                 [self.pos[0] + size_2, self.pos[1] + size_1],
                                                                 [self.pos[0] - size_2, self.pos[1] + size_1],
                                                                 [self.pos[0] - size_2, self.pos[1] + size_2],
                                                                 [self.pos[0] - size_1, self.pos[1] + size_2],
                                                                 [self.pos[0] - size_1, self.pos[1] - size_2],
                                                                 [self.pos[0] - size_2, self.pos[1] - size_2]])

    def highlight(self, mouse_used, resolution):
        if self.collision(resolution):
            self.highlighted = True
            if pygame.mouse.get_pressed()[0] and not mouse_used:
                return True
        else:
            self.highlighted = False
        return False

    def set_pos(self, pos):
        self.pos = pos
        
#----------------------------------------------------------------------------------------------------------------------------------
class Scroll_Bar():
    def __init__(self, window, pos, colour, resolution):
        self.window = window
        self.pos = pos
        self.colour = colour
        self.grabbed = False
        self.slider_pos = 0
        self.slider_size = resolution[1]/5.4
        self.max = resolution[1]/1.08

    def render(self):
        pygame.draw.rect(self.window, self.colour, [self.pos[0] - self.max/50, self.pos[1] - self.max/2, self.max/25, self.max], int(self.max/250))
        pygame.draw.rect(self.window, self.colour, [self.pos[0] - self.max/50, self.slider_pos + self.max/25, self.max/25, self.slider_size])

    def dragging(self):        
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            if (mouse_pos[0] <= self.pos[0] + self.max/25 and mouse_pos[0] >= self.pos[0] and
                mouse_pos[1] <= self.slider_pos + self.slider_size + self.max/25 and mouse_pos[1] >= self.slider_pos + self.max/25) or self.grabbed:

                self.grabbed = True

                self.slider_pos = mouse_pos[1] - self.slider_size / 2 - self.max/25
                if self.slider_pos > self.max - self.slider_size:
                    self.slider_pos = self.max - self.slider_size
                elif self.slider_pos < 0:
                    self.slider_pos = 0
                    
            else:
                self.grabbed = False
        else:
            self.grabbed = False

        if self.slider_size == self.max:
            return 0
        else:
            return (self.slider_pos / (self.max - self.slider_size))

    def set_size(self, size):
        self.slider_size = size

    def reset_size(self, resolution):
        self.slider_size = resolution / 5.4
        self.max = resolution / 1.08

    def set_pos(self, pos):
        self.pos = pos

#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
