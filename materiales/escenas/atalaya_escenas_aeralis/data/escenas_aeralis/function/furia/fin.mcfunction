execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[type=atalaya:aeralis]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
title @a times 5 40 10
title @a subtitle {"text": "Repite cualquiera: /function escenas_aeralis:<nombre>", "color": "#E4ECF8"}
title @a title {"text": "Fin", "color": "#9FE8FF"}
gamemode creative @a
gamerule spawn_mobs true
