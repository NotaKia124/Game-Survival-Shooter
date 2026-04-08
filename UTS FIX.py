import pygame
import random
import sys

pygame.init()

# ===== Initilization Screen =====
ScreenWidth = 1000
ScreenHeight = 500

Screen = pygame.display.set_mode((ScreenWidth, ScreenHeight))
pygame.display.set_caption("Game Survival Shooter UTS PBO")

# ===== Initilization font =====
font = pygame.font.SysFont(None, 36)

# ===== Colors =====
Green = (0, 255, 0) #Player

Red = (255, 0, 0) #Normal Enemy
Blue = (0, 0, 255) #Speedy Enemy
DarkGrey = (70, 70, 70) #Shooter Enemy

Grey = (128, 128, 128) #Platform
White = (255, 255, 255) #BG

Black = (0, 0, 0) #Bullet

# ===== Clock =====
Clock = pygame.time.Clock()

# ===== Score Variable =====
Time_Score = 0
Kill_Score = 0
Game_Score = 0

# ===== Constant Variable =====
Gravity = 0.98
MaxEnemy = 12
Spawn_CD = 90

# ===== Other Variables =====
Spawn_Timer = Spawn_CD
GameState = "MENU"

# ===== Class players =====
class Players:
    def __init__(self, x, y):
        # ===== Player's Spawn Coordinate =====
        self.x = x
        self.y = y

        # ===== Player's Velocity =====
        self.Velocity_x = 0
        self.Velocity_y = 0

        # ===== Player's Speed Control =====
        self.Acceleration = 0.6
        self.MaxSpeed = 6
        self.Friction = 0.1

        # ===== Player's Size =====
        self.Width = 50
        self.Height = 50

        # ===== Player's CD =====
        self.HitCooldown = 0
        self.ShotCooldown = 0

        # ===== Player's Other Stats =====
        self.Color = Green
        self.Health = 3
        self.Facing = 1  
        self.Bullets = []
        self.IsJumping = False
        self.IsAccel = False

    def Move(self, keys):
        # ===== 
        self.IsAccel = False

        # ===== Left and Right Movement =====
        if keys[pygame.K_a]:
            self.Velocity_x -= self.Acceleration
            self.Facing = -1 
            self.IsAccel = True

        if keys[pygame.K_d]:
            self.Velocity_x += self.Acceleration
            self.Facing = 1 
            self.IsAccel = True

        # ===== Max Speed =====
        if self.Velocity_x >= self.MaxSpeed:
            self.Velocity_x = self.MaxSpeed
        if self.Velocity_x <= -self.MaxSpeed:
            self.Velocity_x = -self.MaxSpeed

        # ===== Apply Friction =====
        if not self.IsAccel:
            self.FrictionMech()
            if self.Velocity_x >= 0 and self.Velocity_x <= 0.1:
                self.Velocity_x = 0
            elif self.Velocity_x <= 0 and self.Velocity_x >= -0.1:
                self.Velocity_x = 0

        # ===== Update Possition =====
        self.x += self.Velocity_x

        # ===== Left and Right Border =====
        if self.x <= 0:
            self.x = 0
            self.Velocity_x = 0
        if self.x >= ScreenWidth - self.Width:
            self.x = ScreenWidth - self.Width
            self.Velocity_x = 0

    def Shot(self):
        if self.ShotCooldown == 0:
            direction = self.Facing

            if direction == 1:
                Bullet_Spawn = self.x + self.Width
            elif direction == -1:
                Bullet_Spawn = self.x

            bullet = Bullet(Bullet_Spawn, self.y + self.Height // 2, direction)

            self.Bullets.append(bullet)
            self.ShotCooldown = 60

    def FrictionMech(self):# ===== Friction Mechanic =====
        self.Velocity_x = self.Velocity_x * (1 - self.Friction)
    
    def DrawInScreen(self, Surface):# ===== Spawn The Player =====
        pygame.draw.rect(Surface, self.Color, (self.x, self.y, self.Width, self.Height))
    
    def get_rect(self):# ===== get player hitbox =====
        return pygame.Rect(self.x, self.y, self.Width, self.Height)

# ===== Class Enemy =====
class Enemys:
    def __init__(self, x, y):
        # ===== Enemy's Spawn Coordinate =====
        self.x = x
        self.y = y

        # ===== Enemy's Size =====
        self.Width = 50
        self.Height = 50

        # ===== Enemy's Speed =====
        self.Speed = 2

        # ===== Enemy's Other Stats
        self.Color = Red
        self.ShotCooldown = 60
        self.Facing = 1  
        self.Bullets = []
        self.Alive = True

    def MoveFollowPlayer(self, player):
        # ===== Enemy follow x Player =====
        if self.Alive:
            if abs(self.x - player.x) < self.Speed:
                self.x = player.x
            elif self.x < player.x:
                self.x += self.Speed
                self.Facing = 1
            elif self.x > player.x:
                self.x -= self.Speed
                self.Facing = -1
    
    def DrawInScreen(self, Surface):
        pygame.draw.rect(Surface, self.Color, (self.x, self.y, self.Width, self.Height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.Width, self.Height)
    
# ==== Type Class of Enemy ==== 
class FastEnemy(Enemys):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.Speed = 4
        self.Color = Blue

class ShooterEnemy(Enemys): 

    def __init__(self, x, y):
        super().__init__(x, y)
        self.Speed = 1
        self.Color = DarkGrey
    
    def Shot(self):
        # ===== Enemy shot Player =====
        if self.Alive:
            if self.ShotCooldown == 0:
                direction = self.Facing

                if direction == 1:
                    Bullet_Spawn = self.x + self.Width
                elif direction == -1:
                    Bullet_Spawn = self.x

                bullet = Bullet(Bullet_Spawn, self.y + self.Height // 2, direction)

                if direction == 1:
                    bullet.Speed += 3
                elif direction == -1:
                    bullet.Speed -= 3

                self.Bullets.append(bullet)
                self.ShotCooldown = 120

# ===== Class Platform =====
class Platforms:
    def __init__(self, x, y, Width, Height):
        # ===== Platform's Coordinates =====
        self.x = x
        self.y = y

        # ===== Platform's Size =====
        self.Width = Width
        self.Height = Height

        # ===== Platform's Other Stats =====
        self.Color = Grey

    def DrawInScreen(self, Surface): # ===== Spawn The Platform =====
        pygame.draw.rect(Surface, self.Color, (self.x, self.y, self.Width, self.Height))

    def get_rect(self):# ===== Get Platform Hitbox =====
        return pygame.Rect(self.x, self.y, self.Width, self.Height)

# ===== Class Bullet =====
class Bullet:
    def __init__(self, x, y, Direction):
        # ===== Bullet's Coordinate =====
        self.x = x
        self.y = y

        # ===== Bullet's Size =====
        self.Width = 10
        self.Height = 5

        # ===== Bullet's Other Stats =====
        self.Speed = 9 * Direction
        self.Color = Black

    def Move(self):
        self.x += self.Speed

    def Draw(self, surface):
        pygame.draw.rect(surface, self.Color, (self.x, self.y, self.Width, self.Height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.Width, self.Height)

# ===== Inilization Objects =====
Ground = Platforms(0, ScreenHeight - 75, ScreenWidth, 75)

EnemyTypes = [ShooterEnemy, FastEnemy, Enemys] # ==== List Type of Enemy ====

Platform1 = Platforms(250, 300, 100, 25)
Platform2 = Platforms(650, 300, 100, 25) 

PlatformsList = [Platform1, Platform2]

# ===== Function Enemy Choser =====
def EnemyChoser(): 
    Side = random.choice(["Kiri", "Kanan"])

    if Side == "Kiri":
        x = 0 - 50
        Direction = 1
    elif Side == "Kanan":
        x = ScreenWidth
        Direction = -1

    y = 375

    EnemyClass = random.choice(EnemyTypes)
    Enemy = EnemyClass(x,y)

    Enemy.Facing = Direction

    return Enemy

# ===== Function SetGame =====
def SetGame():
    global Player, BadGuyInScreen, Time_Score, Kill_Score, Game_Score, Spawn_Timer

    Player = Players(675, 250)
    BadGuyInScreen = [] # ==== List enemy in screen ====

    Time_Score = 0
    Kill_Score = 0
    Game_Score = 0

    Spawn_Timer = Spawn_CD

# ===== Run Game =====
running = True
while running:

    Clock.tick(60) # fixxed FPS cap

    # ===== Event Handling =====
    for event in pygame.event.get(): # Player Rage Quit LLOOLOLOLOOOLOLOLO
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if GameState == "MENU":
                    SetGame()
                    GameState = "RUNNING"
                elif GameState == "GAMEOVER":
                    GameState = "MENU"
    
    # ===== Menu Handling =====
    if GameState == "MENU":
        Screen.fill(White)

        title = font.render("SURVIVAL SHOOTER", True, Black)
        start_text = font.render("Press Enter to START", True, Black)

        Screen.blit(title, (ScreenWidth//2 - title.get_width()//2, 180))
        Screen.blit(start_text, (ScreenWidth//2 - start_text.get_width()//2, 240))

        pygame.display.flip()
        continue

    if GameState == "GAMEOVER":
        Screen.fill(White)
    
        over_text = font.render("GAME OVER", True, Red)
        score_text = font.render(f"Score: {Game_Score}", True, Black)
        retry_text = font.render("Press Enter to return MENU", True, Black)
    
        Screen.blit(over_text, (ScreenWidth//2 - over_text.get_width()//2, 180))
        Screen.blit(score_text, (ScreenWidth//2 - score_text.get_width()//2, 220))
        Screen.blit(retry_text, (ScreenWidth//2 - retry_text.get_width()//2, 260))
    
        pygame.display.flip()
        continue
    
    keys = pygame.key.get_pressed() # Keys just keys on keyboards

    # ===== Scoring =====
    Time_Score += 1
    Game_Score = (Time_Score // 120) + Kill_Score

    # ===== Player's Movement =====
    Player.Move(keys)

    # ==== Player's Jumping ====
    if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and not Player.IsJumping:
        Player.Velocity_y = -17
        Player.IsJumping = True
    
    # ==== Player's Gravity ====
    Player.Velocity_y += Gravity
    Player.y += Player.Velocity_y

    # ==== Player's Top Border  ====
    if Player.y < 0:
        Player.y = 0
        Player.Velocity_y = 0

    # ===== Player Shoting CD =====
    if Player.ShotCooldown > 0:
        Player.ShotCooldown -= 1

    if keys[pygame.K_l]:
        Player.Shot()

    for bullet in Player.Bullets:
        bullet.Move()
    
    Player.Bullets = [b for b in Player.Bullets if 0 < b.x < ScreenWidth]

    # ===== Badguy Spawning =====
    if Spawn_Timer > 0:
        Spawn_Timer -= 1

    if len(BadGuyInScreen) < MaxEnemy and Spawn_Timer == 0:
        BadGuyInScreen.append(EnemyChoser())
        Spawn_Timer = Spawn_CD 

    # ===== BadGuy Shooting CD =====
    for BadGuys in BadGuyInScreen:
        BadGuys.MoveFollowPlayer(Player)

        if BadGuys.ShotCooldown > 0:
            BadGuys.ShotCooldown -= 1

        if BadGuys.Alive:
            if isinstance(BadGuys, ShooterEnemy):
                BadGuys.Shot()

        for bullet in BadGuys.Bullets:
            bullet.Move()

    # ===== Player and Badguy Collision =====
    if Player.HitCooldown > 0: # HitCooldown
        Player.HitCooldown -= 1

    for BadGuys in BadGuyInScreen:
        if Player.get_rect().colliderect(BadGuys.get_rect()) and Player.HitCooldown == 0 and BadGuys.Alive:
            Player.HitCooldown = 120
            Player.Health -= 1

    # ===== Enemy Bullet to Player Collision =====
    for BadGuys in BadGuyInScreen:
        for bullet in BadGuys.Bullets[:]:
            if bullet.get_rect().colliderect(Player.get_rect()):
                if Player.HitCooldown == 0:
                    Player.Health -= 1
                    Player.HitCooldown = 60

                BadGuys.Bullets.remove(bullet)

    # ===== Player Bullet to Enemy Collision =====
    for BadGuys in BadGuyInScreen:
        for bullet in Player.Bullets[:]:
            if bullet.get_rect().colliderect(BadGuys.get_rect()) and BadGuys.Alive:
                BadGuys.Alive = False
                Kill_Score += 3

                Player.Bullets.remove(bullet)
    
    BadGuyInScreen = [e for e in BadGuyInScreen if e.Alive]

    # ===== Ground Collision =====
    if Player.get_rect().colliderect(Ground.get_rect()):
        if Player.Velocity_y > 0:  
            Player.IsJumping = False
            Player.y = Ground.y - Player.Height
            Player.Velocity_y = 0 

    # ===== Platform Collision =====
    for Plat in PlatformsList:
        if Player.get_rect().colliderect(Plat.get_rect()):
            if Player.Velocity_y > 0:
                Player.IsJumping = False
                Player.y = Plat.y - Player.Height
                Player.Velocity_y = 0

    # ===== A Little bit of UI =====
    Screen.fill(White)

    hp_text = font.render(f"HP: {Player.Health}", True, Red)
    score_text = font.render(f"Score: {Game_Score}", True, (0,0,0))

    Screen.blit(hp_text, (10, 10))
    Screen.blit(score_text, (10, 40))

    # ===== Render The Game =====
    Player.DrawInScreen(Screen)
    Ground.DrawInScreen(Screen)

    for Plat in PlatformsList:
        Plat.DrawInScreen(Screen)
    
    for bullet in Player.Bullets:
        bullet.Draw(Screen)

    for BadGuys in BadGuyInScreen:
        if BadGuys.Alive:
            BadGuys.DrawInScreen(Screen)

        for bullet in BadGuys.Bullets:
            bullet.Draw(Screen)

    pygame.display.flip()

    # ===== Game Over Stuff =====
    if Player.Health <= 0 or len(BadGuyInScreen) >= MaxEnemy:
        print("Game Over")
        GameState = "GAMEOVER"

pygame.quit()
sys.exit()
