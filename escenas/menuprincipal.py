import pygame
import sys
from configuracion import screenancho, screenalto, FPS, titulo_juego, blanco
from utilidades.boton import Boton




class MenuPrincipal:
    def __init__(self, screen):
        self.screen= screen
        self.next_scene = None
#<<<Carga de recursos>>>
        
        try:
        #Fondo
            self.fondo=pygame.image.load('recursos/imagenes/background1.png').convert_alpha()
            self.fondo = pygame.transform.scale(self.fondo, (screenancho, screenalto))
        #Hoja de ls botones
            self.hoja_botones=pygame.image.load('recursos/imagenes/hojadebotones.png').convert_alpha()
        except pygame.error as e:
            print(f"error al cargar recursos: {e}")
            self.fondo=None
            sys.exit()

        try:
            pygame.mixer.music.load('recursos/musica/Main_menu.wav')
            pygame.mixer.music.play(-1, fade_ms=5000)
        except pygame.erros as e:
            print("error en la musica: {e}")

        #Variables de Play
        recorte_jugar = (800, 150, 550, 300) 
        pos_x_jugar = (screenancho // 2) - 100  # Centrado horizontalmente aprox
        pos_y_jugar = 250

        #Variables de exit
        recorte_salir = (1360, 880, 550, 300)
        pos_x_salir = (screenancho // 2) - 100
        pos_y_salir = 400

        #Recorte
        self.boton_jugar = Boton(pos_x_jugar, pos_y_jugar, self.hoja_botones, recorte_jugar, escala=0.3)
        self.boton_salir = Boton(pos_x_salir, pos_y_salir, self.hoja_botones, recorte_salir, escala=0.3)

        

    def handle_events(self, events):
        for event in events:
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_RETURN:
                    print('ta funcionando')
    
    def update(self):
        pass

    def draw(self):

        if self.fondo:
            self.screen.blit(self.fondo, (0,0))
        else:
            self.screen.fill(blanco)

        if self.boton_jugar.draw(self.screen):
            pygame.mixer.music.fadeout(1000)
            self.next_scene = "juego" 
        if self.boton_salir.draw(self.screen):
            pygame.quit()
            sys.exit()