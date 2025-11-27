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
        self.is_attacking = False
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_window_ms = 400
    
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
        # NOTA: Asegúrate que default_animation (ej. 'idle') exista en animation_data
        self.start_frame_index, self.animation_duration = self.animation_data[self.state]
        # El frame actual DENTRO de la animación (0 a duration-1)
        self.current_frame_in_animation = 0 
        
        # Calculamos el índice real para la imagen inicial
        initial_spritesheet_index = self.start_frame_index + self.current_frame_in_animation
        
        # Creamos la primera imagen y el rect (SOLUCIÓN AL ERROR: rect = None)
        self.image = self.get_image(initial_spritesheet_index)
        self.rect = self.image.get_rect() # <--- ¡IMPORTANTE! self.rect debe inicializarse aquí
        
        # Asignamos la posición inicial
        self.rect.x = visual_config["start_x"]
        self.rect.y = visual_config["start_y"]

    # --- Método de Extracción de Imagen ---
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

    # --- Método de Actualización de Animación ---
    def update(self):
        current_time = pygame.time.get_ticks()
        # NOTA: check_state_change() se llama al inicio para aplicar el nuevo estado inmediatamente
        self.check_state_change() 

        # 1. Lógica de avance de frame
        if current_time - self.last_update >= self.cooldown:
            self.last_update = current_time 
            self.current_frame_in_animation += 1
            
            # 2. Bucle (si termina la animación)
            if self.current_frame_in_animation >= self.animation_duration:
                self.current_frame_in_animation = 0 
                
            # 3. Calcular el índice real
            spritesheet_index = self.start_frame_index + self.current_frame_in_animation
            
            # 4. Actualizar la imagen y el rect
            self.image = self.get_image(spritesheet_index)
            self.compensate() # Aplica flip y reajusta self.rect al final
    
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
            # (SOLUCIÓN AL ERROR KeyError: 'walk', las claves deben existir)
            try:
                self.start_frame_index, self.animation_duration = self.animation_data[self.state]
            except KeyError:
                print(f"Error: La animación '{self.state}' no existe en animation_data.")
                self.state = self.previous_state if self.previous_state else 'idle'
                return

            # 2. Reiniciar el frame y el temporizador
            self.current_frame_in_animation = 0
            self.last_update = pygame.time.get_ticks() 
            
            # 3. Dibujar el primer frame de la nueva animación inmediatamente
            spritesheet_index = self.start_frame_index 
            self.image = self.get_image(spritesheet_index)
            
            self.compensate()
            # 4. Actualizar el estado anterior
            self.previous_state = self.state
    
class Player(Entity):
    def __init__(self, name, spritesheet, visual_config, animation_data, default_animation):
        super().__init__(name, spritesheet, visual_config, animation_data, default_animation)
        
        # Variables de Salto
        self.on_ground = True      
        self.jump_speed = -20      
        self.vertical_momentum = 0 
        self.gravity = 1           
        self.jumping = False
        
        # Variables de Dash
        self.dashing = False 
        self.dash_duration_ms = 500 
        self.dash_timer = 0         
        self.dash_speed = 20
        
        self.is_moving = False # Para saber si debe volver a 'walk' o 'idle'

    def apply_gravity_and_jump(self):
        """Aplica la gravedad y el movimiento vertical."""
        
        # 1. Aplicar Gravedad
        if not self.on_ground:
            self.vertical_momentum += self.gravity
            
        # 2. Limitar la Velocidad (Opcional)
        if self.vertical_momentum > 15: 
            self.vertical_momentum = 15
            
        # 3. Aplicar Movimiento
        self.rect.y += self.vertical_momentum
        
        # 4. Simulación del Suelo (Reemplazar con colisión real)
        GROUND_Y = 600
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.on_ground = True
            self.jumping = False
            self.vertical_momentum = 0
            
            # Si aterriza, el estado se manejará en Player.update
            
    def Running_player(self, keys):
        self.keys = keys
        self.is_moving = False
        
        # Bloquea movimiento si está atacando O dashando
        if self.is_attacking or self.dashing:
            return 

        # --- Movimiento Lateral (Permitido en aire) ---
        movement_applied = False

        if keys[pygame.K_LEFT]:
            self.direction = "left"
            self.rect.x -= self.speed
            movement_applied = True
            
        if keys[pygame.K_RIGHT]:
            self.direction = "right"
            self.rect.x += self.speed
            movement_applied = True
            
        # --- Lógica de Estado (SOLO si está en el suelo) ---
        if self.on_ground: 
            if movement_applied:
                self.state = "walk"
                self.is_moving = True
            else:
                self.state = "idle"
        else:
            # Guarda si hubo input de movimiento para el retorno después del dash/ataque
            self.is_moving = movement_applied 

    def player_attack(self, event): 
        """Registra la pulsación de la tecla para iniciar o encadenar el combo."""
        
        # SOLUCIÓN al AttributeError: 'pygame.event.Event' object has no attribute 'key'
        if event.type != pygame.KEYDOWN:
            return
            
        if event.key == pygame.K_x:
            current_time = pygame.time.get_ticks()

            # --- 1. Lógica de REGISTRO (Combo ya iniciado) ---
            if self.combo_timer > current_time and self.combo_count < 3: 
                self.combo_count += 1
                print(f"Combo registrado: Siguiente Ataque ({self.combo_count})")
                
            # --- 2. Lógica de INICIO (Primer Ataque) ---
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
                print("Iniciando Ataque 1")

    def player_jump(self, event):
        if self.is_attacking or self.dashing:
            return
        
        # Usamos K_c para el salto (¡asumo que K_z es para Dash!)
        if self.on_ground and event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            self.on_ground = False
            self.jumping = True
            self.state = 'jump'
            self.vertical_momentum = self.jump_speed 

    def player_dashing(self, event):
        """Registra la pulsación de la tecla para iniciar el Dash."""
        
        if self.is_attacking or self.dashing:
            return
            
        # Usamos K_z para el Dash (¡asumo que K_c es para Salto!)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_z:
            current_time = pygame.time.get_ticks()
            
            self.dashing = True
            self.state = 'dash'
            self.dash_timer = current_time + self.dash_duration_ms
            
            # NO resetear self.vertical_momentum aquí para permitir la caída/subida.
            print("Dash iniciado.")

    def update(self):
        current_time = pygame.time.get_ticks()

        # 1. APLICAR FÍSICA (DEBE ser lo primero)
        self.apply_gravity_and_jump() 
        
        # --- 2. LÓGICA DEL DASH (Máxima Prioridad) ---
        if self.dashing:
            
            if current_time < self.dash_timer:
                # Movimiento horizontal (la gravedad se aplica en apply_gravity_and_jump)
                if self.direction == "right":
                    self.rect.x += self.dash_speed
                else:
                    self.rect.x -= self.dash_speed
            else:
                # Dash finalizado
                self.dashing = False
                
                if not self.on_ground:
                    self.state = 'jump' # Vuelve al salto si sigue en el aire
                elif self.is_moving:
                    self.state = 'walk'
                else:
                    self.state = 'idle'
                
        # --- 3. LÓGICA DE ATAQUE (Alta Prioridad) ---
        elif self.is_attacking:
            
            # Transiciones y fin del combo
            if self.current_frame_in_animation >= self.animation_duration - 1:
                
                # Transiciones 1->2 o 2->3
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
                    # FIN DEL COMBO 
                    self.is_attacking = False
                    self.combo_count = 0
                    # Vuelve a 'jump' o 'idle'
                    if not self.on_ground:
                        self.state = 'jump' 
                    else:
                        self.state = 'idle'

        # --- 4. LÓGICA DE REINICIO DE COMBO (Media Prioridad) ---
        elif current_time > self.combo_timer:
            self.combo_count = 0
            
        # --- 5. PRIORIZACIÓN DEL ESTADO DE SALTO/CAÍDA (Baja Prioridad) ---
        # Si NO está dashando, NO está atacando y NO está en el suelo.
        elif not self.on_ground:
            self.state = 'jump' # <--- Ahora esta línea está correctamente indentada
            
        # 6. ACTUALIZACIÓN DE ENTITY (Debe ser lo último)
        super().update()