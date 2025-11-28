import pygame

class Entity(pygame.sprite.Sprite): 
    # acepta un diccionario (visual_config)
    def __init__(self, name, spritesheet, visual_config, animation_data, default_animation,):
        
        super().__init__() 
        
        self.name = name
        self.spritesheet = spritesheet
        self.animation_data = animation_data
        self.state = default_animation
        self.previous_state = None
        
        self.direction = "right"
        self.is_attacking = False
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_window_ms = 400
    
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
        
        # Control de animacion
        self.last_update = pygame.time.get_ticks() 

        self.start_frame_index, self.animation_duration = self.animation_data[self.state]

        self.current_frame_in_animation = 0 
        

        initial_spritesheet_index = self.start_frame_index + self.current_frame_in_animation
        
        # Creacion de la primera imagen y el rect 
        self.image = self.get_image(initial_spritesheet_index)
        self.rect = self.image.get_rect() 
        
        #posicion inicial
        self.rect.x = visual_config["start_x"]
        self.rect.y = visual_config["start_y"]

            #extraccion de imagen
    def get_image(self, index):
        row = index // self.columns
        col = index % self.columns
        
        sheet_x = col*self.frame_width
        sheet_y = row*self.frame_height
        
        full_frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA).convert_alpha()
        full_frame.blit(self.spritesheet, (0, 0), 
                        (sheet_x, sheet_y, self.frame_width, self.frame_height))
        
        # Recorte y escalado
        if self.crop_bounds:
            left, top, right, bottom = self.crop_bounds
            crop_width = self.frame_width - left - right
            crop_height = self.frame_height - top - bottom
            
            cropped_frame = pygame.Surface((crop_width, crop_height), pygame.SRCALPHA).convert_alpha()
            cropped_frame.blit(full_frame, (0, 0), (left, top, crop_width, crop_height))
            
            scaled_width = int(crop_width * self.scale)
            scaled_height = int(crop_height * self.scale)
            scaled_frame = pygame.transform.scale(cropped_frame, (scaled_width, scaled_height))
            return scaled_frame
        else:
            scaled_width = int(self.frame_width * self.scale)
            scaled_height = int(self.frame_height * self.scale)
            scaled_frame = pygame.transform.scale(full_frame, (scaled_width, scaled_height))
            return scaled_frame

    # Actualiza la nimacion
    def update(self):
        current_time = pygame.time.get_ticks()
        self.check_state_change() 

        if current_time - self.last_update >= self.cooldown:
            self.last_update = current_time 
            self.current_frame_in_animation += 1
            
            if self.current_frame_in_animation >= self.animation_duration:
                self.current_frame_in_animation = 0 
                
            spritesheet_index = self.start_frame_index + self.current_frame_in_animation
            
            self.image = self.get_image(spritesheet_index)
            self.compensate() 
    
    def compensate(self):
        current_midbottom = self.rect.midbottom
        
        should_flip = (self.direction == "left")
        self.image = pygame.transform.flip(self.image, should_flip, False)
        
        self.rect = self.image.get_rect()
        self.rect.midbottom = current_midbottom
        
    def check_state_change(self):
        if self.state != self.previous_state:
            
            try:
                self.start_frame_index, self.animation_duration = self.animation_data[self.state]
            except KeyError:
                print(f"Error: La animación '{self.state}' no existe en animation_data.")
                self.state = self.previous_state if self.previous_state else 'idle'
                return

            self.current_frame_in_animation = 0
            self.last_update = pygame.time.get_ticks() 
            
            spritesheet_index = self.start_frame_index 
            self.image = self.get_image(spritesheet_index)
            
            self.compensate()
            self.previous_state = self.state
    
class Player(Entity):
    def __init__(self, name, spritesheet, visual_config, animation_data, default_animation, floor_y):
        super().__init__(name, spritesheet, visual_config, animation_data, default_animation)
        

        self.floor_y = floor_y

    
        #Variables de Salto
        self.on_ground = True      
        self.jump_speed = -20      
        self.vertical_momentum = 0 
        self.gravity = 1           
        self.jumping = False
        
        #Variables de dash
        self.dashing = False 
        self.dash_duration_ms = 500 
        self.dash_timer = 0         
        self.dash_speed = 20
        
        self.is_moving = False 

    def apply_gravity_and_jump(self):
        """Aplica la gravedad y el movimiento vertical."""
        
        #Aplicar Gravedad
        if not self.on_ground:
            self.vertical_momentum += self.gravity
            
        #Limitar la Velocidad
        if self.vertical_momentum > 15: 
            self.vertical_momentum = 15
            
        #Aplicar Movimiento
        self.rect.y += self.vertical_momentum
        
        #Coli del eje Y
        if self.rect.bottom >= self.floor_y:
            self.rect.bottom = self.floor_y
            self.on_ground = True
            self.jumping = False
            self.vertical_momentum = 0
            
            
    def Running_player(self, keys):
        self.keys = keys
        self.is_moving = False
        
        # Bloquea movimiento si está atacando o dashando
        if self.is_attacking or self.dashing:
            return 

        #Movimiento Lateral
        movement_applied = False

        if keys[pygame.K_LEFT]:
            self.direction = "left"
            self.rect.x -= self.speed
            movement_applied = True
            
        if keys[pygame.K_RIGHT]:
            self.direction = "right"
            self.rect.x += self.speed
            movement_applied = True
            
        #Lógica de Estado
        if self.on_ground: 
            if movement_applied:
                self.state = "walk"
                self.is_moving = True
            else:
                self.state = "idle"
        else:
            self.is_moving = movement_applied 

    def player_attack(self, event): 
        """Registra la pulsación de la tecla para iniciar o encadenar el combo."""
        
        if event.type != pygame.KEYDOWN:
            return
            
        if event.key == pygame.K_x:
            current_time = pygame.time.get_ticks()

            #wombo combo
            if self.combo_timer > current_time and self.combo_count < 3: 
                self.combo_count += 1
                
            # ataque 1
            elif not self.is_attacking:
                self.combo_count = 1
                self.is_attacking = True
                self.combo_timer = current_time + self.combo_window_ms
                
                self.state = "attack_1"
                self.current_frame_in_animation = 0 
                
                # Movimiento de avance
                if self.direction == "left":
                    self.rect.x -= 6
                else:
                    self.rect.x += 6

    def player_jump(self, event):
        if self.is_attacking or self.dashing:
            return
        
        
        if self.on_ground and event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            self.on_ground = False
            self.jumping = True
            self.state = 'jump'
            self.vertical_momentum = self.jump_speed 

    def player_dashing(self, event):
        """Registra la pulsación de la tecla para iniciar el Dash."""
        
        if self.is_attacking or self.dashing:
            return
            
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
            current_time = pygame.time.get_ticks()
            
            self.dashing = True
            self.state = 'dash'
            self.dash_timer = current_time + self.dash_duration_ms
            

    def update(self):
        current_time = pygame.time.get_ticks()

        
        self.apply_gravity_and_jump() 
        
        if self.dashing:
            
            if current_time < self.dash_timer:
                # Movimiento horizontal
                if self.direction == "right":
                    self.rect.x += self.dash_speed
                else:
                    self.rect.x -= self.dash_speed
            else:
                self.dashing = False
                
                if not self.on_ground:
                    self.state = 'jump' 
                elif self.is_moving:
                    self.state = 'walk'
                else:
                    self.state = 'idle'
                
        
        elif self.is_attacking:
            
            if self.current_frame_in_animation >= self.animation_duration - 1:
                
                # wombo combo 1->2 o 2->3
                if self.combo_count >= 2 and self.state == "attack_1":
                    self.state = "attack_2" 
                    self.current_frame_in_animation = 0 
                    self.last_update = current_time 
                    self.combo_timer = current_time + self.combo_window_ms
                elif self.combo_count >= 3 and self.state == "attack_2":
                    self.state = "attack_3" 
                    self.current_frame_in_animation = 0
                    self.last_update = current_time
                else:
                    self.is_attacking = False
                    self.combo_count = 0
                    if not self.on_ground:
                        self.state = 'jump' 
                    else:
                        self.state = 'idle'

        elif current_time > self.combo_timer:
            self.combo_count = 0
            
        elif not self.on_ground:
            self.state = 'jump' 
            
        super().update()