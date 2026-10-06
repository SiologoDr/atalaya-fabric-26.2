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
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run summon minecraft:mannequin ~30 ~ ~4 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run summon minecraft:mannequin ~26 ~ ~-10 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run tp @a ~10 ~14 ~-30 facing ~22 ~4 ~0
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run title @a subtitle {"text": "El ancla vuela con su estela y un aro bajo a quien va", "color": "#E4ECF8"}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run title @a title {"text": "Arpon", "color": "#7FE6F2"}
schedule function escenas_nerea:arpon/t0000 45t append
schedule function escenas_nerea:arpon/t0080 125t append
schedule function escenas_nerea:arpon/t0140 185t append
schedule function escenas_nerea:arpon/t0157 202t append
schedule function escenas_nerea:arpon/t0161 206t append
schedule function escenas_nerea:arpon/t0168 213t append
schedule function escenas_nerea:arpon/t0182 227t append
schedule function escenas_nerea:arpon/t0190 235t append
schedule function escenas_nerea:arpon/fin 265t append
