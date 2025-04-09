import random
import os
import subprocess
import json
import re

datos = []

next_json_value = 181
n = 1000

numbers = [ f"numbers/{i}" for i in os.listdir("numbers") ]
symbols = [ f"symbols/{i}" for i in os.listdir("symbols") ]

first = []
second = []

for _ in range(n):
    first = []
    second = []
    
    for _ in range(random.randint(1,2)):
        first.append(random.choice(numbers))
    
    op = random.choice(symbols)
    
    for _ in range(random.randint(1,2)):
        second.append(random.choice(numbers))
    
    filename = f"img_{next_json_value}.png"

    subprocess.run(f"magick -gravity center {" ".join(first)} {op} {" ".join(second)} +append -resize 540x98 -extent 640x128 ./operations/{filename}".split())
    
    s0 = "".join(list(map(lambda x: x[0], f"{" ".join(first)}".replace("numbers/", "").split())))
    s1 = re.findall("plus|slash|minus", op.replace("symbols/", ""))
    c = '\0'
    if s1[0] == "plus":
        c = '+'
    elif s1[0] == "minus":
        c = '-'
    else:
        c = '/'

    s2 = "".join(list(map(lambda x: x[0], f"{" ".join(second)}".replace("numbers/", "").split())))
    
    operacion = f"{s0}{c}{s2}"
    
    sub1 = s0
    sub2 = s2
    
    if s0[0] == '0' and len(s0) > 1:
        sub1 = f"{s0[1]}"
    if s2[0] == '0' and len(s2) > 1:
        sub2 = f"{s2[1]}"

    if c == '/' and sub2 == "0":
        continue
    
    resultado = eval(f"{sub1}{c}{sub2}")
    
    datos.append({
        "imagen": filename,
        "operacion": operacion,
        "resultados": {
            "primer_numero": int(s0),
            "segundo_numero": int(s2),
            "operacion": f"{c}",
            "resultado": resultado
        }
    })

    next_json_value += 1

with open("datos.json", "w") as f:
    f.write(str(datos))
