execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[type=atalaya:aeralis]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run execute as @e[type=minecraft:slime,distance=..80] run data merge entity @s {Size:0}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[distance=..80,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run time set noon
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run weather clear
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run difficulty normal
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon atalaya:aeralis ~0 ~ ~0 {Rotation:[-90f,0f]}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run tp @a ~40 ~14 ~0 facing ~0 ~13 ~0
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a subtitle {"text": "Brisa, Rafaga, Tempestad y Ojo de la tormenta", "color": "#E4ECF8"}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a title {"text": "Las cuatro fases", "color": "#9FE8FF"}
schedule function escenas_aeralis:fases/t0000 45t append
schedule function escenas_aeralis:fases/t0090 135t append
schedule function escenas_aeralis:fases/t0100 145t append
schedule function escenas_aeralis:fases/t0150 195t append
schedule function escenas_aeralis:fases/t0160 205t append
schedule function escenas_aeralis:fases/t0210 255t append
schedule function escenas_aeralis:fases/t0220 265t append
schedule function escenas_aeralis:fases/t0270 315t append
schedule function escenas_aeralis:fases/t0280 325t append
schedule function escenas_aeralis:fases/t0290 335t append
schedule function escenas_aeralis:fases/fin 355t append
