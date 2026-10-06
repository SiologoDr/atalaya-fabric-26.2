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
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run summon minecraft:mannequin ~22 ~ ~0 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run tp @a ~-14 ~22 ~-44 facing ~0 ~5 ~0
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a subtitle {"text": "Tres fuentes le dan fuego; rotas, cae aturdido", "color": "#F4E9D8"}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a title {"text": "Fuentes Solares", "color": "#FFC23A"}
schedule function escenas_novilis:fuentes/t0000 45t append
schedule function escenas_novilis:fuentes/t0075 120t append
schedule function escenas_novilis:fuentes/t0150 195t append
schedule function escenas_novilis:fuentes/t0225 270t append
schedule function escenas_novilis:fuentes/t0243 288t append
schedule function escenas_novilis:fuentes/t0260 305t append
schedule function escenas_novilis:fuentes/t0300 345t append
schedule function escenas_novilis:fuentes/t0310 355t append
schedule function escenas_novilis:fuentes/t0320 365t append
schedule function escenas_novilis:fuentes/t0330 375t append
schedule function escenas_novilis:fuentes/t0340 385t append
schedule function escenas_novilis:fuentes/t0343 388t append
schedule function escenas_novilis:fuentes/t0346 391t append
schedule function escenas_novilis:fuentes/t0349 394t append
schedule function escenas_novilis:fuentes/t0352 397t append
schedule function escenas_novilis:fuentes/t0355 400t append
schedule function escenas_novilis:fuentes/t0358 403t append
schedule function escenas_novilis:fuentes/t0361 406t append
schedule function escenas_novilis:fuentes/t0364 409t append
schedule function escenas_novilis:fuentes/t0367 412t append
schedule function escenas_novilis:fuentes/t0370 415t append
schedule function escenas_novilis:fuentes/t0372 417t append
schedule function escenas_novilis:fuentes/t0373 418t append
schedule function escenas_novilis:fuentes/t0376 421t append
schedule function escenas_novilis:fuentes/t0379 424t append
schedule function escenas_novilis:fuentes/t0382 427t append
schedule function escenas_novilis:fuentes/t0385 430t append
schedule function escenas_novilis:fuentes/t0388 433t append
schedule function escenas_novilis:fuentes/t0391 436t append
schedule function escenas_novilis:fuentes/t0394 439t append
schedule function escenas_novilis:fuentes/t0397 442t append
schedule function escenas_novilis:fuentes/t0400 445t append
schedule function escenas_novilis:fuentes/t0403 448t append
schedule function escenas_novilis:fuentes/t0406 451t append
schedule function escenas_novilis:fuentes/t0409 454t append
schedule function escenas_novilis:fuentes/t0412 457t append
schedule function escenas_novilis:fuentes/t0415 460t append
schedule function escenas_novilis:fuentes/t0418 463t append
schedule function escenas_novilis:fuentes/t0421 466t append
schedule function escenas_novilis:fuentes/t0424 469t append
schedule function escenas_novilis:fuentes/t0427 472t append
schedule function escenas_novilis:fuentes/t0436 481t append
schedule function escenas_novilis:fuentes/t0446 491t append
schedule function escenas_novilis:fuentes/t0456 501t append
schedule function escenas_novilis:fuentes/fin 565t append
