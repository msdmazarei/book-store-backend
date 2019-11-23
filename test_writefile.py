from json import  dumps

js = dict(a=1,b=2,c=dict(a=1,b=2))
f=open("/tmp/msd.nsm",'wb')
c=dumps(js)
f.write(c.encode())
f.close()