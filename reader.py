print("\n\n\n");

monitorarr=[]
def monitor(b,c):
    monitorarr.append(c)


class stateMachine:
    def __init__(self):
        self.pc=0;
        self.regfile=[0]*32;
        self.spl=0;
        self.sreg=0;
        


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
#----------IO Functions------------------------
        self.funcList[0x3d]=self.setspl;
        self.funcList[0x3f]=self.setsreg
        self.funcList[0x18]=monitor
#---------------------------------------------

    def __getitem__(self,key):
        return self.__ioaddr[key]
    def __setitem__(self,key,value):
        self.__ioaddr[key]=value;
        self.funcList[key](key,value)


    def setspl(self,key,value=0):
        cpu.spl=value;
        print(f"SPL: {cpu.spl}",end="")
    def setsreg(self,key,value=0):
        cpu.sreg=value;
        pass
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

def pop(p):
    cpu.spl+=1
    val=ram[cpu.spl]
    #print("NUM:",val)
    return val

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
    if (offset & 0b0000100000000000) > 0:
        offset-=4096
    
    lowrbyte= cpu.pc&0b0000000011111111
    highbyte=(cpu.pc&0b1111111100000000)>>8
    push(lowrbyte)
    push(highbyte)
    cpu.pc+=2*offset;
    print("RCALL",hex(cpu.pc),end="    ")
    print("");


def ret(p):
    print("RET", end=" ")
    hval=(pop(p)<<8)
    lval=(pop(p))
    cpu.pc=hval|lval
    print("")
    pass;

def sbi(p):
    byteorder=p&0b0000000000000111;
    ioaddr=(p&0b0000000011111000)>>3;
    io_mem[ioaddr]|=1<<byteorder;
    print("SBI",f"B{byteorder}","-S>","IO",hex(ioaddr),)

def setStatFlag(*,carry=0,zero=0,negative=0,overflow=0,sign=0,half_carry=0,transfer_bit=0,interuppt_en=0):
    cpu.sreg|=(1*carry)<<0|(1*zero)<<1|(1*negative)<<2|(1*overflow)<<3|(1*sign)<<4|(1*half_carry)<<5|(1*transfer_bit)<<6|(1*interuppt_en)<<7
def clearStatFlag(*,carry=1,zero=1,negative=1,overflow=1,sign=1,half_carry=1,transfer_bit=1,interuppt_en=1):
    cpu.sreg&=(1*carry)<<0|(1*zero)<<1|(1*negative)<<2|(1*overflow)<<3|(1*sign)<<4|(1*half_carry)<<5|(1*transfer_bit)<<6|(1*interuppt_en)<<7
def getStatFlag(*,carry=0,zero=0,negative=0,overflow=0,sign=0,half_carry=0,transfer_bit=0,interuppt_en=0):
    lst=[carry,zero,negative,overflow,sign,half_carry,transfer_bit,interuppt_en]
    i=0
    for x in lst:
        if x==1:
            break;
        i+=1;
    return ((cpu.sreg&(1<<i))>>i)
def getbit(p,n):
    return (p&(1<<n))>>n

def brne(p):
    offset=(p&(0b0000001111111000))>>3
    if(offset&0b0000000001000000>0):
        offset-=128
        pass
    offset*=2;
    strg="not jumping by"
    if(getStatFlag(zero=1)==0):
        strg="jumping by"
        cpu.pc+=offset;
    print("BRNE",strg,offset)
    pass

def noper(p):
    print("NOP");

def subi(p):
    regi=(((p&0b0000000011110000)|(1<<8))>>4)
    k=(p&0b0000000000001111)|((p&0b0000111100000000)>>4)
    old=cpu.regfile[regi];
    #-------------------------------------
    if(cpu.regfile[regi]<k):
        setStatFlag(carry=1);
        cpu.regfile[regi]|=1<<8
        cpu.regfile[regi]-=k;
        cpu.regfile[regi]&=0xFF
    else:
        cpu.regfile[regi]-=k;
        clearStatFlag(carry=0)
    #-------------------------------------
    #-----------------------------flag setting------------------------------------------------------------------------
    clearStatFlag(half_carry=0);
    clearStatFlag(sign=0);
    
    clearStatFlag(negative=0);
    clearStatFlag(overflow=0);
    z=getStatFlag(zero=1)
    clearStatFlag(zero=0);
    
    setStatFlag(half_carry=( ( (not getbit(old,3)) and getbit(k,3) ) or ( getbit(cpu.regfile[regi],3) and getbit(k,3) ) or (getbit(cpu.regfile[regi],3) and (not getbit(old,3))  )   ))
    setStatFlag(
    carry=
    (
        ((not getbit(old,7)) and getbit(k,7))
        or
        (getbit(cpu.regfile[regi],7) and getbit(k,7))
        or
        (getbit(cpu.regfile[regi],7) and (not getbit(old,7)))
    )
)

    # N
    setStatFlag(
        negative=getbit(cpu.regfile[regi],7)
    )

    # V
    setStatFlag(
        overflow=
        (
            (getbit(old,7) and (not getbit(k,7)) and (not getbit(cpu.regfile[regi],7)))
            or
            ((not getbit(old,7)) and getbit(k,7) and getbit(cpu.regfile[regi],7))
        )
    )

    # S = N xor V
    setStatFlag(
        sign=
        (
            getbit(cpu.regfile[regi],7)
            ^
            (
                (getbit(old,7) and (not getbit(k,7)) and (not getbit(cpu.regfile[regi],7)))
                or
                ((not getbit(old,7)) and getbit(k,7) and getbit(cpu.regfile[regi],7))
            )
        )
    )

    # Z
    setStatFlag(
        zero=(cpu.regfile[regi] == 0)) 


    print("SUBI",f"R{regi} - {k} = {cpu.regfile[regi]}")
    pass
#------------------------------------------------------------------------------------------------------------------------------------------------


def sbci(p):
    regi=(((p&0b0000000011110000)|(1<<8))>>4)
    k=(p&0b0000000000001111)|((p&0b0000111100000000)>>4)
    old=cpu.regfile[regi];
    #-------------------------------------
    if(cpu.regfile[regi]<k+getStatFlag(carry=1)):
        
        cpu.regfile[regi]|=1<<8
        cpu.regfile[regi]-=k+getStatFlag(carry=1);
        cpu.regfile[regi]&=0xFF
        setStatFlag(carry=1);
    else:
        cpu.regfile[regi]-=k+getStatFlag(carry=1);
        clearStatFlag(carry=0)
    #-------------------------------------
    clearStatFlag(half_carry=0);
    clearStatFlag(sign=0);
    
    clearStatFlag(negative=0);
    clearStatFlag(overflow=0);
    z=getStatFlag(zero=1)
    clearStatFlag(zero=0);
    
    setStatFlag(half_carry=( ( (not getbit(old,3)) and getbit(k,3) ) or ( getbit(cpu.regfile[regi],3) and getbit(k,3) ) or (getbit(cpu.regfile[regi],3) and (not getbit(old,3))  )   ))
    setStatFlag(
    carry=
    (
        ((not getbit(old,7)) and getbit(k,7))
        or
        (getbit(cpu.regfile[regi],7) and getbit(k,7))
        or
        (getbit(cpu.regfile[regi],7) and (not getbit(old,7)))
    )
)

    # N
    setStatFlag(
        negative=getbit(cpu.regfile[regi],7)
    )

    # V
    setStatFlag(
        overflow=
        (
            (getbit(old,7) and (not getbit(k,7)) and (not getbit(cpu.regfile[regi],7)))
            or
            ((not getbit(old,7)) and getbit(k,7) and getbit(cpu.regfile[regi],7))
        )
    )

    # S = N xor V
    setStatFlag(
        sign=
        (
            getbit(cpu.regfile[regi],7)
            ^
            (
                (getbit(old,7) and (not getbit(k,7)) and (not getbit(cpu.regfile[regi],7)))
                or
                ((not getbit(old,7)) and getbit(k,7) and getbit(cpu.regfile[regi],7))
            )
        )
    )

    # Z
    setStatFlag(
        zero=(cpu.regfile[regi] == 0) and z) 
    

    print("SBCI",f"R{regi} - {k} = {cpu.regfile[regi]}")
    pass

def sbiw(p):
    k=(((p&0b0000000011000000)>>2)|(p&0b0000000000001111))
    r=2*((p&0b0000000000110000)>>4)+24
    hval=cpu.regfile[r+1];
    lval=cpu.regfile[r];
    val=(hval<<8)|lval
    oldval=val;
    val-=k;
    val&=0xFFFF
    hval=(val&0b1111111100000000)>>8
    lval=(val&0b0000000011111111)
    cpu.regfile[r+1]=hval;
    cpu.regfile[r]=lval;
    clearStatFlag(sign=0);
    clearStatFlag(negative=0);
    clearStatFlag(overflow=0);
    clearStatFlag(zero=0);
    clearStatFlag(carry=0);

    setStatFlag(
        carry=
        (
            getbit(val,15)
            and
            (not getbit(oldval,15))
        )
    );

    setStatFlag(
        negative=getbit(val,15)
    );

    setStatFlag(
        overflow=
        (
            getbit(val,15)
            and
            (not getbit(oldval,15))
        )
    );

    setStatFlag(
        sign=
        (
            getbit(val,15)
            ^
            (
                getbit(val,15)
                and
                (not getbit(oldval,15))
            )
        )
    );

    setStatFlag(
        zero=((val & 0xFFFF) == 0)
    );

    print(f"SBIW R{r+1}:{r} - {k}")
    pass

def cpi(p):
    pass


InstrucTable=[Instruc("rjump",0b1111000000000000,0b1100000000000000,rjump),
              Instruc("eor",0b1111110000000000,0b0010010000000000,eor),
              Instruc("out",0b1111100000000000,0b1011100000000000,out),
              Instruc("in",0b1111100000000000,0b1011000000000000,inp),
              Instruc("ldi",0b1111000000000000,0b1110000000000000,ldi),
              Instruc("rcall",0b1111000000000000,0b1101000000000000,rcall),
              Instruc("sbi",0b1111111100000000,0b1001101000000000,sbi),
              Instruc("subi",0b1111000000000000,0b0101000000000000,subi),
              Instruc("sbci",0b1111000000000000,0b0100000000000000,sbci),
              Instruc("brne",0b1111110000000111,0b1111010000000001,brne),
              Instruc("sbiw",0b1111111100000000,0b1001011100000000,sbiw),
              Instruc("nop",0b1111111111111111,0b0000000000000000,noper),
              Instruc("ret",0b1111111111111111,0b1001010100001000,ret),
              Instruc("cpi",0b1111000000000000,0b0011000000000000,cpi)]


print("Total Instructions:",len(InstrucTable),"\n\n")
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
            print(hex(cpu.pc).ljust(6),end=" ")
            cpu.pc+=2;
            ins.handler(result);
        elif flag==1:
            break;
    if flag==1:
        flag=0;
    else:
        print("\nExecution Halted\n\n\n")
        print(monitorarr,len(monitorarr))
        break;

    



