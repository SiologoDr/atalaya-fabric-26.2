execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:nerea]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:aeralis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:rajang]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run summon atalaya:rajang ~ ~ ~ {Rotation:[180f,0f]}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run tp @a ~ ~3 ~-28 facing ~ ~8 ~
schedule function escenas_novilis:presenta_rajang_despierta 40t replace
