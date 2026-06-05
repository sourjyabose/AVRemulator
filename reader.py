class stateMachine:
    def __init__(self):
        self.pc=0;
        self.regfile=[0]*32;
        


class memory:
    def __init__(self,):
        self.mem=[0]*(159-95)
    def __getitem__(self,key):
        if key>=69 and key<=159:
            print("Accessing Memory",key)
            return self.mem[key-69]
        

class io:
    def __init__(self):
        self.__ioaddr=[0]*(95-31);
    def __getitem__(self,key,value):
        return self.__ioaddr[key]
    def __setitem__(self,key,value):
        self.__ioaddr[key]=value;


class Instruc:
    def __init__(self,name,mask,pattern,handler):
        self.name=name;
        self.mask=mask;
        self.pattern=pattern;
        self.handler=handler;

cpu=stateMachine();
io_mem=io();
def rjump(p):
    res=p&0b0000111111111111;
    res*=2;
    
    cpu.pc+=res;
    print("RJUMP by",res,"To",hex(cpu.pc));

def eor(p):
    destReg=(p&0b0000000111110000)>>4
    srcReg=(p&0b0000000000001111)|((p&0b0000001000000000)>>5)
    cpu.regfile[destReg]=cpu.regfile[destReg]^cpu.regfile[srcReg]
    print("EOR","R"+str(destReg)+" ^ R"+str(srcReg));


def out(p):
    srcReg=(p&0b0000000111110000)>>4
    ioport=(p&0b0000000000001111)|((p&0b0000011000000000)>>5)
    io_mem[ioport]=cpu.regfile[srcReg];
    print("OUT",f"R{srcReg} ->",hex(ioport));

def ldi(p):
    reg=(p&0b0000000111110000)>>4;
    constant=()
    pass

InstrucTable=[Instruc("rjump",0b1111000000000000,0b1100000000000000,rjump),
              Instruc("eor",0b1111110000000000,0b0010010000000000,eor),
              Instruc("out",0b1111100000000000,0b1011100000000000,out),
              Instruc("ldi",0b1111000000000000,0b1110000000000000,ldi)]

file=open("main.bin","rb")
content=file.read()
i=0;
low=0b0;
high=0b0;

while cpu.pc<len(content):
    low=content[cpu.pc];
    high=content[cpu.pc+1];
    result=((high<<8) | low);
    for ins in InstrucTable:
        if (ins.mask & result) == ins.pattern:
            cpu.pc+=2;
            ins.handler(result);
    



