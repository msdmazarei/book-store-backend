#!/usr/bin/python

from random import randint
import  sys
from time import sleep
print("sleeping ...")
sleep(10)
r = randint(0,10)
if len(sys.argv)<3:
    print("arguments are invalid")
    sys.exit(2)
if r<50:
    fr=open(sys.argv[1],'rb')
    d=fr.read()
    fr.close()
    fw = open(sys.argv[2],'wb')
    fw.write(d)
    fw.close()

    print("exit successfully")
    sys.exit(0)
else:
    print("exit with failaur")
    sys.exit(1)
