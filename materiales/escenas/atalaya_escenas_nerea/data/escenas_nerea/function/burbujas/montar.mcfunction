execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run kill @e[type=atalaya:nerea]
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run kill @e[type=atalaya:ola_nerea]
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run kill @e[type=atalaya:geiser_nerea]
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run execute as @e[type=minecraft:slime,distance=..80] run data merge entity @s {Size:0}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run kill @e[distance=..80,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run time set noon
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run weather clear
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run difficulty normal
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run summon atalaya:nerea ~0 ~ ~0 {Rotation:[-90f,0f]}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run summon minecraft:mannequin ~16 ~ ~6 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run summon minecraft:mannequin ~14 ~ ~-8 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run summon minecraft:mannequin ~22 ~ ~0 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run tp @a ~8 ~14 ~-30 facing ~12 ~4 ~0
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run title @a subtitle {"text": "El corazon dentro y en el suelo hasta donde revientan", "color": "#E4ECF8"}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run title @a title {"text": "Burbujas bomba", "color": "#7FE6F2"}
schedule function escenas_nerea:burbujas/t0000 45t append
schedule function escenas_nerea:burbujas/t0080 125t append
schedule function escenas_nerea:burbujas/t0092 137t append
schedule function escenas_nerea:burbujas/t0100 145t append
schedule function escenas_nerea:burbujas/t0110 155t append
schedule function escenas_nerea:burbujas/t0116 161t append
schedule function escenas_nerea:burbujas/fin 195t append
