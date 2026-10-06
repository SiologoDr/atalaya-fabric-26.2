execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:estatua_novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:fuente_solar]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:sol_novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:sello_sol]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:onda_fuego]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:tajo_novilis]
title @a times 5 40 10
title @a subtitle {"text": "Repite cualquiera: /function escenas_novilis:<nombre>", "color": "#F4E9D8"}
title @a title {"text": "Fin", "color": "#FFC23A"}
effect clear @a
gamemode creative @a
gamerule spawn_mobs true
