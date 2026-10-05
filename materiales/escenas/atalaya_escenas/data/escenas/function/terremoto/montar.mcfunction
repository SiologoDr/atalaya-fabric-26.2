execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[type=atalaya:rajang]
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run execute as @e[type=minecraft:slime,distance=..72] run data merge entity @s {Size:0}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[distance=..72,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run fill ~13 ~ ~-6 ~14 ~7 ~6 minecraft:air replace minecraft:stone_bricks
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run time set noon
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run weather clear
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run difficulty normal
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run summon atalaya:rajang ~0 ~ ~0 {Rotation:[-90f,0f]}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run summon minecraft:mannequin ~10 ~ ~6 {Tags:["escena"],CustomName:"presa"}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run summon minecraft:mannequin ~14 ~ ~-8 {Tags:["escena"],CustomName:"presa"}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run summon minecraft:mannequin ~-8 ~ ~10 {Tags:["escena"],CustomName:"presa"}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run summon minecraft:mannequin ~18 ~ ~2 {Tags:["escena"],CustomName:"presa"}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run tp @a ~-6 ~14 ~-22 facing ~6 ~0 ~2
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run title @a subtitle {"text": "Los pilares lanzan a 10 bloques", "color": "#E3ECDF"}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run title @a title {"text": "Terremoto Ancestral", "color": "#8CFF5A"}
schedule function escenas:terremoto/t0000 45t append
schedule function escenas:terremoto/t0048 93t append
schedule function escenas:terremoto/fin 175t append
