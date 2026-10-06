execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run kill @e[type=atalaya:nerea]
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run kill @e[type=atalaya:ola_nerea]
title @a times 5 40 10
title @a subtitle {"text": "Repite cualquiera: /function escenas_nerea:<nombre>", "color": "#E4ECF8"}
title @a title {"text": "Fin", "color": "#7FE6F2"}
gamemode creative @a
gamerule spawn_mobs true
