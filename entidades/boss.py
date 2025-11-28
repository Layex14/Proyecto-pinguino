import pygame 
import math 
from .Entity import Entity

GRAVITY = 0.5
PROJECTILE_SPEED = 15
BOSS_SPEED = 3
BOSS_DASH_SPEED = 20
ATTACK_RANGE_MELEE = 150
ATTACK_RANGE_RANGED = 600
COOLDOWN_ATTACK = 2000

class Proyectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, floor_y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 215, 0)) 
        self.rect = self.image.get_rect(center=(x, y))
        self.floor_y = floor_y

        #trayectoria (Creo)
        dx = target_x - x
        dy = target_y - y
        angle = math.atan2(dy, dx)


        self.vel_x = math.cos(angle) * PROJECTILE_SPEED
        self.vel_y = math.sin(angle) * PROJECTILE_SPEED - 5 
        self.landed = False

    def update(self):
        if not self.landed:
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            self.vel_y += GRAVITY
            

            #colis
            if self.rect.bottom >= self.floor_y:
                self.rect.bottom = self.floor_y
                self.landed = True
                self.vel_x = 0
                self.vel_y = 0


class BossPancho(Entity):
    def __init__(self, x, y, floor_y, player_target, spritesheet, visual_config, animation_data):
        super().__init__("Pancho", spritesheet, visual_config, animation_data, "idle")


        self.floor_y = floor_y
        self.rect.centerx = x
        self.rect.bottom = self.floor_y

        #Nossa IA
        self.player = player_target
        self.projectile = None 
        self.ai_state = 'CHASE' 
        self.last_attack_time = 0


    def get_distance_to_player(self):
            # Teo del compa pitago
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        return math.sqrt(dx**2 + dy**2)
    
    def update(self):
        current_time = pygame.time.get_ticks()
        dist = self.get_distance_to_player()

            #orientacion
        if self.ai_state != 'DASHING_TO_WEAPON':
            if self.player.rect.centerx < self.rect.centerx:
                self.direction = "left"
            else:
                self.direction = "right"
        else:
            if self.projectile and self.projectile.rect.centerx < self.rect.centerx:
                self.direction = "left"
            else:
                self.direction = "right"

        #Cerebro
        if self.ai_state == 'CHASE':
            self.state = 'walk'
            if dist < ATTACK_RANGE_MELEE and (current_time - self.last_attack_time > COOLDOWN_ATTACK):
                self.ai_state = 'ATTACK_MELEE'
                self.last_attack_time = current_time 
                self.current_frame_in_animation = 0
            
            elif dist < ATTACK_RANGE_RANGED and dist > ATTACK_RANGE_MELEE and (current_time - self.last_attack_time > COOLDOWN_ATTACK):
                self.ai_state = 'THROWING'

            else:
                self.move_towards_target(self.player.rect.centerx, BOSS_SPEED)

        elif self.ai_state == 'ATTACK_MELEE':
            
            #arreglar cuando este el idle

            self.state = 'attack_1' if 'attack_1' in self.animation_data else 'idle'
            

            if current_time - self.last_attack_time > 1000: 
                self.ai_state = 'CHASE'

                #pa lanzar el proyectil

        elif self.ai_state == 'THROWING':
            self.state = 'idle' #arreglar cuando haya animacion de ataque
            
            if self.projectile is None:
                # limite del suelo
                self.projectile = Proyectile(self.rect.centerx, 
                                            self.rect.centery, 
                                            self.player.rect.centerx, 
                                            self.player.rect.centery, 
                                            self.floor_y)
                

            self.projectile.update()
            
            if self.projectile.landed:
                self.ai_state = 'DASHING_TO_WEAPON'

                #va hacai el arma lanzada

        elif self.ai_state == 'DASHING_TO_WEAPON':
            self.state = 'walk' 
            
            if self.projectile:
                arrived = self.move_towards_target(self.projectile.rect.centerx, BOSS_DASH_SPEED)
                if arrived:
                    self.projectile = None # Recoge el arma
                    self.last_attack_time = current_time
                    self.ai_state = 'CHASE'
            else:
                self.ai_state = 'CHASE'

            #gravedad

        if self.rect.bottom < self.floor_y:
            self.rect.y += 10 
        elif self.rect.bottom > self.floor_y:
            self.rect.bottom = self.floor_y

        super().update()

    def move_towards_target(self, target_x, speed):
        dx = target_x - self.rect.centerx
        if abs(dx) < speed:
            self.rect.centerx = target_x
            return True 
        
        if dx > 0:
            self.rect.x += speed
        else:
            self.rect.x -= speed
        return False

    def draw_projectile(self, surface):
        """Método auxiliar para dibujar el proyectil si existe."""
        if self.projectile:
            surface.blit(self.projectile.image, self.projectile.rect)