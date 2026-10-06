execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:estatua_novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:fuente_solar]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:sol_novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:sello_sol]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:onda_fuego]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:tajo_novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run execute as @e[type=minecraft:slime,distance=..90] run data merge entity @s {Size:0}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[distance=..90,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run time set noon
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run weather clear
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run difficulty normal
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run summon atalaya:novilis ~0 ~ ~0 {Rotation:[-90f,0f]}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run tp @a ~30 ~9 ~0 facing ~0 ~9 ~0
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a subtitle {"text": "16 bloques hasta el yelmo, 18 con el halo", "color": "#F4E9D8"}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a title {"text": "Novilis, el Caballero Solar", "color": "#FFC23A"}
schedule function escenas_novilis:cuerpo/t0004 49t append
schedule function escenas_novilis:cuerpo/t0006 51t append
schedule function escenas_novilis:cuerpo/t0030 75t append
schedule function escenas_novilis:cuerpo/t0056 101t append
schedule function escenas_novilis:cuerpo/t0085 130t append
schedule function escenas_novilis:cuerpo/t0095 140t append
schedule function escenas_novilis:cuerpo/t0105 150t append
schedule function escenas_novilis:cuerpo/t0115 160t append
schedule function escenas_novilis:cuerpo/t0125 170t append
schedule function escenas_novilis:cuerpo/t0135 180t append
schedule function escenas_novilis:cuerpo/t0145 190t append
schedule function escenas_novilis:cuerpo/t0155 200t append
schedule function escenas_novilis:cuerpo/t0165 210t append
schedule function escenas_novilis:cuerpo/t0175 220t append
schedule function escenas_novilis:cuerpo/t0185 230t append
schedule function escenas_novilis:cuerpo/fin 250t append
