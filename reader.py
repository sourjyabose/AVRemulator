class Instruc:
    def __init__(self,name,mask,pattern,handler):
        self.name=name;
        self.mask=mask;
        self.pattern=pattern;
        self.handler=handler;

def rjump(p):
    print("rjump",p);

InstrucTable=[Instruc("rjump",0b1111000000000000,0b1100000000000000,rjump)]

file=open("main.bin","rb")
content=file.read()
i=0;
low=0b0;
high=0b0;
pc=0;
while pc<len(content):
    pass

