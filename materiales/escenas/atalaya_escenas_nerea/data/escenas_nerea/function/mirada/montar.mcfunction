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
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run summon minecraft:mannequin ~16 ~ ~6 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run summon minecraft:mannequin ~-14 ~ ~8 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run summon minecraft:mannequin ~20 ~ ~-10 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run summon minecraft:mannequin ~-18 ~ ~-6 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run summon minecraft:mannequin ~8 ~ ~18 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run summon minecraft:mannequin ~-6 ~ ~-20 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run summon minecraft:mannequin ~24 ~ ~2 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run summon minecraft:mannequin ~-24 ~ ~0 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run summon minecraft:mannequin ~2 ~ ~24 {Tags:["escena"],CustomName:"presa",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f,equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run tp @a ~-26 ~20 ~-36 facing ~0 ~9 ~0
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run title @a subtitle {"text": "Mira a un tercio (de 9, 3); 10 impactos por ojo; si sale: totem fuera y Furia", "color": "#E4ECF8"}
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run title @a title {"text": "Mirada del Abismo", "color": "#7FE6F2"}
schedule function escenas_nerea:mirada/t0000 45t append
schedule function escenas_nerea:mirada/t0080 125t append
schedule function escenas_nerea:mirada/t0140 185t append
schedule function escenas_nerea:mirada/t0200 245t append
schedule function escenas_nerea:mirada/t0222 267t append
schedule function escenas_nerea:mirada/t0226 271t append
schedule function escenas_nerea:mirada/t0232 277t append
schedule function escenas_nerea:mirada/t0238 283t append
schedule function escenas_nerea:mirada/t0242 287t append
schedule function escenas_nerea:mirada/t0250 295t append
schedule function escenas_nerea:mirada/t0252 297t append
schedule function escenas_nerea:mirada/t0255 300t append
schedule function escenas_nerea:mirada/t0258 303t append
schedule function escenas_nerea:mirada/t0262 307t append
schedule function escenas_nerea:mirada/t0290 335t append
schedule function escenas_nerea:mirada/t0300 345t append
schedule function escenas_nerea:mirada/t0310 355t append
schedule function escenas_nerea:mirada/t0322 367t append
schedule function escenas_nerea:mirada/fin 395t append
