clear @s
gamemode survival @s
effect clear @s
item replace entity @s armor.head with minecraft:netherite_helmet[minecraft:enchantments={"minecraft:protection":4}]
item replace entity @s armor.chest with minecraft:netherite_chestplate[minecraft:enchantments={"minecraft:protection":4}]
item replace entity @s armor.legs with minecraft:netherite_leggings[minecraft:enchantments={"minecraft:protection":4}]
item replace entity @s armor.feet with minecraft:netherite_boots[minecraft:enchantments={"minecraft:protection":4}]
item replace entity @s weapon.mainhand with minecraft:netherite_sword[minecraft:enchantments={"minecraft:sharpness":5}]
item replace entity @s weapon.offhand with minecraft:totem_of_undying
give @s minecraft:totem_of_undying 3
give @s minecraft:enchanted_golden_apple 8
give @s minecraft:golden_apple 16
give @s minecraft:bow[minecraft:enchantments={"minecraft:power":5,"minecraft:infinity":1}]
give @s minecraft:arrow 1
give @s minecraft:torch 8
give @s minecraft:potion[minecraft:potion_contents={potion:"minecraft:water"}] 4
give @s atalaya:huevo_nerea
give @s atalaya:huevo_aeralis
give @s atalaya:huevo_rajang
give @s atalaya:huevo_novilis
effect give @s minecraft:instant_health 1 9 true
effect give @s minecraft:saturation 1 9 true
gamerule spawn_mobs false
time set noon
weather clear
tellraw @s {"text":"[Atalaya] Kit de prueba: netherita Prot IV, 4 totems, manzanas de Notch y los huevos de los 4 jefes. /function escenas_novilis:kit para repetirlo.","color":"#FFC23A"}
