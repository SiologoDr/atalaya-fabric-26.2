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
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run summon minecraft:mannequin ~12 ~ ~6 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run summon minecraft:mannequin ~-8 ~ ~8 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run summon minecraft:mannequin ~14 ~ ~-10 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run summon minecraft:mannequin ~-12 ~ ~-6 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run tp @a ~-20 ~28 ~-48 facing ~0 ~6 ~0
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a subtitle {"text": "Fase IV: suelta la espada y llena las zonas carmesi de soles", "color": "#F4E9D8"}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a title {"text": "Dios de la Guerra", "color": "#FFC23A"}
schedule function escenas_novilis:dios/t0000 45t append
schedule function escenas_novilis:dios/t0075 120t append
schedule function escenas_novilis:dios/t0150 195t append
schedule function escenas_novilis:dios/t0225 270t append
schedule function escenas_novilis:dios/t0300 345t append
schedule function escenas_novilis:dios/t0312 357t append
schedule function escenas_novilis:dios/t0322 367t append
schedule function escenas_novilis:dios/t0334 379t append
schedule function escenas_novilis:dios/t0356 401t append
schedule function escenas_novilis:dios/t0376 421t append
schedule function escenas_novilis:dios/t0392 437t append
schedule function escenas_novilis:dios/t0400 445t append
schedule function escenas_novilis:dios/t0420 465t append
schedule function escenas_novilis:dios/fin 495t append
