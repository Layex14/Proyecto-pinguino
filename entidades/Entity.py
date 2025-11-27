import pygame

# Heredar de pygame.sprite.Sprite es la mejor práctica
class Entity(pygame.sprite.Sprite): 
    # El constructor ahora acepta un diccionario (visual_config)
    def __init__(self, name, spritesheet, visual_config, animation_data, default_animation):
        # Inicializa la clase Sprite de Pygame
        super().__init__() 
        
        self.name = name
        self.spritesheet = spritesheet
        self.animation_data = animation_data
        self.state = default_animation
        self.previous_state = None
        
        self.direction = "right"

    
        # --- Desempaquetado del Diccionario de Configuración ---
        self.frame_width = visual_config["frame_width"]
        self.frame_height = visual_config["frame_height"]
        self.scale = visual_config["scale"]
        self.columns = visual_config["columns"]
        self.cooldown = visual_config["cooldown"]
        self.speed = visual_config["speed"]
        
        if "crop_bounds" in visual_config:
            self.crop_bounds = visual_config["crop_bounds"]
        else:
            self.crop_bounds = None
        
        # Control de animación
        self.last_update = pygame.time.get_ticks() 

        # El índice inicial del frame de la animación actual (ej. 8 para "walk")
        self.start_frame_index, self.animation_duration = self.animation_data[self.state]
        # El frame actual DENTRO de la animación (0 a duration-1)
        self.current_frame_in_animation = 0 
        
        # Calculamos el índice real para la imagen inicial
        initial_spritesheet_index = self.start_frame_index + self.current_frame_in_animation
        
        # Creamos la primera imagen y el rect
        self.image = self.get_image(initial_spritesheet_index)
        self.rect = self.image.get_rect()

        self.rect.x = visual_config["start_x"]
        self.rect.y = visual_config["start_y"]
    # --- Método de Extracción de Imagen ---
    def get_image(self, index):
        row = index // self.columns
        col = index % self.columns
        
        sheet_x = col*self.frame_width
        sheet_y = row*self.frame_height
        # Crea una superficie para el frame completo
        full_frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA).convert_alpha()
        full_frame.blit(self.spritesheet, (0, 0), 
                    (sheet_x, sheet_y, self.frame_width, self.frame_height))
        
        # Recorta si hay configuración de recorte
        if self.crop_bounds:
            left, top, right, bottom = self.crop_bounds
            crop_width = self.frame_width - left - right
            crop_height = self.frame_height - top - bottom
            
            # Crea superficie recortada
            cropped_frame = pygame.Surface((crop_width, crop_height), pygame.SRCALPHA).convert_alpha()
            cropped_frame.blit(full_frame, (0, 0), (left, top, crop_width, crop_height))
            
            # Escala la imagen recortada
            scaled_width = int(crop_width * self.scale)
            scaled_height = int(crop_height * self.scale)
            scaled_frame = pygame.transform.scale(cropped_frame, (scaled_width, scaled_height))
            return scaled_frame
        else:
            # Escala la imagen completa (comportamiento original)
            scaled_width = int(self.frame_width * self.scale)
            scaled_height = int(self.frame_height * self.scale)
            scaled_frame = pygame.transform.scale(full_frame, (scaled_width, scaled_height))
            return scaled_frame

    # --- Método de Actualización de Animación (Corregido) ---
    def update(self):
        current_time = pygame.time.get_ticks()
        self.check_state_change()

        # 1. Comprobar si el tiempo de espera (cooldown) ha pasado
        if current_time - self.last_update >= self.cooldown:
            self.last_update = current_time # Reinicia el temporizador
            
            # 2. Avanzar el frame dentro de la duración de la animación
            self.current_frame_in_animation += 1
            
            # 3. Comprobar si se ha llegado al final de la animación (hacer un bucle)
            if self.current_frame_in_animation >= self.animation_duration:
                self.current_frame_in_animation = 0 
            
            # 4. Calcular el índice real del spritesheet
            spritesheet_index = self.start_frame_index + self.current_frame_in_animation
            
            # 5. Actualizar la imagen y el rectángulo
            self.image = self.get_image(spritesheet_index)
            
            self.compensate()

            current_midbottom = self.rect.midbottom 
            self.rect = self.image.get_rect()
            self.rect.midbottom = current_midbottom
    
    def compensate(self):
        # Guarda la posición actual basada en midbottom
        current_midbottom = self.rect.midbottom
        
        # Aplica el flip
        should_flip = (self.direction == "left")
        self.image = pygame.transform.flip(self.image, should_flip, False)
        
        # Reajusta la posición
        self.rect = self.image.get_rect()
        self.rect.midbottom = current_midbottom
    def check_state_change(self):
        if self.state != self.previous_state:
            # 1. Obtener la nueva información de la animación
            self.start_frame_index, self.animation_duration = self.animation_data[self.state]
            
            # 2. Reiniciar el frame y el temporizador
            self.current_frame_in_animation = 0
            self.last_update = pygame.time.get_ticks() # Para que el cambio sea instantáneo
            
            # 3. Dibujar el primer frame de la nueva animación inmediatamente
            spritesheet_index = self.start_frame_index 
            self.image = self.get_image(spritesheet_index)
            
            self.compensate()
            # 4. Actualizar el estado anterior
            self.previous_state = self.state
    
class Player(Entity):
    def __init__(self, name, spritesheet, visual_config, animation_data, default_animation):
        super().__init__(name, spritesheet, visual_config, animation_data, default_animation)
    def Running_player(self,keys):
        self.keys = keys
        self.is_moving = False
        if keys[pygame.K_LEFT]:
            self.direction = "left"
            self.rect.x -= self.speed
            self.state = "walk"
            self.is_moving = True
            
        if keys[pygame.K_RIGHT]:
            self.direction = "right"
            self.rect.x += self.speed
            self.state = "walk"
            self.is_moving = True
            
        if not self.is_moving:
            self.state = "idle"
        
    def player_attack(self, event):
        self.event = event
        is_attaking = False
        if self.event.key == pygame.K_x:
            if not is_attaking:
                self.state = "general_attack"
                self.is_attaking = True
                
                self.is_moving = False
                if self.direction == "left":
                    self.rect.x -= 6
                else:
                    self.rect.x += 6
           # print("ashu")




