execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[type=atalaya:rajang]
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run execute as @e[type=minecraft:slime,distance=..72] run data merge entity @s {Size:0}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[distance=..72,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run fill ~13 ~ ~-6 ~14 ~7 ~6 minecraft:air replace minecraft:stone_bricks
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run time set noon
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run weather clear
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run difficulty normal
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run summon atalaya:rajang ~0 ~ ~0 {Rotation:[-90f,0f]}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run summon minecraft:mannequin ~5 ~ ~4 {Tags:["escena"],CustomName:"pegado"}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run summon minecraft:mannequin ~16 ~ ~-4 {Tags:["escena"],CustomName:"dentro"}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run summon minecraft:mannequin ~26 ~ ~-12 {Tags:["escena"],CustomName:"dentro"}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run summon minecraft:mannequin ~0 ~ ~-33 {Tags:["escena"],CustomName:"dentro"}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run summon minecraft:mannequin ~40 ~ ~3 {Tags:["escena"],CustomName:"fuera"}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run summon minecraft:mannequin ~-30 ~ ~25 {Tags:["escena"],CustomName:"fuera"}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run tp @a ~-12 ~52 ~-56 facing ~0 ~0 ~0
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run title @a subtitle {"text": "Sal del círculo de 36 bloques antes de que se llene (6 s)", "color": "#E3ECDF"}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run title @a title {"text": "Tumba de Raíces", "color": "#8CFF5A"}
schedule function escenas:tumba/t0000 45t append
schedule function escenas:tumba/t0070 115t append
schedule function escenas:tumba/t0122 167t append
schedule function escenas:tumba/fin 225t append
