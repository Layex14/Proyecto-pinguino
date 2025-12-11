import pygame 
import sys 
from configuracion import screenancho, screenalto, blanco
#entidades
from entidades.Entity import Player , Entity

from entidades.boss import BossPancho

#diccionario
from entidades.pancho_config import player_config, player_definitions, pancho_config, pancho_definitions

#Camara
from utilidades.camera import Camera

class Juego:
    def __init__(self, screen):
        self.screen=screen
        self.next_scene=None

        self.game_over = False
        self.victoria = False

        self.font_grande = pygame.font.Font(None, 74) 
        self.font_chica = pygame.font.Font(None, 36)

        self.ground_level = 127*4 
        self.floor_color = (43, 25, 40)
        
        self.showing_intro = True
        self.intro_stage = "fade_in" # Estados: fade_in, hold, fade_out
        self.intro_alpha = 0         # Transparencia (0 invisible, 255 visible)
        self.intro_timer = pygame.time.get_ticks()
        
        
        self.DURATION_FADE_IN = 1000
        self.DURATION_HOLD = 1000    # Tiempo que el texto se queda quieto
        self.DURATION_FADE_OUT = 1000
        
        
        try:
            self.font_boss_big = pygame.font.SysFont("georgia", 100, bold=True)
            self.font_boss_sub = pygame.font.SysFont("georgia", 40, italic=True)
        except:
            self.font_boss_big = pygame.font.SysFont(None, 100)
            self.font_boss_sub = pygame.font.SysFont(None, 40)
            
        # Renderizamos los textos una sola vez para optimizar
        self.text_name = self.font_boss_big.render("PANCHITO", True, (255, 255, 255))
        self.text_sub = self.font_boss_sub.render("EL ANTILOPE SABLE", True, (200, 200, 200))
        
        # Centramos los textos en la pantalla
        self.rect_name = self.text_name.get_rect(center=(screenancho//2, screenalto//2 - 50))
        self.rect_sub = self.text_sub.get_rect(center=(screenancho//2, screenalto//2 + 20))
        # carga de recursos

        try:
            self.escenario = pygame.image.load('recursos/imagenes/escenario.png').convert_alpha()
            
            self.malla_jugador=pygame.image.load("recursos/imagenes/player_sprites.png").convert_alpha()
            self.malla_pancho=pygame.image.load("recursos/imagenes/pancho_sprites.png").convert_alpha()
            pygame.mixer.music.load('recursos/musica/Musicaboss.mp3')
            pygame.mixer.music.play(-1, fade_ms=2000)
            pygame.mixer.music.set_volume(0.4)

            self.ancho_escenario = self.escenario.get_width()
        except pygame.error as e:
            print("error de sprite: {e}")
            sys.exit()

        self.all_sprites=pygame.sprite.Group()
        self.enemies=pygame.sprite.Group()


        self.player= Player(
            name="Heroe",
            spritesheet=self.malla_jugador,
            visual_config=player_config,
            animation_data=player_definitions,
            default_animation="idle",
            floor_y=self.ground_level,
            limit_rigth=self.ancho_escenario-30
        )
        self.all_sprites.add(self.player)


        self.pancho = BossPancho(
            x=1000, 
            y=self.ground_level, 
            floor_y=self.ground_level, 
            player_target=self.player, 
            spritesheet=self.malla_pancho,
            visual_config=pancho_config,
            animation_data=pancho_definitions
        )
        self.all_sprites.add(self.pancho)

        self.enemies.add(self.pancho)

        self.camera = Camera(
            who=self.player,
            ancho_pantalla= screenancho,
            ancho_escenario=self.ancho_escenario
        )

    #Procesa eventos

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    self.next_scene="menu_principal"
                if self.game_over:
                    if event.key == pygame.K_RETURN: 
                        if self.victoria:
                            self.next_scene = "menu_principal" 
                        else:
                            self.next_scene = "juego" 
                    return

                self.player.player_attack(event)  # Tecla Z
                self.player.player_jump(event)    # Tecla X
                self.player.player_dashing(event) # Tecla C

    #Cerebro de Juego
    def update(self):
        current_time = pygame.time.get_ticks()
        #logic de intro
        if self.showing_intro:
            if self.intro_stage == "fade_in":
                progress = (current_time - self.intro_timer) / self.DURATION_FADE_IN
                if progress >= 1:
                    self.intro_alpha = 255
                    self.intro_stage = "hold"
                    self.intro_timer = current_time 
                else:
                    self.intro_alpha = int(progress * 255)

            elif self.intro_stage == "hold":
                self.intro_alpha = 255
                if current_time - self.intro_timer > self.DURATION_HOLD:
                    self.intro_stage = "fade_out"
                    self.intro_timer = current_time 

            elif self.intro_stage == "fade_out":
                progress = (current_time - self.intro_timer) / self.DURATION_FADE_OUT
                if progress >= 1:
                    self.intro_alpha = 0
                    self.showing_intro = False 
                else:
                    self.intro_alpha = 255 - int(progress * 255)
            
            self.camera.update()
            return 



        if self.game_over:
            return

        keys=pygame.key.get_pressed()

        self.player.Running_player(keys)
        
        self.all_sprites.update()

        self.camera.update()

        if self.player.is_attacking:
            attack_box = self.player.attack_hitbox()
            if attack_box and attack_box.colliderect(self.pancho.rect):
                self.pancho.damage(5)
        
        if self.pancho.state == 'attack': 
            boss_hitbox = self.pancho.attack_hitbox()
            if boss_hitbox:
                if boss_hitbox.colliderect(self.player.rect):
                    if self.player.damage(20):

                        # Empuja
                        if self.pancho.rect.centerx < self.player.rect.centerx:
                            self.player.rect.x += 900 #der
                        else:
                            self.player.rect.x -= 900 #isq

        
        if self.pancho.projectile and not self.pancho.projectile.landed:

            moneda_destruida = False 

            if self.player.is_attacking:
                sword_hitbox = self.player.attack_hitbox()
                #parry (HAZLO KEVIN POR EL BENDITO)
                if sword_hitbox:
                    if sword_hitbox.colliderect(self.pancho.projectile.rect):
                        
                        self.pancho.projectile = None
                        moneda_destruida = True
            if not moneda_destruida and self.pancho.projectile:
                if self.pancho.projectile.rect.colliderect(self.player.rect):
                    if self.player.damage(15): 
                        self.pancho.projectile = None


        if self.pancho.hp <= 0:
            self.game_over = True
            self.victoria = True
            pygame.mixer.music.stop()

        if self.player.hp <= 0:
            self.game_over = True
            self.victoria = False
            pygame.mixer.music.stop()


    #Barras de vida         
    def draw_health_bar(self, entity, x, y, width, height, color):
        """Función auxiliar para dibujar barras de vida."""
        
        pygame.draw.rect(self.screen, (60, 60, 60), (x, y, width, height))
        
        
        ratio = entity.hp / entity.max_hp
        pygame.draw.rect(self.screen, color, (x, y, width * ratio, height))
        
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, width, height), 2)


    def draw_text_with_alpha(self, surface, text_img, rect, alpha):
        """Función auxiliar para dibujar texto transparente"""
        # Creamos una copia de la imagen del texto para ponerle alpha
        temp_surface = text_img.copy()
        temp_surface.set_alpha(alpha)
        surface.blit(temp_surface, rect)

    #Dibujos de hitbox u otro
    def draw(self):

        offset = self.camera.offset_x

        if self.escenario:
            self.screen.blit(self.escenario, (-offset,0))
        else:
            self.screen.fill(blanco)

        for sprite in self.all_sprites: 
            image_rect = sprite.image.get_rect()
            
            image_rect.midbottom = sprite.rect.midbottom 
            
            ajuste_visual = sprite.image_offset_x

            if sprite.direction == "left":
                ajuste_visual = -ajuste_visual

            image_rect.x += ajuste_visual

            draw_pos = image_rect.move(-offset, 9)
            
            self.screen.blit(sprite.image, draw_pos)
            
            debug_rect = sprite.rect.move(-offset, 0)
            pygame.draw.rect(self.screen, (255, 0, 0), debug_rect, 2)
            
            # Hitbox ataque
            if hasattr(sprite, 'is_attacking') and sprite.is_attacking:
                hitbox = sprite.attack_hitbox()
                if hitbox:
                    hitbox_moved = hitbox.move(-offset, 0)
                    pygame.draw.rect(self.screen, (255, 0, 0), hitbox_moved, 2)

            if sprite == self.pancho and sprite.state == 'attack':
                hitbox = sprite.attack_hitbox()
                if hitbox:
                    hitbox_moved = hitbox.move(-offset, 0)
                    pygame.draw.rect(self.screen, (255, 0, 0), hitbox_moved, 2)

        #Proyectil de pancho
        self.pancho.draw_projectile(self.screen, offset)

        self.draw_health_bar(self.player, 20, 20, 200, 20, (0, 255, 0))

        if not self.pancho.is_dead:
             self.draw_health_bar(self.pancho, screenancho // 2 - 250, 650, 500, 25, (255, 0, 0))

        if self.showing_intro:
            
            dark_overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            dark_overlay.fill((0, 0, 0))
            dark_overlay.set_alpha(100) # Oscuridad parcial
            self.screen.blit(dark_overlay, (0, 0))

            # Dibujar Título y Subtítulo
            self.draw_text_with_alpha(self.screen, self.text_name, self.rect_name, self.intro_alpha)
            self.draw_text_with_alpha(self.screen, self.text_sub, self.rect_sub, self.intro_alpha)
            
            
            if self.intro_alpha > 0:
                line_width = 400
                center_x = self.screen.get_width() // 2
                line_y = self.rect_name.bottom - 10
                # Línea que se desvanece con el texto
                s = pygame.Surface((line_width, 2))
                s.fill((255, 255, 255))
                s.set_alpha(self.intro_alpha)
                self.screen.blit(s, (center_x - line_width//2, line_y))

        if self.game_over:
            # Capa oscura
            s = pygame.Surface((screenancho, screenalto))  
            s.set_alpha(128)                
            s.fill((0,0,0))           
            self.screen.blit(s, (0,0))
            
            # Textos
            if self.victoria:
                texto = "¡VICTORIA (el 7 profe)!"
                color = (0, 255, 0)
                instruccion = "Presiona ENTER para volver al Menú"
            else:
                texto = "DERROTA"
                color = (255, 0, 0)
                instruccion = "Presiona ENTER para Reiniciar"
            
            # Variables locales temporales para renderizar
            cartel = self.font_grande.render(texto, True, color)
            subtitulo = self.font_chica.render(instruccion, True, (255, 255, 255))

            # Centrar
            rect_cartel = cartel.get_rect(center=(screenancho//2, screenalto//2 - 50))
            rect_sub = subtitulo.get_rect(center=(screenancho//2, screenalto//2 + 20))

            self.screen.blit(cartel, rect_cartel)
            self.screen.blit(subtitulo, rect_sub)
