import pygame 
import sys 
from configuracion import screenancho, screenalto, blanco
#entidades
from entidades.Entity import Player, Entity
#diccionario
from entidades.pancho_config import player_config, player_definitions, pancho_config, pancho_definitions

class Juego:
    def __init__(self, screen):
        self.screen=screen
        self.next_scene=None

        self.ground_level = 420 
        self.floor_color = (43, 25, 40)
        
        try:
            self.malla_jugador=pygame.image.load("recursos/imagenes/player_sprites.png").convert_alpha()
            self.malla_pancho=pygame.image.load("recursos/imagenes/pancho_sprites.png").convert_alpha()
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
            default_animation="idle"
        )

        self.all_sprites.add(self.player)
        self.pancho=Entity(
            name="pancho",
            spritesheet=self.malla_pancho,
            visual_config=pancho_config,
            animation_data=pancho_definitions,
            default_animation="idle"
        )

        self.all_sprites.add(self.pancho)
        self.enemies.add(self.pancho)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    self.next_scene="menu_principal"
                    

                self.player.player_attack(event)  # Tecla X
                self.player.player_jump(event)    # Tecla C
                self.player.player_dashing(event) # Tecla Z


    def update(self):
        keys=pygame.key.get_pressed()

        self.player.Running_player(keys)
        
        self.all_sprites.update()

    def draw(self):
        self.screen.fill((50, 50, 50)) # Fondo gris oscuro

        # --- DIBUJAR SUELO ---
        # Dibujamos el suelo desde el nivel 600 hacia abajo
        pygame.draw.rect(self.screen, self.floor_color, [0, self.ground_level, screenancho, screenalto - self.ground_level])
        # Línea de borde
        pygame.draw.line(self.screen, (0,0,0), (0, self.ground_level), (screenancho, self.ground_level), 5)

        # Dibujar Sprites
        self.all_sprites.draw(self.screen)