execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[type=atalaya:aeralis]
execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute if score #recorrido escenas_aeralis matches 1 run function escenas_aeralis:aleteo/montar
execute unless score #recorrido escenas_aeralis matches 1 run gamemode creative @a
execute unless score #recorrido escenas_aeralis matches 1 run gamerule spawn_mobs true
