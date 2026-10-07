function escenas_novilis:ancla
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:nerea]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:aeralis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:rajang]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run time set noon
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run weather clear
gamemode spectator @a
gamerule spawn_mobs false
schedule function escenas_novilis:presenta_nerea 20t append
schedule function escenas_novilis:presenta_aeralis 730t append
schedule function escenas_novilis:presenta_rajang 1440t append
schedule function escenas_novilis:presenta_novilis 2150t append
schedule function escenas_novilis:presenta_fin 2860t append
