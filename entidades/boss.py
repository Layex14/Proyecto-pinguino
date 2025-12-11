import pygame
import math
from .Entity import Entity 


GRAVITY = 0.5
PROJECTILE_SPEED = 20
BOSS_SPEED = 3
BOSS_DASH_SPEED = 20
ATTACK_RANGE_MELEE = 250 
ATTACK_RANGE_RANGED = 900 
COOLDOWN_ATTACK = 1000     


class Proyectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, floor_y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 215, 0)) 
        self.rect = self.image.get_rect(center=(x, y))
        self.floor_y = floor_y

        #Trayec
        dx = target_x - x
        dy = target_y - y
        angle = math.atan2(dy, dx)

        self.vel_x = math.cos(angle) * PROJECTILE_SPEED
        self.vel_y = math.sin(angle) * PROJECTILE_SPEED
        self.vel_y -= 8 # Parabola
        
        self.landed = False

    def update(self):
        if not self.landed:
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            self.vel_y += GRAVITY

            # Colision con el suelo
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

        # IA y Estado
        self.player = player_target
        self.projectile = None 
        self.ai_state = 'CHASE' 
        self.last_attack_time = 0

    def attack_hitbox(self):
        """Calcula el área de daño del golpe melee de Pancho."""
        
        if self.state != 'attack': 
            return None
        
        if self.current_frame_in_animation < 10 or self.current_frame_in_animation > 15:
            return None

        hitbox = pygame.Rect(0, 0, 150, 150)
        
        if self.direction == "right":
            hitbox.midleft = self.rect.midright
        else:
            hitbox.midright = self.rect.midleft
            
        hitbox.centery = self.rect.centery
        
        return hitbox

    def get_distance_to_player(self):
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        return math.sqrt(dx**2 + dy**2)
    
    def update(self):
        current_time = pygame.time.get_ticks()
        dist = self.get_distance_to_player()

        
        target_x_look = self.player.rect.centerx
        
        #mira a la moneda
        if self.ai_state == 'DASHING_TO_WEAPON' and self.projectile:
            target_x_look = self.projectile.rect.centerx

        if target_x_look < self.rect.centerx:
            self.direction = "left"
        else:
            self.direction = "right"


        
        #persigue
        if self.ai_state == 'CHASE':
            self.state = 'walk'
            
            can_attack = (current_time - self.last_attack_time > COOLDOWN_ATTACK)

            if dist < ATTACK_RANGE_MELEE and can_attack:
                self.ai_state = 'ATTACK_MELEE'
                self.current_frame_in_animation = 0 
            
            
            elif dist < ATTACK_RANGE_RANGED and dist > ATTACK_RANGE_MELEE and can_attack:
                self.ai_state = 'THROWING'
                self.current_frame_in_animation = 0 

            else:
                self.move_towards_target(self.player.rect.centerx, BOSS_SPEED)

        #mele
        elif self.ai_state == 'ATTACK_MELEE':
            self.state = 'attack'
            
            if self.animation_finished:
                
                self.last_attack_time = current_time
                self.ai_state = 'CHASE'

        #throw
        elif self.ai_state == 'THROWING':
            self.state = 'trowing' 
            
            if self.animation_finished:
                if self.projectile is None:
                    self.projectile = Proyectile(
                        self.rect.centerx, 
                        self.rect.centery, 
                        self.player.rect.centerx, 
                        self.player.rect.centery, 
                        self.floor_y
                    )
                self.ai_state = 'WAITING_PROJECTILE'

        elif self.ai_state == 'WAITING_PROJECTILE':
            self.state = 'idle'
            
            if self.projectile:
                self.projectile.update()
                if self.projectile.landed:
                    self.ai_state = 'DASHING_TO_WEAPON'
            else:
                self.ai_state = 'CHASE'

        # ir a moneda
        elif self.ai_state == 'DASHING_TO_WEAPON':
            self.state = 'walk' 
            
            if self.projectile:
                arrived = self.move_towards_target(self.projectile.rect.centerx, BOSS_DASH_SPEED)
                
                if arrived:
                    self.projectile = None 
                    self.last_attack_time = current_time 
                    self.ai_state = 'CHASE'
            else:
                self.ai_state = 'CHASE'


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

    def draw_projectile(self, surface, offset_x=0):
        if self.projectile:
            draw_rect = self.projectile.rect.move(-offset_x, 0)
            surface.blit(self.projectile.image, draw_rect)