tellraw @a "FOTO presenta_nerea_12_lejos"
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run damage @e[type=atalaya:nerea,limit=1,sort=nearest] 1000000 minecraft:out_of_world
schedule function escenas_novilis:presenta_nerea_11_corazones_vuelve 120t replace
