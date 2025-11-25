import pygame

class Character(pygame.sprite.Sprite): 
    def __init__(self, name, health, speed, spritesheet, frame_width, frame_height, scale, columns, animation_data, default_animation='idle'):
        # Inicializa la clase Sprite de Pygame
        super().__init__() 
        
        self.name = name
        self.health = health
        self.speed = speed
        self.spritesheet = spritesheet
        
        # Nuevos atributos de configuración visual
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.scale = scale
        self.columns = columns
        self.animation_data = animation_data

        start_frame, duration_frame = self.animation_data[default_animation]
        # Inicializamos la primera imagen (frame 0)
        self.current_frame_index = start_frame
        self.animation_duration = duration_frame
        
        # Creamos el rect (posición y tamaño) a partir de la imagen
        self.image = self.get_image(self.current_frame_index)
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0) # Posición inicial por defecto

    # Simplificamos get_image para que use los atributos de la clase
    def get_image(self, index):
        """Extrae un frame específico del spritesheet."""
        row = index // self.columns
        col = index % self.columns
        
        # Crea una superficie transparente para el frame
        image_frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA).convert_alpha()

        # Dibuja la parte del spritesheet en la nueva superficie
        image_frame.blit(self.spritesheet, (0, 0), 
                         (col * self.frame_width, 
                          row * self.frame_height, 
                        self.frame_width, 
                        self.frame_height))

        # Escala la imagen al tamaño deseado
        image_frame = pygame.transform.scale(image_frame, 
                                             (self.frame_width * self.scale, 
                                              self.frame_height * self.scale))

        return image_frame

    def update(self):
        
        pass