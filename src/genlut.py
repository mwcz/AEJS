#!/usr/bin/python

from copy import copy
import sys

# Generate a LUT for all 68k opcodes


# Operands

# Size
PATTERNS = {

    # one bit
    "b" : [ [0],[1], ],

    "S" : [ # size
            [0,0], 
            [0,1], 
            [1,0], ],

  "MXn" : [ # mode and Xn
            [0,0,0,"Xn"],
            [0,0,1,"Xn"],
            [0,1,0,"Xn"],
            [0,1,1,"Xn"],
            [1,0,0,"Xn"],
            [1,0,1,"Xn"],
            [1,1,0,"Xn"],
            [1,1,1,"M111Xn"], ],

   "Xn" : [ # register number
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
            [1,0,1],
            [1,1,0],
            [1,1,1], ],

"M111Xn": [ # the valid register numbers when the addressing mode is (xxx).W or (xxx).L
            [0,0,0],
            [0,0,1], ],

 "COND" : [ # condition
            [0,0,0,0,],
            [0,0,0,1,],
            [0,0,1,0,],
            [0,0,1,1,],
            [0,1,0,0,],
            [0,1,0,1,],
            [0,1,1,0,],
            [0,1,1,1,],
            [1,0,0,0,],
            [1,0,0,1,],
            [1,0,1,0,],
            [1,0,1,1,],
            [1,1,0,0,],
            [1,1,0,1,],
            [1,1,1,0,],
            [1,1,1,1,], ],
}

# Mode and Xn



OPCODES = {
    "ORI to CCR" : [0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0],
    "ORI to SR"  : [0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0],
    "ORI"        : [0,0,0,0,0,0,0,0,"S","MXn"],
    "ANDI to CCR": [0,0,0,0,0,0,1,0,0,0,1,1,1,1,0,0],
    "ANDI to SR" : [0,0,0,0,0,0,1,0,0,1,1,1,1,1,0,0],
    "ANDI"       : [0,0,0,0,0,0,1,0,"S","MXn"],
    "SUBI"       : [0,0,0,0,0,1,0,0,"S","MXn"],
    "ADDI"       : [0,0,0,0,0,1,1,0,"S","MXn"],

}

INSTRUCTIONS = []

def isstatic( _bits ):
    """Returns true if the bits are all ones and zeroes (no patterns)"""
    for b in _bits:
        if b in PATTERNS:
            return False
    return True

def gen( _bits, _name ):
    
    if isstatic( _bits ):
        INSTRUCTIONS.append( [ _bits, _name ] )
        
    i = 0

    while i in range( len( _bits ) ): # strange loop

        b = _bits[i]
        pattern_length = 0

        if b in PATTERNS:
            pat            = PATTERNS[b]
            pattern_length = len( pat )

            for p in pat:
                bits_copy = copy( _bits )
                bits_copy.pop(i)
                bits_copy[i:i] = p
                gen( bits_copy, _name )

        i += pattern_length
        i += 1

    return _bits

for op in OPCODES:
    gen( OPCODES[op], op )
    

for instr in INSTRUCTIONS:
    print(instr)

