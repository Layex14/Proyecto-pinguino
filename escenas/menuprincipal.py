import pygame
from configuracion import screenancho, screenalto, FPS, titulo_juego, blanco

class MenuPrincipal:
    def __init__(self, screen):
        self.screen= screen
        self.next_scene = None


        try:
            self.fondo=pygame.image.load('recursos/imagenes/background1.png').convert_alpha()
            self.fondo = pygame.transform.scale(self.fondo, (screenancho, screenalto))
        except pygame.error:
            print("Error al cargar la imagen del menu.")
            self.fondo = None

        

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
