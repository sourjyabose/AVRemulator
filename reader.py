print("\n\n\n");



class stateMachine:
    def __init__(self):
        self.pc=0;
        self.regfile=[0]*32;
        self.spl=0;
        


class memory:
    def __init__(self,):
        self.mem=[0]*(159-95)
    def __getitem__(self,key):
        if key>=96 and key<=159:
            print("Get Memory",hex(key),end="    ")
            return self.mem[key-96]
    def __setitem__(self,key,value):
        if key>=96 and key<=159:
            print("NUM:",value,"->","Memory",hex(key),end="    ")
            self.mem[key-96]=value;   

class io:
    def __init__(self):
        self.__ioaddr=[0]*(95-31);
        self.funcList=[self.noop]*(95-31);
        self.funcList[0x3d]=self.setspl;
    def __getitem__(self,key):
        return self.__ioaddr[key]
    def __setitem__(self,key,value):
        self.__ioaddr[key]=value;
        self.funcList[key](key,value)
    def setspl(self,key,value):
        cpu.spl=value;
        print(f"SPL: {cpu.spl}",end="")
    def noop(self,key,value):
        pass
        


class Instruc:
    def __init__(self,name,mask,pattern,handler):
        self.name=name;
        self.mask=mask;
        self.pattern=pattern;
        self.handler=handler;

cpu=stateMachine();
ram=memory()
io_mem=io();

def push(p):
    ram[cpu.spl]=p;
    cpu.spl-=1;

def rjump(p):
    res=p&0b0000111111111111;
    if (res & 0b0000100000000000) > 0:
        res-=4096
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
    print("OUT",f"R{srcReg} -> IO",hex(ioport),end="   ");
    io_mem[ioport]=cpu.regfile[srcReg];
    print("");
    
def inp(p):
    srcReg=(p&0b0000000111110000)>>4
    ioport=(p&0b0000000000001111)|((p&0b0000011000000000)>>5)
    print("IN",f"R{srcReg} <- IO",hex(ioport),end="   ");
    cpu.regfile[srcReg]=io_mem[ioport];
    print("");

def ldi(p):
    reg=((p&0b0000000011110000)>>4)+16;
    constant=((p&0b0000111100000000)>>4)|(p&0b0000000000001111)
    print(f"LDI     NUM: {constant} -> R{reg}")
    cpu.regfile[reg]=constant


def rcall(p):
    offset=(p&0b0000111111111111)
    cpu.pc+=2*offset;
    print("RCALL",hex(cpu.pc),end="    ")
    lowrbyte=cpu.pc&0b0000000011111111
    highbyte=(cpu.pc&0b1111111100000000)>>8
    push(lowrbyte)
    push(highbyte)
    print("");

def sbi(p):
    byteorder=p&0b0000000000000111;
    ioaddr=(p&0b0000000011111000)>>3;
    io_mem[ioaddr]|=1<<byteorder;
    print("SBI",f"B{byteorder}","-S>","IO",hex(ioaddr),)
    



InstrucTable=[Instruc("rjump",0b1111000000000000,0b1100000000000000,rjump),
              Instruc("eor",0b1111110000000000,0b0010010000000000,eor),
              Instruc("out",0b1111100000000000,0b1011100000000000,out),
              Instruc("in",0b1111100000000000,0b1011000000000000,inp),
              Instruc("ldi",0b1111000000000000,0b1110000000000000,ldi),
              Instruc("rcall",0b1111000000000000,0b1101000000000000,rcall),
              Instruc("sbi",0b1111111100000000,0b1001101000000000,sbi)]

file=open("main.bin","rb")
content=file.read()
i=0;
low=0b0;
high=0b0;

while cpu.pc<len(content):
    low=content[cpu.pc];
    high=content[cpu.pc+1];
    result=((high<<8) | low);
    flag=0
    for ins in InstrucTable:
        if (ins.mask & result) == ins.pattern:
            flag=1;
            cpu.pc+=2;
            ins.handler(result);
        elif flag==1:
            break;
    if flag==1:
        flag=0;
    else:
        print("\nExecution Halted\n\n\n")
        break;

    



