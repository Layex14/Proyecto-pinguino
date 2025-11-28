import pygame 
import sys 
from configuracion import screenancho, screenalto, blanco
#entidades
from entidades.Entity import Player , Entity

from entidades.boss import BossPancho

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
            pygame.mixer.music.load('recursos/musica/Musicaboss.mp3')
            pygame.mixer.music.play(-1, fade_ms=2000)
            pygame.mixer.music.set_volume(0.4)
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
            floor_y=self.ground_level
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
        self.screen.fill((50, 50, 50))
        
        pygame.draw.rect(self.screen, self.floor_color, [0, self.ground_level, screenancho, screenalto - self.ground_level])
        pygame.draw.line(self.screen, (0,0,0), (0, self.ground_level), (screenancho, self.ground_level), 5)

        self.all_sprites.draw(self.screen)

        pygame.draw.rect(self.screen, (255, 0, 0), self.player.rect, 2)
        
        pygame.draw.rect(self.screen, (255, 0, 0), self.pancho.rect, 2)

        self.pancho.draw_projectile(self.screen)
