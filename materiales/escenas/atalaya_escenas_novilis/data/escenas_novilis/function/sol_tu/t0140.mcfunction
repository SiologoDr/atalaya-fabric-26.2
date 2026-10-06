execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run effect clear @a
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run tp @a ~16 ~ ~ facing ~0 ~10 ~0
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run gamemode survival @a
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run function escenas_novilis:armadura
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run item replace entity @a weapon.offhand with minecraft:totem_of_undying
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run effect give @a minecraft:resistance 40 3 true
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run give @a minecraft:potion[minecraft:potion_contents={potion:"minecraft:water"}] 2
