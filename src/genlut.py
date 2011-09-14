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

   "EA" : [ # mode and Xn
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
"ORI"        : [0,0,0,0,0,0,0,0,"S","EA"],
"ANDI to CCR": [0,0,0,0,0,0,1,0,0,0,1,1,1,1,0,0],
"ANDI to SR" : [0,0,0,0,0,0,1,0,0,1,1,1,1,1,0,0],
"ANDI"       : [0,0,0,0,0,0,1,0,"S","EA"],
"SUBI"       : [0,0,0,0,0,1,0,0,"S","EA"],
"RTM"  :[0,0,0,0,0,1,1,0,1,1,0,0,"b","Xn"],
"CALLM":[0,0,0,0,0,1,1,0,1,1,"EA"],
"ADDI"       : [0,0,0,0,0,1,1,0,"S","EA"],
"CMP2/CHK2":[0,0,0,0,0,"S",0,1,1,"EA"], # See Note 1.0
"EORI_to_CCR":[0,0,0,0,1,0,1,0,0,0,1,1,1,1,0,0],
"EORI_to_SR": [0,0,0,0,1,0,1,0,0,1,1,1,1,1,0,0],
"EORI":[0,0,0,0,1,0,1,0,"S","EA"],
"CMPI":[0,0,0,0,1,1,0,0,"S","EA"],
"BTST":[0,0,0,0,1,0,0,0,0,0,"EA"],
"BCHG":[0,0,0,0,1,0,0,0,0,1,"EA"],
"BCLR":[0,0,0,0,1,0,0,0,1,0,"EA"],
"BSET":[0,0,0,0,1,0,0,0,1,1,"EA"],
"MOVES":[0,0,0,0,1,1,1,0,"S","EA"],
"CAS2":[0,0,0,0,1,"S",0,1,1,1,1,1,1,0,0],

}
# Note 1.0: The bits for the first word of CMP2 and CHK2 are the same.
#           We will figure out which one it actually is during the 
#           execute step.

INSTRUCTIONS = []
for i in xrange(2**16):
    INSTRUCTIONS.append( None )

def isstatic( _bits ):
    """Returns true if the bits are all ones and zeroes (no patterns)"""
    for b in _bits:
        if b in PATTERNS:
            return False
    return True

def gen( _bits, _name ):
    
    if isstatic( _bits ):
        # Okay, if all the bits are static (no more variables), that is the recursion termination
        # condition.

        # Let's put the bits into a nice-to-look-at string, and calculate the base-10 value

        bit_string = "".join( [ "%d" % bit for bit in _bits ] )
        bit_value  = int( bit_string, 2 )
        bit_string = bit_string[:8] + " " + bit_string[8:]

        # There was a lot of manual typing in the OPCODES dict above, so
        # let's do some error checking.

        # Before we do anything with this value, we need to be sure it's the correct
        # length, which is two bytes, aka one "word", aka sixteen bits.
        assert  \
            len( _bits ) == 16, \
            "The bit pattern for %s has length %d, when 16 is required." % ( _name, len(_bits) )

        # if there is already a value here, fail with collision message
        assert  \
            INSTRUCTIONS[ bit_value ] == None, \
            "Attempted to add new opcode %s as bit pattern %s, but that pattern already exists for opcode %s."  \
            % ( _name, bit_string, INSTRUCTIONS[ bit_value ] )

        print( "\t%s" % bit_string )

        INSTRUCTIONS[ bit_value ] = _name
        #INSTRUCTIONS.append( [ _bits, _name ] )
        
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
    print( "Generating bit patterns for %s... " % op )
    gen( OPCODES[op], op )
    

for instr in INSTRUCTIONS:
    print(instr)

