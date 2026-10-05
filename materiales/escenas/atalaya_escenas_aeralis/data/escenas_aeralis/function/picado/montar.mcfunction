execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[type=atalaya:aeralis]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run execute as @e[type=minecraft:slime,distance=..80] run data merge entity @s {Size:0}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[distance=..80,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run time set noon
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run weather clear
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run difficulty normal
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon atalaya:aeralis ~0 ~ ~0 {Rotation:[-90f,0f]}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon minecraft:mannequin ~26 ~ ~0 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon minecraft:mannequin ~16 ~ ~3 {Tags:["escena"],CustomName:"en medio",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run tp @a ~16 ~26 ~-52 facing ~20 ~2 ~0
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a subtitle {"text": "Si te pilla, te gasta el totem y te manda al cielo; luego se posa 3 s", "color": "#E4ECF8"}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a title {"text": "Picado del Vendaval", "color": "#9FE8FF"}
schedule function escenas_aeralis:picado/t0000 45t append
schedule function escenas_aeralis:picado/t0080 125t append
schedule function escenas_aeralis:picado/t0130 175t append
schedule function escenas_aeralis:picado/t0150 195t append
schedule function escenas_aeralis:picado/t0162 207t append
schedule function escenas_aeralis:picado/t0170 215t append
schedule function escenas_aeralis:picado/t0178 223t append
schedule function escenas_aeralis:picado/t0190 235t append
schedule function escenas_aeralis:picado/t0204 249t append
schedule function escenas_aeralis:picado/t0212 257t append
schedule function escenas_aeralis:picado/t0222 267t append
schedule function escenas_aeralis:picado/fin 325t append
