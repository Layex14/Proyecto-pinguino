import pygame

class Entity(pygame.sprite.Sprite): 
    def __init__(self, name, spritesheet, visual_config, animation_data, default_animation,):
        
        super().__init__() 
        
        ### obtenemos valores de pancho_config
        

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
        self.attack_cooldown = visual_config.get("attack_cooldown", 50)
        self.speed = visual_config["speed"]
        self.hitbox_width, self.hitbox_height= visual_config.get("hitbox_size")

        self.max_hp = visual_config.get("hp",100)
        self.hp = self.max_hp

        self.last_hit_time = 0
        self.invulnerable_duration = 1000 
        self.is_dead = False


        if "crop_bounds" in visual_config:
            self.crop_bounds = visual_config["crop_bounds"]
        else:
            self.crop_bounds = None
        
        # Controla de animacion
        self.last_update = pygame.time.get_ticks() 

        self.start_frame_index, self.animation_duration = self.animation_data[self.state]

        self.current_frame_in_animation = 0 
        self.animation_finished = False

        initial_spritesheet_index = self.start_frame_index + self.current_frame_in_animation
        
        # Creacion de la primera imagen y el rect 
        self.image = self.get_image(initial_spritesheet_index)

        self.rect=pygame.Rect(0, 0, self.hitbox_width, self.hitbox_height)

        self.image_offset_x = visual_config.get("image_offset_x", 0)

        #posicion inicial
        self.rect.x = visual_config["start_x"]
        self.rect.y = visual_config["start_y"]
    

    def attack_hitbox(self):

        ### Detecta ataques de PJ o panchito
        if not self.is_attacking:
            return None
        hitbox = pygame.Rect(0, 0, 140, 110)
        if self.direction == "right":
            hitbox.midleft = self.rect.midright
        else:
            hitbox.midright = self.rect.midleft
            
        hitbox.centery = self.rect.centery
        return hitbox

    def damage(self, amount):

        #### Generador de daño

        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_hit_time > self.invulnerable_duration:
            self.hp -= amount
            self.last_hit_time = current_time            
            if self.hp <= 0:
                self.hp = 0
                self.is_dead = True
            return True
        return False
    

    def get_image(self, index):

        ### extraccion de imagen


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

    # Actualiza la animacion
    def update(self):
        current_time = pygame.time.get_ticks()
        self.check_state_change() 

        target_cooldown = self.attack_cooldown if self.is_attacking else self.cooldown

        self.animation_finished = False
        if current_time - self.last_update >= target_cooldown:
            self.last_update = current_time 
            self.current_frame_in_animation += 1
            
            # Si llegamos al final de la animación
            if self.current_frame_in_animation >= self.animation_duration:
                # ### NUEVO: Avisamos que terminó el ciclo (Vital para el Boss)
                self.animation_finished = True 

                # Si es un ataque y termina la animación...
                if self.is_attacking:
                    pass 
                
                self.current_frame_in_animation = 0 

            spritesheet_index = self.start_frame_index + self.current_frame_in_animation
            self.image = self.get_image(spritesheet_index)
            self.compensate()
    
    ##voltea la imagen
    def compensate(self):
        
        should_flip = (self.direction == "left")
        self.image = pygame.transform.flip(self.image, should_flip, False)
        

        

    ## Detector de cambios de estado
    def check_state_change(self):
        if self.state != self.previous_state:
            
            try:
                self.start_frame_index, self.animation_duration = self.animation_data[self.state]
            except KeyError:
                print(f"Error: La animación '{self.state}' no existe en animation_data.")
                self.state = self.previous_state if self.previous_state else 'idle'
                return

            self.current_frame_in_animation = 0
            self.animation_finished = False
            self.last_update = pygame.time.get_ticks() 
            
            spritesheet_index = self.start_frame_index 
            self.image = self.get_image(spritesheet_index)
            
            self.compensate()
            self.previous_state = self.state
    
class Player(Entity):
    def __init__(self, name, spritesheet, visual_config, animation_data, default_animation, floor_y, limit_rigth):
        super().__init__(name, spritesheet, visual_config, animation_data, default_animation)
        

        self.floor_y = floor_y

        self.limit_right = limit_rigth
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
        if self.vertical_momentum > 20: 
            self.vertical_momentum = 20
            
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
                movement_applied = False
                self.direction = 'right'
            
        if keys[pygame.K_RIGHT]:
            self.direction = "right"
            self.rect.x += self.speed
            movement_applied = True
            if keys[pygame.K_LEFT]:
                movement_applied = False
                
            
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
            
        if event.key == pygame.K_z:
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
        
        # salto
        if self.on_ground and event.type == pygame.KEYDOWN and event.key == pygame.K_x:
            self.on_ground = False
            self.jumping = True
            self.state = 'jump'
            self.vertical_momentum = self.jump_speed 

    def player_dashing(self, event):
        """Registra la pulsación de la tecla para iniciar el Dash."""
        
        if self.is_attacking or self.dashing:
            return
            
        #dasheo
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            current_time = pygame.time.get_ticks()
            
            self.dashing = True
            self.state = 'dash'
            self.dash_timer = current_time + self.dash_duration_ms
            
    #Cerebro de Entity
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

        if self.rect.left < 30:
            self.rect.left = 30

        # 2. Límite Derecho (No pasar del ancho del escenario)
        if self.rect.right > self.limit_right:
            self.rect.right = self.limit_right