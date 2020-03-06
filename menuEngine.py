"""The following is a game enginge designed for menus, which is an extension of the GVSU educational game engine.
The menu engine is constructed in such a way that parameters and images need only be passed, at which point they will
be converted, processed, and implemented as desired, with much of the process abstracted away from the user. Thus, it
is the beginning of a 'plug and play' game blueprint. This interface requires only paths to the necessary image and
sound files be provided, and the respective functions be bound to the desired keys in pygame.
Authored by Griffin Going, along with GVSU Engine code."""

import abc
import os
import time
import pygame

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import  sys
sys.path.append('.')
from engine.league.league.settings import *
from engine.league.league import *
from helperFuncs import eventNum

class menuEngine():

    def __init__(self, title):
        self.title = title
        self.running = False
        self.clock = None
        self.events = {}
        self.key_events = {}
        self.key_events[Settings.statistics_key] = self.toggle_statistics
        self.objects = []
        self.drawables = pygame.sprite.LayeredUpdates()
        self.screen = None
        self.real_delta_time = 0
        self.visible_statistics = False
        self.statistics_font = None
        self.collisions = {}

    def init_pygame(self):
        """This function sets up the state of the pygame system,
        including passing any specific settings to it."""
        # Startup the pygame system
        pygame.init()
        # Create our window
        self.screen = pygame.display.set_mode((Settings.width, Settings.height))
        # Set the title that will display at the top of the window.
        pygame.display.set_caption(self.title)
        # Create the clock
        self.clock = pygame.time.Clock()
        self.last_checked_time = pygame.time.get_ticks()
        # Startup the joystick system
        pygame.joystick.init()
        # For each joystick we find, initialize the stick
        for i in range(pygame.joystick.get_count()):
            pygame.joystick.Joystick(i).init()
        # Set the repeat delay for key presses
        pygame.key.set_repeat(Settings.key_repeat)
        # Create statistics font
        self.statistics_font = pygame.font.Font(None,30)

    """Here we will iterate through the possible collisions.  If sprite
    i collides with the sprite in the tuple, call the function in the
    tuple"""
    def check_collisions(self):
        for i in self.collisions.keys():
            if pygame.sprite.collide_rect(i, self.collisions[i][0]):
                self.collisions[i][1]()

    def add_group(self, group):
        self.drawables.add(group.sprites())

    """Show/Hide the engine statistics"""
    def toggle_statistics(self):
        self.visible_statistics = not self.visible_statistics

    """draw statistic with this function"""
    def show_statistics(self):
        statistics_string = "Version: " + str(Settings.version)
        statistics_string = statistics_string + " FPS: " + str(int(self.clock.get_fps()))
        fps = self.statistics_font.render(statistics_string, True, Settings.statistics_color)
        self.screen.blit(fps, (10, 10))

    """turn engine off"""
    def stop(self, time):
        self.running = False

    """shut pygame off"""
    def end(self, time):
        pygame.quit()

    """Process all events recieved.  This is a weak system, but
    it works as long as you don't want multiple functions
    to be called per event. This code is from the GVSU educational game engine"""
    def handle_inputs(self):
        for event in pygame.event.get():
            # Check "normal" events
            if event.type in self.events.keys():
                self.events[event.type](self.game_delta_time)
            # Check if these key_event keys were pressed
            if event.type == pygame.KEYDOWN:
                if event.key in self.key_events.keys():
                    self.key_events[event.key](self.game_delta_time)

    """ This is the event counter for our manually created events, call with evCnt()
     This is cast as a lambda function to allow easy incrementing, such that events can be added retroactivey
     and dynamically without harming earlier events"""
    evCnt = lambda: helperFuncs.eventNum.newEvent(helperFuncs.eventNum)

    """Define music to play for menu using pygames mixer. Requires only a file path."""
    def setMusic(self, musicPath):
        pygame.mixer.music.load(musicPath)

    """sets the (x, y) coordinates at which the selector sprite will be located at. Takes any number of 
    options, which are checked against and defined in another method."""
    def setSelectLocations(self, selectorLocations):
        self.selectorLocations = selectorLocations
        self.numSelectOptions = len(selectorLocations) - 1
        self.currentSelection = 0

    """sets up the selector sprite by taking in an array of images, and a pixel size for the selector, converting
    each image as necessary, and then scaling each image. Stores the number of sprites for the iterateSelectorSprite
     function, as to further abstract and simplify use of the menu engine for the user"""""
    def setSelectorSprite(self, selectorSprite, x, y):
        self.selectorSprite = selectorSprite
        self.numSelectorSprites = len(selectorSprite)

        #convert sprites to proper type and size
        for i in range(self.numSelectorSprites):
            selectorSprite[i] = pygame.image.load(selectorSprite[i]).convert_alpha()
            selectorSprite[i] = pygame.transform.scale(selectorSprite[i], (x, y))

        self.selectCounter = 0 #counter for sprite interation
        self.currentSelectorImage = selectorSprite[0]

    """Iterates to the next simage in the array of selector sprites. If there is no 'next', 
    we reset to the first image"""
    def iterateSelectorSprite(self):
        self.currentSelectorImage = self.selectorSprite[self.selectCounter]
        arrCount = self.numSelectorSprites - 1
        if (self.selectCounter >= (arrCount)):
            self.selectCounter = 0
        else:
            self.selectCounter = self.selectCounter + 1

    """Iterates the selection number forward, and implicitly forward in the sprite location array """
    def changeSelectionBack(self, time):
        self.currentSelection = self.currentSelection - 1

        if (self.currentSelection < 0):
            self.currentSelection = self.numSelectOptions

    """Iterates the selection backwards, and implicitly backward in the sprite location array """
    def changeSelectionForward(self, time):
        self.currentSelection = self.currentSelection + 1

        if (self.currentSelection > self.numSelectOptions):
            self.currentSelection = 0

            print(self.currentSelection)
    """Does what it says - plays the music"""
    def playMusic(self):
        pygame.mixer.music.play(-1)

    """converts, scales, and sets the given image to the background of the main menu"""
    def setMenuImage(self, mainMenu):
        self.mainMenu = pygame.image.load(mainMenu).convert_alpha() #convert image
        self.mainMenu = pygame.transform.scale(self.mainMenu, (Settings.width, Settings.height)) #scale to screen size

    """displays the menu background image"""
    def showMenu(self):
        self.screen.blit(self.mainMenu, (0, 0))

    """Using a given set of intro screens, the engine automatically calculates fade in and hold times for each image,
    such that the main menu itself will be displayed at the given number of seconds, which is the intro 'runTime'. 
    Automatically displays images at the center of the screen using a few quick calculations, and automatic image
    resizing is coming soon. Additionally, split-second machine benchmarking will be added prior to the sequence
    such that the time stamp is reliable on any machine in any environment."""
    def showIntro(self, introScreens, runTime):
        #runTime is the total desired time for the entire intro sequence

        black = (0, 0, 0) #fill color for screen
        self.screen.fill(black) #give them something to look at while we do all this wibbly wobbly timey wimey math
        screenWidth = Settings.width
        screenHeight = Settings.height
        fadeTimePerImage = 5.983205318450928  # time for fade in and fade out per image
        darkTime = .5 #time between the previous and next image during which the screen is blank
        #two lines below are for benchmarking machines. above constant is from my machine
        # fadeFrameTimePerFrame = 0.011731775134217505 #time in seconds that each fading frame requires
        # print(fadeFrameTimePerFrame * 510) #print total fade time per image. For testing purposes on various machines
        numImages = len(introScreens) #the number of intro screens
        totalFadeTime = fadeTimePerImage * len(introScreens) #total fade time for the entire intro sequence
        imageHoldTime = (runTime - totalFadeTime - (darkTime * numImages)) / numImages #remaining time to hold each image after fade is remobed

        pygame.mixer.music.play(-1) #start the music

        for i in range(numImages): #calculate image size for centering, and fade image in, hold, then fade out

            imageWidth = introScreens[i].get_width()
            imageHeight = introScreens[i].get_height()

            #resize to display size if too large

            #else, calculate x and y position
            x = (screenWidth / 2) - (imageWidth / 2)
            y = (screenHeight / 2) - (imageHeight / 2)

            for j in range(256):
                introScreens[i].set_alpha(j)
                self.screen.fill(black)
                self.screen.blit(introScreens[i], (x, y))
                pygame.display.flip()
                time.sleep(.01)
            time.sleep(imageHoldTime)
            for j in range(255):
                introScreens[i].set_alpha(255-(j+1))
                self.screen.fill(black)
                self.screen.blit(introScreens[i], (x, y))
                pygame.display.flip()
                time.sleep(.01)
            time.sleep(darkTime)

    def run(self):
        """The main menu loop, which makes animating the menu possible"""
        self.running = True
        while self.running:
            # The time since the last check
            now = pygame.time.get_ticks()
            self.real_delta_time = now - self.last_checked_time
            self.last_checked_time = now
            self.game_delta_time = self.real_delta_time * (0.001 * Settings.gameTimeFactor)

            # Wipe screen
            self.screen.fill(Settings.fill_color)

            # Process inputs
            self.handle_inputs()

            # Update game world
            # Each object must have an update(time) method
            self.check_collisions()
            for o in self.objects:
                o.update(self.game_delta_time)

            #show menu image, animate selector sprite, and show selector image in selected location
            self.showMenu()
            self.iterateSelectorSprite()
            self.screen.blit(self.currentSelectorImage, self.selectorLocations[self.currentSelection])

            # Generate outputs
            # d.update()
            self.drawables.draw(self.screen)

            # Show statistics?
            if self.visible_statistics:
                self.show_statistics()

            # Could keep track of rectangles and update here, but eh.
            pygame.display.flip()

            # Frame limiting code
            self.clock.tick(Settings.fps)
