execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[type=atalaya:rajang]
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run execute as @e[type=minecraft:slime,distance=..72] run data merge entity @s {Size:0}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[distance=..72,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run fill ~13 ~ ~-6 ~14 ~7 ~6 minecraft:air replace minecraft:stone_bricks
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run time set noon
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run weather clear
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run difficulty normal
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run summon atalaya:rajang ~0 ~ ~0 {Rotation:[-90f,0f]}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run summon minecraft:mannequin ~16 ~ ~0 {Tags:["escena"],CustomName:"presa"}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run tp @a ~8 ~6 ~-18 facing ~10 ~2 ~0
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run title @a subtitle {"text": "El zarpazo empuja 6 bloques; los picos lanzan a 10 y dejan el Peso 3 s", "color": "#E3ECDF"}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run title @a title {"text": "Garra Terrestre", "color": "#8CFF5A"}
schedule function escenas:garra/t0000 45t append
schedule function escenas:garra/t0002 47t append
schedule function escenas:garra/t0020 65t append
schedule function escenas:garra/t0030 75t append
schedule function escenas:garra/fin 135t append
