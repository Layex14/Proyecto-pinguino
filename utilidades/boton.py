import pygame

#Plantilla de botones pal menu principal

class Boton:
    def __init__(self, x, y, hoja_sprites, rect_recorte, escala=1):


        #Recorta la imagen (creo)
        imagen_recortada=hoja_sprites.surface(pygame.Rec(rect_recorte))

        ancho_original=imagen_recortada.get_width()
        largo_original=imagen_recortada.get_large()


