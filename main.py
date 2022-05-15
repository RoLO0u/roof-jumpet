import pygame, json, sys, random

# Execute settings
with open("settings.json", "r") as file:
    settings = json.load(file)

class Frog(pygame.sprite.Sprite):
    """Main sprite, player and frog"""

    def __init__(self) -> None:
        """Init arguments with own and grand class"""

        # init main things from pygame.sprite.Sprite (like i think)
        super().__init__()

        # Init integer to see if frog jumped or not to animate it
        self.frame = 0 # 0 for stand, -1 for left, 1 for right

        # Load frog models standing frog, jumping frog 
        self.sprites = [pygame.image.load(r"sprites\frog_stand.png").convert_alpha(), \
         pygame.transform.flip(pygame.image.load(r"sprites\frog_jump.png").convert_alpha(), True, False), \
         pygame.image.load(r"sprites\frog_jump.png").convert_alpha()]
        # pygame.transform.flip by args True and then False flip image to do frog jump to the right
        
        # Init active sprite
        self.image = self.sprites[self.frame] # Frog stand for start

        # Create model rectangle to use collision and coords methods
        self.rect = self.image.get_rect(midbottom = (200, 500))

        self.jumping = False
        self.jumpsound = pygame.mixer.Sound(r"music\jump.wav")

        # Stamina inits
        self.stamina = 300
        self.maxstamina = 406
        self.staminalen = 203
        self.staminaratio = self.maxstamina / self.staminalen

        self.resist = False

    def move(self, dir: int) -> None:
        """Move player if he has stamina. Positive for right, negative for left"""

        if self.stamina > 0:
            # Move player horizontal (positive for right, negative for left)
            self.rect.x += dir
            # Check if player is out of borders
            self.checkBorders()
            self.stamina -= 3
            if not self.jumping:
                self.jumpsound.play()
        elif self.stamina > -3:
            self.stamina -= 20

    def animate(self) -> None:
        """Edit frame of a player. Animate him"""

        self.image = self.sprites[self.frame] # Change to active sprite, where 
        # self.frame should change in playerInput func

    def checkBorders(self) -> None:
        """Check if player stands in borders"""

        # Check if player is out of right borders
        if self.rect.x > settings["WIDTH"] - 20:
            # If yes move player to left side
            self.rect.x = -10
        # else if player is out of left border
        elif self.rect.x < -20:
            # Move him to right border
            self.rect.x = settings["WIDTH"] - 20
    
    def barDraw(self) -> None:
        pygame.draw.rect(screen, (255, 50, 0), (22, 29, self.stamina / self.staminaratio, 20))

    def playerInput(self) -> None:
        """Take player input from keyboard"""

        # Take all presed keys
        keys = pygame.key.get_pressed()

        self.speed = settings["frog_speed"]
        if keys[pygame.K_SPACE] and (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and not self.resist and self.stamina > 50:
            self.speed = 40
            self.stamina -= 50
            self.resist = True
        elif not keys[pygame.K_SPACE]:
            self.resist = False

        # Check if left button is pressed
        if keys[pygame.K_LEFT]:
            # Move to left for frog_speed * -1 in settings.json if button left is pressed
            self.move(-self.speed)
            self.frame = -1 # Change to -1 to edit animation of frog
            self.jumping = True
        # Check if right button is pressed
        elif keys[pygame.K_RIGHT]:
            # Move to left for frog_speed in settings.json if button right is pressed
            self.move(self.speed)
            self.frame = 1 # Change to 1 to edit animation of frog
            self.jumping = True
        # if no buttons pressed chane animation to stand
        else:
            self.jumping = False
            self.frame = 0 # Change to 0 to edit animation of frog to stand

    def collideCheck(self, sprites: pygame.sprite.Group) -> bool:
        """Check collision"""

        # Iterate every sprite in group
        for sprite in sprites.sprites():
            # If rect collide with other
            if self.rect.colliderect(sprite.rect):
                # Then return True
                return True
        
        # Else if not collide
        return False

    def update(self) -> None:
        """Update classic pygame method"""

        # Check player input and move himself
        self.playerInput()
        # Animate image
        self.animate()
        # Draw bar
        self.barDraw()
        # add stamina if not max
        if self.stamina < self.maxstamina:
            self.stamina += 1

class FallingItems(pygame.sprite.Sprite):
    """Falling items from up of the roof"""
    
    def __init__(self, type: str) -> None:
        """Init main things"""
        
        # Init grand class
        super().__init__()

        # Integer of frames to animate items
        self.frames = 0

        # Load type
        self.type = type
        
        # Check "spike" type
        if self.type == "spike":
            # Load spike images, convert it and put in list of sprites
            self.sprites = [pygame.image.load(r"sprites\spike.png").convert_alpha()]
            # Set speed for it
            self.speed = 10
        
        # Load main image (default)
        self.image = self.sprites[self.frames]

        # Init rect (see in frog class for more) + place in random pos
        self.rect = self.image.get_rect(bottomleft=(random.randint(0, settings["WIDTH"] - 26), random.randint(-20, 0)))

    def move(self) -> None:
        """Move falling item"""
        
        # Add to y coords to move item down and move by speed setted in __init__
        self.rect.y += self.speed

        # Speed update
        self.speed = score // 20 + 10
    
    def update(self) -> None:
        """Update classic pygame method"""

        # Move falling item
        self.move()

def spawnItems(items: pygame.sprite.Group, types: list, score: int) -> tuple:
    """Spawn items, which came out of borders"""

    # Iterating for every sprite in "items"
    for sprite in items.sprites():

        # check if sprite is under screen
        if sprite.rect.top >= settings["HEIGHT"]:
            # Add score
            score += 1
            # Remove sprite from Group
            items.remove(sprite)
            # Add new sprite
            items.add(FallingItems(random.choice(types)))
    
    # Return updated Group of sprites
    return items, score

def display_score(score: int, pos: tuple) -> None:
    """Display score on a screen"""

    # Set score title
    score_surf = pxfont.render(str(score), False, (255, 0, 0))
    # Init rect of the score
    score_rect = score_surf.get_rect(center=pos)
    # Draw score on the screen
    screen.blit(score_surf, score_rect)

# Init pygame
pygame.init()

# Making main screen
screen = pygame.display.set_mode((settings["WIDTH"], settings["HEIGHT"]))
# Set screen caption
pygame.display.set_caption("Roof jumpet")
# Set screen icon
pygame.display.set_icon(pygame.image.load(r"sprites\frog_stand.png").convert_alpha())
# Roof background init
roof = pygame.image.load(r"sprites\roof.png").convert()
# Menu image init
menu = pygame.image.load(r"sprites\menu.png").convert()
# Init clock
clock = pygame.time.Clock()
# Init player from pygame single group
player = pygame.sprite.GroupSingle(Frog())
# Init list of falling items
types = ["spike"]
# Init score
score = 0
# Init is active
is_active = False
# Init font
pxfont = pygame.font.Font(r"fonts\pixels.TTF", 50)
# Init music
bg_music = pygame.mixer.Sound(r"music\music.mp3")
bg_music.set_volume(0.5)
bg_music.play(loops=-1)

# How to get sprite:
# fallingItems.sprites()[n], where n - index of sprite

# Main loop
while True:
    
    # Taking events (exit, mouse, buttons, etc...)
    for event in pygame.event.get():

        # If player push exit button programm closes correctly (without any expressions)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # If active game started
        if is_active:
            # Will do something (maybe)
            pass
        # If not active
        else:
            # If key pressed
            if event.type == pygame.KEYDOWN:
            
                # If space pressed
                if event.key == pygame.K_SPACE:

                    # reset score
                    score = 0
                    player.sprite.stamina = 300
                    # Init group of falling items
                    fallingItems = pygame.sprite.Group(FallingItems(random.choice(types)), FallingItems(random.choice(types)))
                    # Enable active
                    is_active = True

    # If active game started
    if is_active:
        
        # Draw roof (background)
        screen.blit(roof, (0, 0))

        # Move falling items
        fallingItems.update()

        # Spawn and delete new items
        fallingItems, score = spawnItems(fallingItems, types, score)

        # Move player
        player.update()

        # Draw player
        player.draw(screen)

        # Draw score in top left
        display_score(score, (420, 30))

        # Check collision
        if player.sprite.collideCheck(fallingItems):
            is_active = False

        # Draw items
        fallingItems.draw(screen)
    
    # If game isn't active
    else:

        # Draw Start menu
        screen.blit(menu, (0, 0))

        # Display score in bottom centre
        display_score(score, (250, 500))

    # Update screen
    pygame.display.update()

    # Set game framerate (FPS)
    clock.tick(settings["FPS"])