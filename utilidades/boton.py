import pygame

#Plantilla de botones pal menu principal

class Boton:
    def __init__(self, x, y, hoja_sprites, rect_recorte, escala=1):


        #Recorta la imagen (creo)
        imagen_recortada=hoja_sprites.subsurface(pygame.Rect(rect_recorte))


        #Escala la imagen
        ancho_original=imagen_recortada.get_width()
        largo_original=imagen_recortada.get_height()

        nuevo_ancho=int(ancho_original*escala)
        nuevo_largo=int(largo_original*escala)


        #Eacala la imagen final
        self.imagen=pygame.transform.scale(imagen_recortada, (nuevo_ancho, nuevo_largo))

        #Crea el rectangulo
        self.rect=self.imagen.get_rect()
        self.rect.topleft=(x, y)

        #Estado del botoncinho
        self.presionado=False

    def draw(self, screen):
        accion=False
        poscicion_de_mouse=pygame.mouse.get_pos()

        if self.rect.collidepoint(poscicion_de_mouse):
            if pygame.mouse.get_pressed()[0] == 1 and self.presionado == False:
                self.presionado=True
                accion=True

        if pygame.mouse.get_pressed()[0]==0:
            self.presionado=False

        screen.blit(self.imagen, (self.rect.x, self.rect.y))

        return accion






