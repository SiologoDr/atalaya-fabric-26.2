execute at @s positioned over motion_blocking_no_leaves run summon minecraft:marker ~ ~ ~ {Tags:["ancla"]}
execute at @s if entity @e[type=minecraft:villager,distance=..70] run tellraw @s {"text":"[Atalaya] Hay aldeanos cerca: Rajang puede ir a por ellos. Mejor lejos del pueblo (/function escenas:parar, alejate y vuelve a empezar).","color":"#E3B341"}
