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
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run tp @a ~8 ~22 ~-52 facing ~8 ~6 ~0
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a subtitle {"text": "El aro marca hasta donde atrapa; los tres anillos son sus tres golpes", "color": "#E4ECF8"}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a title {"text": "Tornados", "color": "#9FE8FF"}
schedule function escenas_aeralis:tornados/t0000 45t append
schedule function escenas_aeralis:tornados/t0080 125t append
schedule function escenas_aeralis:tornados/t0130 175t append
schedule function escenas_aeralis:tornados/t0180 225t append
schedule function escenas_aeralis:tornados/t0235 280t append
schedule function escenas_aeralis:tornados/t0265 310t append
schedule function escenas_aeralis:tornados/t0280 325t append
schedule function escenas_aeralis:tornados/t0290 335t append
schedule function escenas_aeralis:tornados/fin 375t append
