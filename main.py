#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BFRES \"Embedded Files\" Extractor
# Version 0.1
# Copyright © 2017 Stella/AboodXD

import os, struct
import tkinter as tk
from tkinter import filedialog


def find_name(f, name_pos):
    name = b""
    char = f[name_pos:name_pos + 1]
    i = 1

    while char != b"\x00":
        name += char
        if name_pos + i == len(f): break  # Prevent it from looping forever
        
        char = f[name_pos + i:name_pos + i + 1]
        i += 1

    return(name.decode("utf-8"))


def main():
    print("BFRES \"Embedded Files\" Extractor v0.1")
    print("(C) 2017 Stella/AboodXD")

    root = tk.Tk()
    root.withdraw()
    
    filetypes = [('BFRES files', '.bfres')]
    filename = filedialog.askopenfilename(filetypes=filetypes)

    if filename:
        with open(filename, "rb") as inf:
            inb = inf.read()
            inf.close()

        wiiu = False
        switch = False

        if inb[:8] == b'FRES    ':
            switch = True

        elif inb[:4] == b'FRES':
            wiiu = True

        if wiiu:
            print("")
            print("Wii U BFRES detected!")
            bom = ">" if inb[8:0xA] == b'\xFE\xFF' else "<" # Usually ">"

            endianness = {">": "Big", "<": "Little"}
            print("Endianness: " + endianness[bom])

            pos = struct.unpack(bom + "i", inb[0x4C:0x50])[0]

            pos += 0x4C
            size = struct.unpack(bom + "I", inb[pos:pos+4])[0]
            count = struct.unpack(bom + "i", inb[pos+4:pos+8])[0]

            if pos - 0x4C:
                print("")
                print("File count: " + str(count))
            

                for i in range(count + 1):
                    name_pos = struct.unpack(bom + "i", inb[pos+16+(0x10*i):pos+20+(0x10*i)])[0]
                    data_pos = struct.unpack(bom + "i", inb[pos+20+(0x10*i):pos+24+(0x10*i)])[0]

                    if data_pos in [0, 0xFFFFFFFF]:
                        name = ""

                    else:
                        name_pos += pos + 8 + (0x10*i) + 8
                        data_pos += pos + 8 + (0x10*i) + 12

                        pos = data_pos
                        data_pos = struct.unpack(bom + "i", inb[pos:pos+4])[0] + pos
                        dataSize = struct.unpack(bom + "I", inb[pos+4:pos+8])[0]

                        data = inb[data_pos:data_pos + dataSize]

                        name = find_name(inb, name_pos)
                    
                        print("")
                        print("File " + str(i) + " offset:       " + hex(data_pos))
                        print("File " + str(i) + " size:         " + str(dataSize))
                        print("File " + str(i) + " name offset:  " + hex(name_pos))
                        print("File " + str(i) + " name:         " + name)

                        folder = os.path.dirname(os.path.abspath(filename))
                        with open(folder + "/" + name, "wb+") as output:
                            output.write(data)

            else:
                print("")
                print("No Embedded files found.")

        elif switch:
            print("")
            print("Switch BFRES detected!")
            bom = ">" if inb[0xC:0xE] == b'\xFE\xFF' else "<" # Usually "<"

            endianness = {">": "Big", "<": "Little"}
            print("Endianness: " + endianness[bom])

            startoff = struct.unpack(bom + "q", inb[0x98:0xA0])[0]
            count = struct.unpack(bom + "q", inb[0xC8:0xD0])[0]

            if not count:
                print("")
                print("No Embedded files found.")

            else:
                # Not sure if this is correct, I hope it is.
                # If you face any problems, try replacing "0x20" with "0x10 * count".
                namesoff = struct.unpack(bom + "q", inb[0xA0:0xA8])[0] + 0x20

                print("")
                print("File count: " + str(count))

                for i in range(count):
                    fileoff = struct.unpack(bom + "q", inb[startoff + i * 16:startoff + 8 + i * 16])[0]
                    dataSize = struct.unpack(bom + "q", inb[startoff + 8 + i * 16:startoff + 16 + i * 16])[0]

                    print("")
                    print("File " + str(i+1) + " offset:       " + hex(fileoff))
                    print("File " + str(i+1) + " size:         " + str(dataSize))

                    data = inb[fileoff:fileoff + dataSize]

                    nameoff = struct.unpack(bom + "q", inb[namesoff + i * 16:namesoff + 8 + i * 16])[0]

                    print("File " + str(i+1) + " name offset:  " + hex(nameoff))

                    nameSize = struct.unpack(bom + 'H', inb[nameoff:nameoff + 2])[0]
                    name = inb[nameoff + 2:nameoff + 2 + nameSize].decode('utf-8')

                    print("File " + str(i+1) + " name:         " + name)

                    folder = os.path.dirname(os.path.abspath(filename))
                    with open(folder + "/" + name, "wb+") as output:
                        output.write(data)

        else:
            print("Unable to recognize the BFRES file!")


if __name__ == '__main__': main()
