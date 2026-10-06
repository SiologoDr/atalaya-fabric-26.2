execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run kill @e[type=atalaya:nerea]
execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run kill @e[type=atalaya:ola_nerea]
execute if score #recorrido escenas_nerea matches 1 run function escenas_nerea:geiser/montar
execute unless score #recorrido escenas_nerea matches 1 run gamemode creative @a
execute unless score #recorrido escenas_nerea matches 1 run gamerule spawn_mobs true
