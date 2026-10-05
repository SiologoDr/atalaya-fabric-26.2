execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[type=atalaya:rajang]
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute if score #recorrido escenas matches 1 run function escenas:embestida/montar
execute unless score #recorrido escenas matches 1 run gamemode creative @a
execute unless score #recorrido escenas matches 1 run gamerule spawn_mobs true
