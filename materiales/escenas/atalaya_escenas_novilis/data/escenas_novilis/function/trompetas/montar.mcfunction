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
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run summon minecraft:mannequin ~26 ~ ~0 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run tp @a ~-30 ~16 ~-32 facing ~0 ~5 ~0
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a subtitle {"text": "Cada angel en su estrado: cada 5 s un pulso de fuego tira a quien este encima", "color": "#F4E9D8"}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a title {"text": "Trompetas del Apocalipsis", "color": "#FFC23A"}
schedule function escenas_novilis:trompetas/t0000 45t append
schedule function escenas_novilis:trompetas/t0075 120t append
schedule function escenas_novilis:trompetas/t0150 195t append
schedule function escenas_novilis:trompetas/t0176 221t append
schedule function escenas_novilis:trompetas/t0192 237t append
schedule function escenas_novilis:trompetas/t0212 257t append
schedule function escenas_novilis:trompetas/t0215 260t append
schedule function escenas_novilis:trompetas/t0220 265t append
schedule function escenas_novilis:trompetas/t0230 275t append
schedule function escenas_novilis:trompetas/t0276 321t append
schedule function escenas_novilis:trompetas/t0296 341t append
schedule function escenas_novilis:trompetas/t0302 347t append
schedule function escenas_novilis:trompetas/t0312 357t append
schedule function escenas_novilis:trompetas/t0330 375t append
schedule function escenas_novilis:trompetas/t0340 385t append
schedule function escenas_novilis:trompetas/t0360 405t append
schedule function escenas_novilis:trompetas/t0380 425t append
schedule function escenas_novilis:trompetas/t0383 428t append
schedule function escenas_novilis:trompetas/t0386 431t append
schedule function escenas_novilis:trompetas/t0389 434t append
schedule function escenas_novilis:trompetas/t0392 437t append
schedule function escenas_novilis:trompetas/t0395 440t append
schedule function escenas_novilis:trompetas/t0398 443t append
schedule function escenas_novilis:trompetas/t0401 446t append
schedule function escenas_novilis:trompetas/t0404 449t append
schedule function escenas_novilis:trompetas/t0407 452t append
schedule function escenas_novilis:trompetas/t0415 460t append
schedule function escenas_novilis:trompetas/t0640 685t append
schedule function escenas_novilis:trompetas/t0650 695t append
schedule function escenas_novilis:trompetas/t0680 725t append
schedule function escenas_novilis:trompetas/fin 785t append
