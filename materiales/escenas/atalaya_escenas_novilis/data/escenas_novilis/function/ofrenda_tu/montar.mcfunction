execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:estatua_novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:fuente_solar]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:sol_novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:sello_sol]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:onda_fuego]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:tajo_novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run execute as @e[type=minecraft:slime,distance=..90] run data merge entity @s {Size:0}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[distance=..90,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run time set noon
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run weather clear
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run difficulty normal
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run summon atalaya:novilis ~0 ~ ~0 {Rotation:[-90f,0f]}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run tp @a ~12 ~ ~ facing ~0 ~10 ~0
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a subtitle {"text": "Pulsa las letras en orden: Escape no la para", "color": "#F4E9D8"}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a title {"text": "Ofrenda al Sol (tu)", "color": "#FFC23A"}
schedule function escenas_novilis:ofrenda_tu/t0000 45t append
schedule function escenas_novilis:ofrenda_tu/t0075 120t append
schedule function escenas_novilis:ofrenda_tu/t0150 195t append
schedule function escenas_novilis:ofrenda_tu/t0215 260t append
schedule function escenas_novilis:ofrenda_tu/t0225 270t append
schedule function escenas_novilis:ofrenda_tu/t0240 285t append
schedule function escenas_novilis:ofrenda_tu/t0250 295t append
schedule function escenas_novilis:ofrenda_tu/t0262 307t append
schedule function escenas_novilis:ofrenda_tu/t0282 327t append
schedule function escenas_novilis:ofrenda_tu/t0302 347t append
schedule function escenas_novilis:ofrenda_tu/t0330 375t append
schedule function escenas_novilis:ofrenda_tu/t0370 415t append
schedule function escenas_novilis:ofrenda_tu/t0480 525t append
schedule function escenas_novilis:ofrenda_tu/t0496 541t append
schedule function escenas_novilis:ofrenda_tu/fin 585t append
