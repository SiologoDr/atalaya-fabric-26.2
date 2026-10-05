execute as @e[type=minecraft:mannequin,tag=cebo] at @s run tp @s ~0.33 ~ ~
scoreboard players remove #cebo escenas 1
execute if score #cebo escenas matches 1.. run schedule function escenas:paso/cebo 1t replace
