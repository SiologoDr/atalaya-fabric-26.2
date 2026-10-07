execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[type=atalaya:aeralis]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run execute as @e[type=minecraft:slime,distance=..80] run data merge entity @s {Size:0}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[distance=..80,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run time set noon
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run weather clear
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run difficulty normal
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon atalaya:aeralis ~0 ~ ~0 {Rotation:[-90f,0f]}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon minecraft:mannequin ~14 ~ ~4 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon minecraft:mannequin ~10 ~ ~-8 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon minecraft:mannequin ~-6 ~ ~10 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run tp @a ~8 ~22 ~-52 facing ~8 ~8 ~0
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a subtitle {"text": "Cada tornado roto le devuelve su viento; con 10, 20 o 30 cae aturdida 10 s", "color": "#E4ECF8"}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a title {"text": "Viento de vuelta", "color": "#9FE8FF"}
schedule function escenas_aeralis:viento/t0000 45t append
schedule function escenas_aeralis:viento/t0080 125t append
schedule function escenas_aeralis:viento/t0130 175t append
schedule function escenas_aeralis:viento/t0200 245t append
schedule function escenas_aeralis:viento/t0210 255t append
schedule function escenas_aeralis:viento/t0235 280t append
schedule function escenas_aeralis:viento/t0245 290t append
schedule function escenas_aeralis:viento/t0258 303t append
schedule function escenas_aeralis:viento/t0282 327t append
schedule function escenas_aeralis:viento/t0290 335t append
schedule function escenas_aeralis:viento/t0305 350t append
schedule function escenas_aeralis:viento/t0360 405t append
schedule function escenas_aeralis:viento/t0420 465t append
schedule function escenas_aeralis:viento/t0455 500t append
schedule function escenas_aeralis:viento/t0480 525t append
schedule function escenas_aeralis:viento/fin 565t append
