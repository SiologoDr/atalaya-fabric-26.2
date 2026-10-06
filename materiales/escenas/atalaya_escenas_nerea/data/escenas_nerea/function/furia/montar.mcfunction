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
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run tp @a ~32 ~10 ~0 facing ~0 ~8 ~0
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run title @a subtitle {"text": "Si la Mirada sale: mas rapida, mas dano y menos espera hasta que la derriben", "color": "#E4ECF8"}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run title @a title {"text": "Furia de las Mareas", "color": "#7FE6F2"}
schedule function escenas_nerea:furia/t0000 45t append
schedule function escenas_nerea:furia/t0080 125t append
schedule function escenas_nerea:furia/t0140 185t append
schedule function escenas_nerea:furia/t0200 245t append
schedule function escenas_nerea:furia/t0225 270t append
schedule function escenas_nerea:furia/t0235 280t append
schedule function escenas_nerea:furia/t0245 290t append
schedule function escenas_nerea:furia/t0255 300t append
schedule function escenas_nerea:furia/t0265 310t append
schedule function escenas_nerea:furia/fin 335t append
