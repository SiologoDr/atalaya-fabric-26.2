execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[type=atalaya:aeralis]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run execute as @e[type=minecraft:slime,distance=..80] run data merge entity @s {Size:0}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[distance=..80,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run time set noon
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run weather clear
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run difficulty normal
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon atalaya:aeralis ~0 ~ ~0 {Rotation:[-90f,0f]}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run tp @a ~30 ~12 ~0 facing ~0 ~13 ~0
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a subtitle {"text": "El remake: alas de 38 bloques, halo, corona y melena", "color": "#E4ECF8"}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a title {"text": "Aeralis, Reina del Vendaval", "color": "#9FE8FF"}
schedule function escenas_aeralis:cuerpo/t0000 45t append
schedule function escenas_aeralis:cuerpo/t0095 140t append
schedule function escenas_aeralis:cuerpo/t0105 150t append
schedule function escenas_aeralis:cuerpo/t0115 160t append
schedule function escenas_aeralis:cuerpo/t0125 170t append
schedule function escenas_aeralis:cuerpo/t0135 180t append
schedule function escenas_aeralis:cuerpo/t0145 190t append
schedule function escenas_aeralis:cuerpo/t0155 200t append
schedule function escenas_aeralis:cuerpo/t0165 210t append
schedule function escenas_aeralis:cuerpo/t0175 220t append
schedule function escenas_aeralis:cuerpo/t0185 230t append
schedule function escenas_aeralis:cuerpo/t0195 240t append
schedule function escenas_aeralis:cuerpo/fin 265t append
