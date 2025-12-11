import pygame
import math
from .Entity import Entity # Asumo que tu archivo se llama Entity.py

# --- CONSTANTES ---
GRAVITY = 0.5
PROJECTILE_SPEED = 20
BOSS_SPEED = 3
BOSS_DASH_SPEED = 20
ATTACK_RANGE_MELEE = 250   # Distancia para activar golpe
ATTACK_RANGE_RANGED = 900  # Distancia para activar lanzamiento
COOLDOWN_ATTACK = 1000     # Tiempo entre ataques

# ==========================================
# CLASE PROYECTIL
# ==========================================
class Proyectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, floor_y):
        super().__init__()
        # Visual simple para el proyectil (puedes cambiarlo por una imagen si tienes)
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 215, 0)) # Color Dorado
        self.rect = self.image.get_rect(center=(x, y))
        self.floor_y = floor_y

        # Cálculo de trayectoria
        dx = target_x - x
        dy = target_y - y
        angle = math.atan2(dy, dx)

        self.vel_x = math.cos(angle) * PROJECTILE_SPEED
        self.vel_y = math.sin(angle) * PROJECTILE_SPEED
        self.vel_y -= 8 # Arco hacia arriba para efecto parabólico
        
        self.landed = False

    def update(self):
        if not self.landed:
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            self.vel_y += GRAVITY

            # Colisión con el suelo
            if self.rect.bottom >= self.floor_y:
                self.rect.bottom = self.floor_y
                self.landed = True
                self.vel_x = 0
                self.vel_y = 0

# ==========================================
# CLASE BOSS PANCHO
# ==========================================
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

    def get_distance_to_player(self):
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        return math.sqrt(dx**2 + dy**2)
    
    def update(self):
        current_time = pygame.time.get_ticks()
        dist = self.get_distance_to_player()

        # -----------------------------------------------------------
        # 1. ORIENTACIÓN (Mirar al jugador o al arma)
        # -----------------------------------------------------------
        target_x_look = self.player.rect.centerx
        
        # Si está corriendo por el arma, mira hacia el arma
        if self.ai_state == 'DASHING_TO_WEAPON' and self.projectile:
            target_x_look = self.projectile.rect.centerx

        if target_x_look < self.rect.centerx:
            self.direction = "left"
        else:
            self.direction = "right"

        # -----------------------------------------------------------
        # 2. MÁQUINA DE ESTADOS (IA)
        # -----------------------------------------------------------
        
        # --- ESTADO: PERSEGUIR ---
        if self.ai_state == 'CHASE':
            self.state = 'walk'
            
            # Verificamos si ya pasó el tiempo de cooldown
            can_attack = (current_time - self.last_attack_time > COOLDOWN_ATTACK)

            # A. Rango Melee (Ataque cercano)
            if dist < ATTACK_RANGE_MELEE and can_attack:
                self.ai_state = 'ATTACK_MELEE'
                self.current_frame_in_animation = 0 # Reiniciar animación visual
            
            # B. Rango Lejano (Lanzar proyectil)
            elif dist < ATTACK_RANGE_RANGED and dist > ATTACK_RANGE_MELEE and can_attack:
                self.ai_state = 'THROWING'
                self.current_frame_in_animation = 0 # Reiniciar animación visual

            # C. Moverse hacia el jugador
            else:
                self.move_towards_target(self.player.rect.centerx, BOSS_SPEED)

        # --- ESTADO: ATAQUE MELEE (GOLPE) ---
        elif self.ai_state == 'ATTACK_MELEE':
            self.state = 'attack' # Usa la nueva animación 'attack'
            
            # Esperar a que termine la animación
            if self.animation_finished:
                # Aquí podrías generar el daño si no usas colisiones por frame
                # self.check_melee_hit() 
                
                self.last_attack_time = current_time
                self.ai_state = 'CHASE'

        # --- ESTADO: PREPARANDO LANZAMIENTO (Animación) ---
        elif self.ai_state == 'THROWING':
            self.state = 'trowing' # Usa la nueva animación 'trowing'
            
            # ¡MAGIA AQUÍ! Solo dispara cuando la animación termina
            if self.animation_finished:
                if self.projectile is None:
                    # Instanciar el proyectil
                    self.projectile = Proyectile(
                        self.rect.centerx, 
                        self.rect.centery, 
                        self.player.rect.centerx, 
                        self.player.rect.centery, 
                        self.floor_y
                    )
                # Pasar a estado de espera (ver el hacha volar)
                self.ai_state = 'WAITING_PROJECTILE'

        # --- ESTADO: ESPERANDO QUE EL PROYECTIL CAIGA ---
        elif self.ai_state == 'WAITING_PROJECTILE':
            self.state = 'idle'
            
            if self.projectile:
                self.projectile.update()
                # Si toca el suelo, corremos a buscarla
                if self.projectile.landed:
                    self.ai_state = 'DASHING_TO_WEAPON'
            else:
                # Si el proyectil desapareció por error, volver a perseguir
                self.ai_state = 'CHASE'

        # --- ESTADO: RECUPERAR ARMA ---
        elif self.ai_state == 'DASHING_TO_WEAPON':
            self.state = 'walk' # O 'dash' si tienes animación de correr rápido
            
            if self.projectile:
                # Correr rápido hacia el proyectil
                arrived = self.move_towards_target(self.projectile.rect.centerx, BOSS_DASH_SPEED)
                
                if arrived:
                    self.projectile = None # "Recoge" el arma
                    self.last_attack_time = current_time # Reinicia el cooldown
                    self.ai_state = 'CHASE'
            else:
                self.ai_state = 'CHASE'

        # -----------------------------------------------------------
        # 3. FÍSICA Y ACTUALIZACIÓN BASE
        # -----------------------------------------------------------
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