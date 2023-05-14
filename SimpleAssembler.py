from params import *
from errors import *

#LINE COUNT ME JHOL HAI!!!!!!
lineCount = 0  # Counting number of lines entered till now
lines = [] #List where commads readd from file are stored
variables = []
commands = []
cmd_list = []
labels = {}
instrn_count = 0

f=open("input_file.txt","r")
cmd_list=f.readlines()
cmd_list = [line.strip() for line in cmd_list]
f.close()
print(cmd_list) #Extra

def splitter():
    parentstr = ""

    if len(cmd_list) > 128: 
       print("Lines exceed 128")
       exit()

    flagVarOver = 0
    for i in range(0,len(cmd_list)):
        line=cmd_list[i].split()
        #checking for variable validity
        if line[0] == "var":
            if len(line) == 2:
                if flagVarOver: 
                    print(f"Error: Variables found after the beginning")
                    exit()
                else:
                    var = line[1]
                    if duplicateVar(var,variables):
                        print(f"Error: Duplicate variable name: {var}")
                        exit()
                    else:
                        if varNameValidity(var):
                            variables.append(var)
                            continue
                        else:
                            exit()
            else:
                print(f"General Syntax Error in line {i+1}: ")
                exit()
        else:
            flagVarOver = 1 #1 = True
        #checking for label validity        
        if line[0][-1] == ":": #IMP - Label Main Code Me Handle?
            if not labelValidity(line[0][:-1]):
                exit()
            else:
                labels[line[0][:-1]] = i - len(variables) #Yeh kya hai?
                continue
            
    #checking for validity of other commands
    for cmd in lines[len(variables) :]:
        if ":" in cmd: #Check this alag se!
            cmd1 = cmd.split(":")[1].strip()
            if isValidCmd(cmd1):
                if isLineValid(cmd1): 
                    commands.append(cmd1)
                else:
                    print(f"General Syntax Error on line {lineCount+1}: {cmd}")
                    exit()
            else:
                print(f"General Syntax Error on line {lineCount+1}: {cmd}")
                exit()
        elif isValidCmd(cmd):
            if isLineValid(cmd): #IMP, check this functions in errors.py
                commands.append(cmd)
            else:
                print(f"General Syntax Error on line {lineCount+1}: {cmd}")
                exit()
        else:
            print("Error: Invalid Command on line " + str(lineCount + 1) + ": " + cmd)
            exit()
    
    for cmd in lines[len(variables) :]:
        if (cmd[0] == "ld") or (cmd[0] == "st"):
            if cmd[-1] not in variables:
                print("Error: Invalid Command: Variable Does NOT Exist " + str(lineCount + 1) + ": " + cmd)
                exit()
    
    hltCount = 0
    #checking for halt commands
    for c in commands:
        if c == "hlt":
            hltCount += 1

    if hltCount > 1:
        print("Error: More than one hlt instruction found")
        exit()
    elif hltCount == 0:
        print("Error: No hlt instruction found")
        exit()
    elif commands[-1]!="hlt":
        print("Error: hlt should be the last command")
    else:
        for key in labels.keys(): 
            labels[key] = make_7bit_binary(labels[key])

    #Calling main function        
    for i in range(0,len(cmd_list)):
        line=cmd_list[i].split()
        parentstr += assembleOut(line) + "\n"       
    print("ALL Gud - ",parentstr) #EXTRA
    return parentstr

def make_7bit_binary(num):
    con_num = []
    while num >= 1:
        rem = num % 2
        con_num.append(str(int(rem)))
        num = num // 2
    con_num = con_num[::-1]
    bin = "".join(con_num)
    if len(bin) < 7:
        bin = "0" * (7 - len(bin)) + bin
    return bin

def typeA(cmd): #the same list given to "assembleOut" is given here
    strout = ""
    strout += opcode[cmd[0]][0]
    strout += "00"
    r1 = registersF[cmd[1]]
    r2 = registersF[cmd[2]]
    r3 = registersF[cmd[3]]
    strout += r1 + r2 + r3
    return strout

def typeB(cmd): #the same list given to "assembleOut" is given here
    strout = ""
    if cmd[0] == "mov":
        strout += opcode[cmd[0]][0][0]
    else:
        strout += opcode[cmd[0]][0]
    strout += "0"
    r1 = registersF[cmd[1]]
    strout += r1
    imm = cmd[2][1:] #as 0 is $
    immbin = make_7bit_binary(int(imm))
    strout += immbin
    return strout

def typeC(cmd): #the same list given to "assembleOut" is given here
    strout = ""
    if cmd[0] == "mov":
        strout += opcode[cmd[0]][1][0]
    else:
        strout += opcode[cmd[0]][0]
    strout += "00000"
    r1 = registersF[cmd[1]]
    strout += r1
    r2 = registersF[cmd[2]]
    strout += r2
    return strout

def typeD(cmd): #the same list given to "assembleOut" is given here
    strout = ""
    if cmd[-1] in variables:
            for i in range(len(variables)):
                if variables[i] == cmd[-1]:
                    ind = i + len(commands) - 1 
                    break
            mem_addr = instrn_count + (ind + 1)
            bin_mem_addr = make_7bit_binary(mem_addr)
            strout = opcode[cmd[0]][0] + "0" + registersF[cmd[1]] + bin_mem_addr
    else:
        pass 
    return strout

def typeE(cmd): #the same list given to "assembleOut" is given here
    if cmd[-1] in variables:
        for i in range(len(variables)):
            if variables[i] == cmd[-1]:
                ind = i + len(commands) - 1 
                break
    mem_addr = instrn_count + (ind + 1)
    bin_mem_addr = make_7bit_binary(mem_addr)
    strout = ""
    strout += opcode[cmd[0]][0]
    strout += "0000"
    strout += bin_mem_addr
    return strout

def typeF(cmd): #the same list given to "assembleOut" is given here
    strout = ""
    strout = opcode[cmd[0]][0] + "00000000000"
    return strout

def assembleOut(cmd):
    #if encountered type is A
    typeA_ins = ["add", "sub", "mul", "xor", "or", "and"]
    if (cmd[0] in typeA_ins): return typeA(cmd)

    #if encountered type is B
    typeB_ins = ["mov", "rs", "ls"]
    if((cmd[0] in typeB_ins) and ('$' in cmd[2])): return typeB(cmd)

    #if encountered type is C
    typeC_ins = ["mov", "div", "not", "cmp"]
    if (cmd[0] in typeC_ins): return typeC(cmd)

    #if encountered type is D
    typeD_ins = ["ld", "st"]
    if (cmd[0] in typeD_ins): return typeD(cmd)

    #if encountered type is E
    typeE_ins = ["jmp", "jlt", "jgt", "je"]
    if (cmd[0] in typeE_ins): return typeE(cmd)

    #if encountered type is F
    typeF_ins = ["hlt"]
    if (cmd[0] in typeF_ins): return typeF(cmd)

splitter()