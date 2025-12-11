

pancho_config = {
    "frame_width":120,
    "frame_height":100,
    "scale":3.5,
    "columns":8,
    "cooldown": 110,
    "speed": 5,
    "start_x":100,
    "start_y": 240,
    "crop_bounds": (10, 0, 10, 15),
    "hp":100,
    "hitbox_size":(50,250),
    "image_offset_x": 0
}

pancho_definitions = {
    "idle": (0,13),
    "walk": (13,15),
    "trowing":(28,12),
    "attack":(40,11)
}

player_config = {
    "frame_width":80,
    "frame_height":80,
    "scale":4.5,
    "columns":8,
    "cooldown": 100,
    "attack_cooldown":50,
    "speed": 15,
    "start_x":300,
    "start_y": 127*8,
    "crop_bounds": (0, 10, 0, 30),
    "hitbox_size":(50,130),
    "image_offset_x": 20
}

player_definitions = {
    "attack_1": (0, 9),
    "attack_2": (9,6),
    "attack_3": (41,9),
    "idle": (15, 12),
    "walk": (27, 10),
    "dash": (37, 4),
    "jump": (50 ,5)
}
