execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[type=atalaya:aeralis]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run execute as @e[type=minecraft:slime,distance=..80] run data merge entity @s {Size:0}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[distance=..80,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run time set noon
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run weather clear
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run difficulty normal
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon atalaya:aeralis ~0 ~ ~0 {Rotation:[-90f,0f]}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon minecraft:mannequin ~10 ~ ~6 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon minecraft:mannequin ~-8 ~ ~8 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon minecraft:mannequin ~14 ~ ~-10 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon minecraft:mannequin ~-12 ~ ~-6 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon minecraft:mannequin ~4 ~ ~14 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon minecraft:mannequin ~-4 ~ ~-14 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon minecraft:mannequin ~18 ~ ~2 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon minecraft:mannequin ~-18 ~ ~0 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run summon minecraft:mannequin ~0 ~ ~20 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run tp @a ~-24 ~24 ~-44 facing ~0 ~10 ~0
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a subtitle {"text": "Un ciclon atrapa a un tercio (de 9, 3); si no rompen los 4 cristales: totem fuera y Furia", "color": "#E4ECF8"}
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run title @a title {"text": "Juicio del Ciclon", "color": "#9FE8FF"}
schedule function escenas_aeralis:juicio/t0000 45t append
schedule function escenas_aeralis:juicio/t0080 125t append
schedule function escenas_aeralis:juicio/t0130 175t append
schedule function escenas_aeralis:juicio/t0180 225t append
schedule function escenas_aeralis:juicio/t0230 275t append
schedule function escenas_aeralis:juicio/t0300 345t append
schedule function escenas_aeralis:juicio/t0330 375t append
schedule function escenas_aeralis:juicio/t0340 385t append
schedule function escenas_aeralis:juicio/t0352 397t append
schedule function escenas_aeralis:juicio/t0500 545t append
schedule function escenas_aeralis:juicio/t0548 593t append
schedule function escenas_aeralis:juicio/t0580 625t append
schedule function escenas_aeralis:juicio/t0590 635t append
schedule function escenas_aeralis:juicio/t0610 655t append
schedule function escenas_aeralis:juicio/fin 695t append
