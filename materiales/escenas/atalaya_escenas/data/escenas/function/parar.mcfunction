scoreboard players set #recorrido escenas 0
scoreboard players set #cebo escenas 0
schedule clear escenas:paso/cebo
schedule clear escenas:paso/montar
schedule clear escenas:garra/montar
schedule clear escenas:terremoto/montar
schedule clear escenas:embestida/montar
schedule clear escenas:estampado/montar
schedule clear escenas:tumba/montar
schedule clear escenas:sello/montar
schedule clear escenas:furia/montar
schedule clear escenas:cataclismo/montar
schedule clear escenas:paso/fin
schedule clear escenas:garra/fin
schedule clear escenas:terremoto/fin
schedule clear escenas:embestida/fin
schedule clear escenas:estampado/fin
schedule clear escenas:tumba/fin
schedule clear escenas:sello/fin
schedule clear escenas:furia/fin
schedule clear escenas:cataclismo/fin
schedule clear escenas:paso/t0000
schedule clear escenas:paso/t0030
schedule clear escenas:paso/t0085
schedule clear escenas:paso/t0130
schedule clear escenas:paso/t0160
schedule clear escenas:garra/t0000
schedule clear escenas:garra/t0002
schedule clear escenas:garra/t0020
schedule clear escenas:garra/t0030
schedule clear escenas:terremoto/t0000
schedule clear escenas:terremoto/t0048
schedule clear escenas:embestida/t0000
schedule clear escenas:embestida/t0002
schedule clear escenas:embestida/t0014
schedule clear escenas:embestida/t0030
schedule clear escenas:embestida/t0040
schedule clear escenas:embestida/t0058
schedule clear escenas:estampado/t0000
schedule clear escenas:estampado/t0038
schedule clear escenas:estampado/t0090
schedule clear escenas:tumba/t0000
schedule clear escenas:tumba/t0070
schedule clear escenas:tumba/t0122
schedule clear escenas:sello/t0000
schedule clear escenas:sello/t0220
schedule clear escenas:sello/t0230
schedule clear escenas:sello/t0265
schedule clear escenas:sello/t0280
schedule clear escenas:sello/t0300
schedule clear escenas:sello/t0303
schedule clear escenas:furia/t0000
schedule clear escenas:furia/t0030
schedule clear escenas:furia/t0042
schedule clear escenas:furia/t0060
schedule clear escenas:cataclismo/t0000
schedule clear escenas:cataclismo/t0084
schedule clear escenas:cataclismo/t0165
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[type=atalaya:rajang]
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run execute as @e[type=minecraft:slime,distance=..72] run data merge entity @s {Size:0}
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run kill @e[distance=..72,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run fill ~13 ~ ~-6 ~14 ~7 ~6 minecraft:air replace minecraft:stone_bricks
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run time set noon
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run weather clear
execute at @e[type=minecraft:marker,tag=ancla,limit=1] run difficulty normal
kill @e[type=minecraft:marker,tag=ancla]
gamerule spawn_mobs true
gamemode creative @a
