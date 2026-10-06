execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=minecraft:mannequin,tag=escena]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:estatua_novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:fuente_solar]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:sol_novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:sello_sol]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:onda_fuego]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[type=atalaya:tajo_novilis]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run execute as @e[type=minecraft:slime,distance=..90] run data merge entity @s {Size:0}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run kill @e[distance=..90,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run time set noon
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run weather clear
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run difficulty normal
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run summon atalaya:novilis ~0 ~ ~0 {Rotation:[-90f,0f]}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run summon minecraft:mannequin ~14 ~ ~ {Tags:["escena","cebo"],CustomName:"cebo",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run tp @a ~20 ~7 ~-34 facing ~20 ~6 ~0
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a times 5 40 10
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a subtitle {"text": "Los pies van con el suelo; la capa y el tabardo con el peso", "color": "#F4E9D8"}
execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run title @a title {"text": "El paso", "color": "#FFC23A"}
schedule function escenas_novilis:andar/t0000 45t append
schedule function escenas_novilis:andar/t0060 105t append
schedule function escenas_novilis:andar/t0061 106t append
schedule function escenas_novilis:andar/t0062 107t append
schedule function escenas_novilis:andar/t0063 108t append
schedule function escenas_novilis:andar/t0064 109t append
schedule function escenas_novilis:andar/t0065 110t append
schedule function escenas_novilis:andar/t0066 111t append
schedule function escenas_novilis:andar/t0067 112t append
schedule function escenas_novilis:andar/t0068 113t append
schedule function escenas_novilis:andar/t0069 114t append
schedule function escenas_novilis:andar/t0070 115t append
schedule function escenas_novilis:andar/t0071 116t append
schedule function escenas_novilis:andar/t0072 117t append
schedule function escenas_novilis:andar/t0073 118t append
schedule function escenas_novilis:andar/t0074 119t append
schedule function escenas_novilis:andar/t0075 120t append
schedule function escenas_novilis:andar/t0076 121t append
schedule function escenas_novilis:andar/t0077 122t append
schedule function escenas_novilis:andar/t0078 123t append
schedule function escenas_novilis:andar/t0079 124t append
schedule function escenas_novilis:andar/t0080 125t append
schedule function escenas_novilis:andar/t0081 126t append
schedule function escenas_novilis:andar/t0082 127t append
schedule function escenas_novilis:andar/t0083 128t append
schedule function escenas_novilis:andar/t0084 129t append
schedule function escenas_novilis:andar/t0085 130t append
schedule function escenas_novilis:andar/t0086 131t append
schedule function escenas_novilis:andar/t0087 132t append
schedule function escenas_novilis:andar/t0088 133t append
schedule function escenas_novilis:andar/t0089 134t append
schedule function escenas_novilis:andar/t0090 135t append
schedule function escenas_novilis:andar/t0091 136t append
schedule function escenas_novilis:andar/t0092 137t append
schedule function escenas_novilis:andar/t0093 138t append
schedule function escenas_novilis:andar/t0094 139t append
schedule function escenas_novilis:andar/t0095 140t append
schedule function escenas_novilis:andar/t0096 141t append
schedule function escenas_novilis:andar/t0097 142t append
schedule function escenas_novilis:andar/t0098 143t append
schedule function escenas_novilis:andar/t0099 144t append
schedule function escenas_novilis:andar/t0100 145t append
schedule function escenas_novilis:andar/t0101 146t append
schedule function escenas_novilis:andar/t0102 147t append
schedule function escenas_novilis:andar/t0103 148t append
schedule function escenas_novilis:andar/t0104 149t append
schedule function escenas_novilis:andar/t0105 150t append
schedule function escenas_novilis:andar/t0106 151t append
schedule function escenas_novilis:andar/t0107 152t append
schedule function escenas_novilis:andar/t0108 153t append
schedule function escenas_novilis:andar/t0109 154t append
schedule function escenas_novilis:andar/t0110 155t append
schedule function escenas_novilis:andar/t0111 156t append
schedule function escenas_novilis:andar/t0112 157t append
schedule function escenas_novilis:andar/t0113 158t append
schedule function escenas_novilis:andar/t0114 159t append
schedule function escenas_novilis:andar/t0115 160t append
schedule function escenas_novilis:andar/t0116 161t append
schedule function escenas_novilis:andar/t0117 162t append
schedule function escenas_novilis:andar/t0118 163t append
schedule function escenas_novilis:andar/t0119 164t append
schedule function escenas_novilis:andar/t0120 165t append
schedule function escenas_novilis:andar/t0121 166t append
schedule function escenas_novilis:andar/t0122 167t append
schedule function escenas_novilis:andar/t0123 168t append
schedule function escenas_novilis:andar/t0124 169t append
schedule function escenas_novilis:andar/t0125 170t append
schedule function escenas_novilis:andar/t0126 171t append
schedule function escenas_novilis:andar/t0127 172t append
schedule function escenas_novilis:andar/t0128 173t append
schedule function escenas_novilis:andar/t0129 174t append
schedule function escenas_novilis:andar/t0130 175t append
schedule function escenas_novilis:andar/t0131 176t append
schedule function escenas_novilis:andar/t0132 177t append
schedule function escenas_novilis:andar/t0133 178t append
schedule function escenas_novilis:andar/t0134 179t append
schedule function escenas_novilis:andar/t0135 180t append
schedule function escenas_novilis:andar/t0136 181t append
schedule function escenas_novilis:andar/t0137 182t append
schedule function escenas_novilis:andar/t0138 183t append
schedule function escenas_novilis:andar/t0139 184t append
schedule function escenas_novilis:andar/t0140 185t append
schedule function escenas_novilis:andar/t0141 186t append
schedule function escenas_novilis:andar/t0142 187t append
schedule function escenas_novilis:andar/t0143 188t append
schedule function escenas_novilis:andar/t0144 189t append
schedule function escenas_novilis:andar/t0145 190t append
schedule function escenas_novilis:andar/t0146 191t append
schedule function escenas_novilis:andar/t0147 192t append
schedule function escenas_novilis:andar/t0148 193t append
schedule function escenas_novilis:andar/t0149 194t append
schedule function escenas_novilis:andar/t0150 195t append
schedule function escenas_novilis:andar/t0151 196t append
schedule function escenas_novilis:andar/t0152 197t append
schedule function escenas_novilis:andar/t0153 198t append
schedule function escenas_novilis:andar/t0154 199t append
schedule function escenas_novilis:andar/t0155 200t append
schedule function escenas_novilis:andar/t0156 201t append
schedule function escenas_novilis:andar/t0157 202t append
schedule function escenas_novilis:andar/t0158 203t append
schedule function escenas_novilis:andar/t0159 204t append
schedule function escenas_novilis:andar/t0160 205t append
schedule function escenas_novilis:andar/t0161 206t append
schedule function escenas_novilis:andar/t0162 207t append
schedule function escenas_novilis:andar/t0163 208t append
schedule function escenas_novilis:andar/t0164 209t append
schedule function escenas_novilis:andar/t0165 210t append
schedule function escenas_novilis:andar/t0166 211t append
schedule function escenas_novilis:andar/t0167 212t append
schedule function escenas_novilis:andar/t0168 213t append
schedule function escenas_novilis:andar/t0169 214t append
schedule function escenas_novilis:andar/t0170 215t append
schedule function escenas_novilis:andar/t0171 216t append
schedule function escenas_novilis:andar/t0172 217t append
schedule function escenas_novilis:andar/t0173 218t append
schedule function escenas_novilis:andar/t0174 219t append
schedule function escenas_novilis:andar/t0175 220t append
schedule function escenas_novilis:andar/t0176 221t append
schedule function escenas_novilis:andar/t0177 222t append
schedule function escenas_novilis:andar/t0178 223t append
schedule function escenas_novilis:andar/t0179 224t append
schedule function escenas_novilis:andar/t0180 225t append
schedule function escenas_novilis:andar/t0181 226t append
schedule function escenas_novilis:andar/t0182 227t append
schedule function escenas_novilis:andar/t0183 228t append
schedule function escenas_novilis:andar/t0184 229t append
schedule function escenas_novilis:andar/t0185 230t append
schedule function escenas_novilis:andar/t0186 231t append
schedule function escenas_novilis:andar/t0187 232t append
schedule function escenas_novilis:andar/t0188 233t append
schedule function escenas_novilis:andar/t0189 234t append
schedule function escenas_novilis:andar/t0190 235t append
schedule function escenas_novilis:andar/t0191 236t append
schedule function escenas_novilis:andar/t0192 237t append
schedule function escenas_novilis:andar/t0193 238t append
schedule function escenas_novilis:andar/t0194 239t append
schedule function escenas_novilis:andar/t0195 240t append
schedule function escenas_novilis:andar/t0196 241t append
schedule function escenas_novilis:andar/t0197 242t append
schedule function escenas_novilis:andar/t0198 243t append
schedule function escenas_novilis:andar/t0199 244t append
schedule function escenas_novilis:andar/t0200 245t append
schedule function escenas_novilis:andar/t0201 246t append
schedule function escenas_novilis:andar/t0202 247t append
schedule function escenas_novilis:andar/t0203 248t append
schedule function escenas_novilis:andar/t0204 249t append
schedule function escenas_novilis:andar/t0205 250t append
schedule function escenas_novilis:andar/t0206 251t append
schedule function escenas_novilis:andar/t0207 252t append
schedule function escenas_novilis:andar/t0208 253t append
schedule function escenas_novilis:andar/t0209 254t append
schedule function escenas_novilis:andar/fin 265t append
