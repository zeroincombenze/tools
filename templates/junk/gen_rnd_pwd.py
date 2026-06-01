from random import randint

seed1 = "0123456789abcdefghijklmnopqrstuvwxyz"
seed2 = "A$CDEFGH!JKLMN.PQRSTUVWXY+"
name = input("Name? ")
while name:
    seed = name.lower() + seed1 + name.lower() + seed2 + seed1
    pwd = ""
    for ix in range(10):
        num = randint(0, len(seed))
        pwd += seed[num]
    print(name, "->", pwd)
    name = input("Name? ")

