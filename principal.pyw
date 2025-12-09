import pygame
import sys
from configuracion import screenancho, screenalto, FPS, titulo_juego
from escenas.menuprincipal import MenuPrincipal 
from escenas.Juego import Juego


class JuegoManager:
    def __init__(self):

        pygame.init()
        #creador de la pantalla
        self.screen = pygame.display.set_mode((screenancho, screenalto))
        pygame.display.set_caption(titulo_juego)

        self.clock = pygame.time.Clock()

        #Gestor de escenario    
        self.scenes={
            "menu_principal": MenuPrincipal,
                "juego": Juego
        }


        self.current_scene_name = "menu_principal"
        self.current_scene = self.scenes[self.current_scene_name](self.screen)


    #Crea el bucle del programa
    def run(self):
        running = True
        while running:

            self.clock.tick(FPS)
        
            evento=pygame.event.get()

            for event in evento:
                if event.type == pygame.QUIT:
                    running = False

            self.current_scene.handle_events(evento)

            self.current_scene.update()

            self.current_scene.draw()

            if self.current_scene.next_scene:
                next_scene_name = self.current_scene.next_scene
                if next_scene_name in self.scenes:
                    self.current_scene = self.scenes[next_scene_name](self.screen)
                    self.current_scene_name = next_scene_name

            pygame.display.flip()
            


        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    juego = JuegoManager()
    juego.run()
