execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[type=atalaya:rajang]
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
title @a times 5 40 10
title @a subtitle {"text": "Repite cualquiera: /function escenas:<nombre>", "color": "#E3ECDF"}
title @a title {"text": "Fin", "color": "#8CFF5A"}
gamemode creative @a
gamerule spawn_mobs true
scoreboard players set #recorrido escenas 0
