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
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run tp @a ~-30 ~16 ~-32 facing ~0 ~5 ~0
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a subtitle {"text": "Cuatro angeles tocan su melodia: rompedlos antes de que acabe", "color": "#F4E9D8"}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a title {"text": "Trompetas del Apocalipsis", "color": "#FFC23A"}
schedule function escenas_novilis:trompetas/t0000 45t append
schedule function escenas_novilis:trompetas/t0075 120t append
schedule function escenas_novilis:trompetas/t0150 195t append
schedule function escenas_novilis:trompetas/t0176 221t append
schedule function escenas_novilis:trompetas/t0192 237t append
schedule function escenas_novilis:trompetas/t0215 260t append
schedule function escenas_novilis:trompetas/t0225 270t append
schedule function escenas_novilis:trompetas/t0235 280t append
schedule function escenas_novilis:trompetas/t0245 290t append
schedule function escenas_novilis:trompetas/t0255 300t append
schedule function escenas_novilis:trompetas/t0270 315t append
schedule function escenas_novilis:trompetas/t0273 318t append
schedule function escenas_novilis:trompetas/t0276 321t append
schedule function escenas_novilis:trompetas/t0279 324t append
schedule function escenas_novilis:trompetas/t0282 327t append
schedule function escenas_novilis:trompetas/t0285 330t append
schedule function escenas_novilis:trompetas/t0288 333t append
schedule function escenas_novilis:trompetas/t0291 336t append
schedule function escenas_novilis:trompetas/t0294 339t append
schedule function escenas_novilis:trompetas/t0297 342t append
schedule function escenas_novilis:trompetas/t0305 350t append
schedule function escenas_novilis:trompetas/t0315 360t append
schedule function escenas_novilis:trompetas/t0325 370t append
schedule function escenas_novilis:trompetas/t0640 685t append
schedule function escenas_novilis:trompetas/t0670 715t append
schedule function escenas_novilis:trompetas/t0700 745t append
schedule function escenas_novilis:trompetas/fin 785t append
