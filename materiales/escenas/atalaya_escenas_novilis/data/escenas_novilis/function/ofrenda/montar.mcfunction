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
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run summon minecraft:mannequin ~10 ~ ~0 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run tp @a ~16 ~12 ~-28 facing ~4 ~9 ~0
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a subtitle {"text": "Te agarra y te alza al sol: 15 letras en 8 s (20 en la fase IV)", "color": "#F4E9D8"}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a title {"text": "Ofrenda al Sol", "color": "#FFC23A"}
schedule function escenas_novilis:ofrenda/t0000 45t append
schedule function escenas_novilis:ofrenda/t0075 120t append
schedule function escenas_novilis:ofrenda/t0150 195t append
schedule function escenas_novilis:ofrenda/t0225 270t append
schedule function escenas_novilis:ofrenda/t0235 280t append
schedule function escenas_novilis:ofrenda/t0253 298t append
schedule function escenas_novilis:ofrenda/t0275 320t append
schedule function escenas_novilis:ofrenda/t0285 330t append
schedule function escenas_novilis:ofrenda/t0300 345t append
schedule function escenas_novilis:ofrenda/t0310 355t append
schedule function escenas_novilis:ofrenda/t0425 470t append
schedule function escenas_novilis:ofrenda/t0450 495t append
schedule function escenas_novilis:ofrenda/fin 535t append
