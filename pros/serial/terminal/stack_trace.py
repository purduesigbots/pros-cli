import subprocess

text = """DATA ABORT EXCEPTION
CURRENT TASK: Display Daemon (PROS)
REGISTERS AT ABORT
 r0: 0x039e0a24  r1: 0x03966b34  r2: 0x00000117  r3: 0x00000000  r4: 0x038000dc  r5: 0x039e08e4  r6: 0x00000001  r7: 0x00000001
 r8: 0x00000001  r9: 0x039e0574 r10: 0x00000000 r11: 0x039d7ca4 r12: 0x000000be  sp: 0x039668c8  lr: 0x0381a484  pc: 0x07800184 

BEGIN STACK TRACE
        0x7800184
        0x381a484
        0x382ae60
        0x381bbe4
        0x381c240
        0x3828718
        0x38288d8
        0x381a098
        0x384b8cc
        0x3845d5c
END OF TRACE
HEAP USED: 6184 bytes
STACK REMAINING AT ABORT: 4234811102 bytes"""

start = text.find("BEGIN STACK TRACE") + 18
end = text.find("END OF TRACE")
addrArray = text[start: end].split()
out = ''
for i, s in enumerate(addrArray):
    out += "    " + s

    def getTrace(s, path):
        temp = subprocess.Popen(['addr2line', '-faps', '-e', path, s],
            stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
        if (temp.find('?') != -1):
            return ' : ??'
        else:
            return ' : ' + temp[15: len(temp)-2]

    out += getTrace(s, "..\..\..\\test-project2\\bin\hot.package.elf")
    out += getTrace(s, "..\..\..\\test-project2\\bin\cold.package.elf")
    out += getTrace(s, "..\..\..\\test-project2\\bin\monolith.elf") + '\n'    
text = text[:start] + out + text[end:]
print(text)
file = open("stack_trace.txt", "w")
file.write(out)
file.close()    