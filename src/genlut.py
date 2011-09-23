#!/usr/bin/python

from copy import deepcopy
import sys

# Generate a LUT for all 68k opcodes

# Yes, this is in Python.  Yes, AEJS is a JavaScript project.
# 
# I am still not sure if the LUT is something that will be 
# generated once and served up statically, or if generation
# will be fast enough that it can be generated at launch-time.
# 
# If generation of the LUT is fast enough, I'll port this
# code into JavaScript and run it at launch.
# 
# If it needs to be served up statically, I'll simply take 
# the output from the Python script and regex it into a 
# JavaScript array.

#**************************
#
# Common patterns
#
#**************************

COMMON_PATTERNS = {#{{{
    # one bit
    "b" : { "length" : 1,
            "bits":
          [ [0],[1], ],
          },

    "S" : { "length" : 2,
            "bits":
          [ # size
            [0,0], 
            [0,1], 
            [1,0], ]
          },

   # A register number, 0 through 7
   "Xn" : { "length" : 3,
            "bits":
          [ # register number
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
            [1,0,1],
            [1,1,0],
            [1,1,1], ]
          },


}#}}}

#**************************
#
# Operand patterns
#
#**************************

PATTERNS = {#{{{

"OPMODE": { "length" : 3, 
            "bits":
          [ # used in MOVEP, and perhaps other ops
            [1,0,0],
            [1,0,1],
            [1,1,0],
            [1,1,1], ]
          },

 "COND" : { "length" : 4,
            "bits":
          [ # condition
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
            [1,1,1,1,], ]
          },

# ORI {{{

"ORI_S" : { "length" : 2,
            "bits":
          [ # condition
            [0,0],
            [0,1],
            [1,0], ]
          },

"ORI_EA" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0,"Xn"],
            [0,1,0,"Xn"],
            [0,1,1,"Xn"],
            [1,0,0,"Xn"],
            [1,0,1,"Xn"],
            [1,1,0,"Xn"],
            [1,1,1,"ORI_ABS_REG" ],
          ]
          },

# The register number when the addressing mode is absolute (Mode 111)
"ORI_ABS_REG" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0],
            [0,0,1],
          ]
          },#}}}
# ANDI {{{

"ANDI_S" : { "length" : 2,
            "bits":
          [ # condition
            [0,0],
            [0,1],
            [1,0], ]
          },

"ANDI_EA" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0,"Xn"],
            [0,1,0,"Xn"],
            [0,1,1,"Xn"],
            [1,0,0,"Xn"],
            [1,0,1,"Xn"],
            [1,1,0,"Xn"],
            [1,1,1,"ANDI_ABS_REG" ],
          ]
          },

# The register number when the addressing mode is absolute (Mode 111)
"ANDI_ABS_REG" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0],
            [0,0,1],
          ]
          },#}}}
# SUBI {{{

"SUBI_S" : { "length" : 2,
            "bits":
          [ # condition
            [0,0],
            [0,1],
            [1,0], ]
          },

"SUBI_EA" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0,"Xn"],
            [0,1,0,"Xn"],
            [0,1,1,"Xn"],
            [1,0,0,"Xn"],
            [1,0,1,"Xn"],
            [1,1,0,"Xn"],
            [1,1,1,"SUBI_ABS_REG" ],
          ]
          },

# The register number when the addressing mode is absolute (Mode 111)
"SUBI_ABS_REG" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0],
            [0,0,1],
          ]
          },#}}}
# RTM {{{
"RTM_b" : COMMON_PATTERNS["b"],
"RTM_Xn" : COMMON_PATTERNS["Xn"],
          #}}}
# CALLM {{{

"CALLM_EA" : { "length" : 3,
            "bits":
          [ # condition
            [0,1,0,"Xn"],
            [1,0,1,"Xn"],
            [1,1,0,"Xn"],
            [1,1,1,"CALLM_ABS_REG" ],
          ]
          },

# The register number when the addressing mode is absolute (Mode 111)
"CALLM_ABS_REG" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
          ]
          },#}}}
# ADDI {{{

"ADDI_S" : { "length" : 2,
            "bits":
          [ # condition
            [0,0],
            [0,1],
            [1,0], ]
          },

"ADDI_EA" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0,"Xn"],
            [0,1,0,"Xn"],
            [0,1,1,"Xn"],
            [1,0,0,"Xn"],
            [1,0,1,"Xn"],
            [1,1,0,"Xn"],
            [1,1,1,"ADDI_ABS_REG" ],
          ]
          },

# The register number when the addressing mode is absolute (Mode 111)
"ADDI_ABS_REG" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0],
            [0,0,1],
          ]
          },#}}}
# CMP2/CHK2 {{{

"CMP2/CHK2_S" : { "length" : 2,
            "bits":
          [ # condition
            [0,0],
            [0,1],
            [1,0], ]
          },

"CMP2/CHK2_EA" : { "length" : 3,
            "bits":
          [ # condition
            [0,1,0,"Xn"],
            [1,0,1,"Xn"],
            [1,1,0,"Xn"],
            [1,1,1,"CMP2/CHK2_ABS_REG" ],
          ]
          },

# The register number when the addressing mode is absolute (Mode 111)
"CMP2/CHK2_ABS_REG" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
          ]
          },#}}}
# EORI {{{

"EORI_S" : { "length" : 2,
            "bits":
          [ # condition
            [0,0],
            [0,1],
            [1,0], ]
          },

"EORI_EA" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0,"Xn"],
            [0,1,0,"Xn"],
            [0,1,1,"Xn"],
            [1,0,0,"Xn"],
            [1,0,1,"Xn"],
            [1,1,0,"Xn"],
            [1,1,1,"EORI_ABS_REG" ],
          ]
          },

# The register number when the addressing mode is absolute (Mode 111)
"EORI_ABS_REG" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0],
            [0,0,1],
          ]
          },#}}}
# CMPI {{{

"CMPI_S" : { "length" : 2,
            "bits":
          [ # condition
            [0,0],
            [0,1],
            [1,0], ]
          },

"CMPI_EA" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0,"Xn"],
            [0,1,0,"Xn"],
            [0,1,1,"Xn"],
            [1,0,1,"Xn"],
            [1,0,0,"Xn"],
            [1,1,0,"Xn"],
            [1,1,1,"CMPI_ABS_REG" ],
          ]
          },

# The register number when the addressing mode is absolute (Mode 111)
"CMPI_ABS_REG" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
          ]
          },#}}}
# BTST_DYNAMIC {{{

"BTST_Xn" : COMMON_PATTERNS[ "Xn" ],

"BTST_DYNAMIC_EA" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0,"Xn"],
            [0,1,0,"Xn"],
            [0,1,1,"Xn"],
            [1,0,0,"Xn"],
            [1,0,1,"Xn"],
            [1,1,0,"Xn"],
            [1,1,1,"BTST_DYNAMIC_ABS_REG" ],
          ]
          },

# The register number when the addressing mode is absolute (Mode 111)
"BTST_DYNAMIC_ABS_REG" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
          ]
          },#}}}
# BTST_STATIC {{{

"BTST_STATIC_EA" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0,"Xn"],
            [0,1,0,"Xn"],
            [0,1,1,"Xn"],
            [1,0,0,"Xn"],
            [1,0,1,"Xn"],
            [1,1,0,"Xn"],
            [1,1,1,"BTST_STATIC_ABS_REG" ],
          ]
          },

# The register number when the addressing mode is absolute (Mode 111)
"BTST_STATIC_ABS_REG" : { "length" : 3,
            "bits":
          [ # condition
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
          ]
          },#}}}
}#}}}

# Include COMMON_PATTERNS in PATTERNS
PATTERNS.update( COMMON_PATTERNS )

OPCODES = {
    "ORI to CCR"    : [0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0],#{{{#{{{#{{{#{{{
    "ORI to SR"     : [0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0],
    "ORI"           : [0,0,0,0,0,0,0,0,"ORI_S","ORI_EA"],
    "ANDI to CCR"   : [0,0,0,0,0,0,1,0,0,0,1,1,1,1,0,0],
    "ANDI to SR"    : [0,0,0,0,0,0,1,0,0,1,1,1,1,1,0,0],
    "ANDI"          : [0,0,0,0,0,0,1,0,"ANDI_S","ANDI_EA"],
    "SUBI"          : [0,0,0,0,0,1,0,0,"SUBI_S","SUBI_EA"],
    "RTM"           : [0,0,0,0,0,1,1,0,1,1,0,0,"RTM_b","RTM_Xn"],
    "CALLM"         : [0,0,0,0,0,1,1,0,1,1,"CALLM_EA"],
    "ADDI"          : [0,0,0,0,0,1,1,0,"ADDI_S","ADDI_EA"],
    "CMP2/CHK2"     : [0,0,0,0,0,"CMP2/CHK2_S",0,1,1,"CMP2/CHK2_EA"], # See Note 1.0#}}}
    "EORI_to_CCR"   : [0,0,0,0,1,0,1,0,0,0,1,1,1,1,0,0],
    "EORI_to_SR"    : [0,0,0,0,1,0,1,0,0,1,1,1,1,1,0,0],#}}}
    "EORI"          : [0,0,0,0,1,0,1,0,"EORI_S","EORI_EA"],#}}}
    "CMPI"          : [0,0,0,0,1,1,0,0,"CMPI_S","CMPI_EA"],#}}}
    "BTST_DYNAMIC"  : [0,0,0,0,"BTST_Xn",1,0,0,"BTST_DYNAMIC_EA"],
    "BTST_STATIC"   : [0,0,0,0,1,0,0,0,0,0,"BTST_STATIC_EA"],
    "BCHG"          : [0,0,0,0,1,0,0,0,0,1,"BCHG_EA"],
    "BCLR"          : [0,0,0,0,1,0,0,0,1,0,"BCLR_EA"],
    "BSET"          : [0,0,0,0,1,0,0,0,1,1,"BSET_EA"],
    "MOVES"         : [0,0,0,0,1,1,1,0,"MOVES_S","MOVES_EA"],
    "CAS2"          : [0,0,0,0,1,"CAS2_S",0,1,1,1,1,1,1,0,0],
    "CAS"           : [0,0,0,0,"CAS_S",0,1,1,"CAS_EA"],
    "BCHG"          : [0,0,0,0,"BCHG_Xn",1,0,1,"BCHG_EA"],
    "BCLR"          : [0,0,0,0,"BCLR_Xn",1,1,0,"BCLR_EA"],
    "BSET"          : [0,0,0,0,"BSET_Xn",1,1,1,"BSET_EA"],
    "MOVEP"         : [0,0,0,0,"MOVEP_Xn","MOVEP_OPMODE",0,0,1,"MOVEP_Xn"],
    "MOVEA"         : [0,0,"MOVEA_S","MOVEA_DN",0,0,1,"MOVEA_SOURCE"],
    "MOVE"          : [0,0,"MOVE_S","MOVE_DESTINATION","MOVE_SOURCE"],
    "MOVE_from_SR"  : [0,1,0,0,0,0,0,0,1,1,"MOVE_from_SR_SOURCE"],
    "MOVE_from_CCR" : [0,1,0,0,0,0,1,0,1,1,"MOVE_from_CCR_EA"],
    "NEGX"          : [0,1,0,0,0,0,0,0,"NEGX_SIZE1","NEGX_EA"],
    "CLR"           : [0,1,0,0,0,0,1,0,"CLR_SIZE","CLR_EA"],
    "MOVE_to_CCR"   : [0,1,0,0,0,1,0,0,1,1,"MOVE_to_CCR_EA"],
    "NEG"           : [0,1,0,0,0,1,0,0,"NEG_SIZE","NEG_EA"],
    "NOT"           : [0,1,0,0,0,1,1,0,"NOT_SIZE","NOT_EA"],
    "MOVE_to_SR"    : [0,1,0,0,0,1,1,0,1,1,"MOVE_to_SR_EA"],
    "EXT/EXTB"      : [0,1,0,0,1,0,0,"EXT/EXTB_OPMODE",0,0,0,"EXT/EXTB_REGISTER"],
    "LINK_LONG"     : [0,1,0,0,1,0,0,0,0,0,0,0,1,"LINK_REGISTER"],
    "LINK_WORD"     : [0,1,0,0,1,1,1,0,0,1,0,1,0,"LINK_REGISTER"],
    "NBCD"          : [0,1,0,0,1,0,0,0,0,0,0,"NBCD_EA"],
    "SWAP"          : [0,1,0,0,1,0,0,0,0,1,0,0,0,"SWAP_REGISTER"],
    "BKPT"          : [0,1,0,0,1,0,0,0,0,1,0,0,1,"BKPT_VECTOR"],
    "PEA"           : [0,1,0,0,1,0,0,0,0,1,"PEA_EA"],
    "BGND"          : [0,1,0,0,1,0,1,0,1,1,1,1,1,0,1,0],
    "ILLEGAL"       : [0,1,0,0,1,0,1,0,1,1,1,1,1,1,0,0],
    "TAS"           : [0,1,0,0,1,0,1,0,1,1,"TAS_EA"],
    "TST"           : [0,1,0,0,1,0,1,0,"TST_SIZE","TST_EA"],
    "MULU"          : [0,1,0,0,1,1,0,0,0,0,"MULU_EA"],
    "MULS"          : [0,1,0,0,1,1,0,0,0,0,"MULS_EA"],
    "DIVU/DIVUL"    : [0,1,0,0,1,1,0,0,0,0,"DIVU/DIVUL_EA"],
    "DIVS/DIVSL"    : [0,1,0,0,1,1,0,0,0,1,"DIVS/DIVSL_EA"],
    "TRAP"          : [0,1,0,0,1,1,1,0,0,1,0,0,"TRAP_VECTOR"],
    "UNLK"          : [0,1,0,0,1,1,1,0,0,1,0,1,1,"UNLK_REGISTER"],
    "MOVE_USP"      : [0,1,0,0,1,1,1,0,0,1,1,0,"MOVE_USP_dr","MOVE_USP_REGISTER"],
    "RESET"         : [0,1,0,0,1,1,1,0,0,1,1,1,0,0,0,0],
    "NOP"           : [0,1,0,0,1,1,1,0,0,1,1,1,0,0,0,1],
    "STOP"          : [0,1,0,0,1,1,1,0,0,1,1,1,0,0,1,0],
    "RTE"           : [0,1,0,0,1,1,1,0,0,1,1,1,0,0,1,1],
    "RTD"           : [0,1,0,0,1,1,1,0,0,1,1,1,0,1,0,0],
    "RTS"           : [0,1,0,0,1,1,1,0,0,1,1,1,0,1,0,1],
    "TRAPV"         : [0,1,0,0,1,1,1,0,0,1,1,1,0,1,1,0],
    "RTR"           : [0,1,0,0,1,1,1,0,0,1,1,1,0,1,1,1],
    "MOVEC"         : [0,1,0,0,1,1,1,0,0,1,1,1,1,0,1,"MOVEC_dr"],
    "JSR"           : [0,1,0,0,1,1,1,0,1,0,"JSR_EA"],
    "JMP"           : [0,1,0,0,1,1,1,0,1,1,"JMP_EA"],
    "MOVEM"         : [0,1,0,0,1,"MOVEM_dr",0,0,1,"MOVEM_SIZE","MOVEM_EA"],
    "LEA"           : [0,1,0,0,"LEA_REGISTER",1,1,1,"LEA_EA"],
    "CHK"           : [0,1,0,0,"CHK_REGISTER","CHK_SIZE",0,"CHK_EA"],
    "ADDQ"          : [0,1,0,1,"ADDQ_DATA",0,"ADDQ_SIZE","ADDQ_EA"],
    "SUBQ"          : [0,1,0,1,"SUBQ_DATA",1,"SUBQ_SIZE","SUBQ_EA"],
    "DBcc"          : [0,1,0,1,"DBcc_CONDITION",1,1,0,0,1,"DBcc_REGISTER"],
    "TRAPcc"        : [0,1,0,1,"TRAPcc_CONDITION",1,1,1,1,1,"TRAPcc_OPCODE"],
    "Scc"           : [0,1,0,1,"Scc_CONDITION",1,1,"Scc_EA"],
    "BRA"           : [0,1,1,0,0,0,0,0,"BRA_8BIT_DISPLACEMENT"],
    "BSR"           : [0,1,1,0,0,0,0,1,"BRA_8BIT_DISPLACEMENT"],
    "Bcc"           : [0,1,1,0,"Bcc_CONDITION","BRA_8BIT_DISPLACEMENT"],
    "MOVEQ"         : [0,1,1,1,"MOVEQ_REGISTER",0,"MOVEQ_DATA"],
    "DIVU/DIVUL"    : [1,0,0,0,"DIVU/DIVUL_REGISTER",0,1,1,"DIVU/DIVUL_EA"],
    "SBCD"          : [1,0,0,0,"SBCD_REGISTER_DyAy",1,0,0,0,0,"SBCD_RM","SBCD_REGISTER_DxAx"],
    "PACK"          : [1,0,0,0,"PACK_REGISTER_DyAy",1,0,1,0,0,"PACK_RM","PACK_REGISTER_DxAx"],
    "UNPK"          : [1,0,0,0,"UNPK_REGISTER_DyAy",1,1,0,0,0,"UNPK_RM","UNPK_REGISTER_DxAx"],
    "DIVS/DIVSL"    : [1,0,0,0,"DIVS/DIVSL_REGISTER",1,1,1,"DIVS/DIVSL_EA"],
    "OR"            : [1,0,0,0,"OR_REGISTER","OR_OPMODE","OR_EA"],
    "SUBX"          : [1,0,0,1,"SUBX_REGISTER_DyAy",1,"SUBX_SIZE",0,0,"SUBX_RM","SUBX_REGISTER_DxAx"],
    "SUB"           : [1,0,0,1,"SUB_REGISTER","SUB_OPMODE","SUB_EA"],
    "SUBA"          : [1,0,0,1,"SUBA_REGISTER", "SUBA_OPMODE","SUBA_EA"],
    "CMPM"          : [1,0,1,1,"CMPM_REGISTER_Ax",1,"CMPM_SIZE",0,0,1,"CMPM_REGISTER_Ay"],
    "CMP"           : [1,0,1,1,"CMP_REGISTER","CMP_OPMODE","CMP_EA"],
    "CMPA"          : [1,0,1,1,"CMPA_REGISTER","CMPA_OPMODE","CMPA_EA"],
    "EOR"           : [1,0,1,1,"EOR_REGISTER","EOR_OPMODE","EOR_EA"],
    "MULU"          : [1,1,0,0,"MULU_REGISTER",0,1,1,"MULU_EA"],
    "ABCD"          : [1,1,0,0,"ABCD_REGISTER_Rx",1,0,0,0,0,"ABCD_RM","ABCD_REGISTER_Ry"],
    "MULS"          : [1,1,0,0,"MULS_REGISTER",1,1,1,"MULS_EA"],
    "EXG"           : [1,1,0,0,"EXG_REGISTER_Rx",1,"EXG_OPMODE","EXG_REGISTER_Ry"],
    "AND"           : [1,1,0,0,"AND_REGISTER","AND_OPMODE","AND_EA"],
    "ADDX"          : [1,1,0,1,"ADDX_REGISTER_Rx",1,"ADDX_SIZE",0,0,"ADDX_RM","ADDX_REGISTER_Ry"],
    "ADDA"          : [1,1,0,1,"ADDA_REGISTER","ADDA_OPMODE","ADDA_EA"],
    "ADD"           : [1,1,0,1,"ADD_REGISTER","ADD_OPMODE","ADD_EA"],
    "ASL/ASR"       : [1,1,1,0,0,0,0,"ASL/ASR_dr",1,1,"ASL/ASR_EA"],
    "LSL/LSR"       : [1,1,1,0,0,0,1,"LSL/LSR_dr",1,1,"LSL/LSR_EA"],
    "ROXL/ROXR"     : [1,1,1,0,0,1,0,"ROXL/ROXR_dr",1,1,"ROXL/ROXR_EA"],
    "ROL/ROR"       : [1,1,1,0,0,1,1,"ROL/ROR_dr",1,1,"ROL/ROR_EA"],
    "BFTST"         : [1,1,1,0,1,0,0,0,1,1,"BFTST_EA"],
    "BFEXTU"        : [1,1,1,0,1,0,0,1,1,1,"BFEXTU_EA"],
    "BFCHG"         : [1,1,1,0,1,0,1,0,1,1,"BFCHG_EA"],
    "BFEXTS"        : [1,1,1,0,1,0,1,1,1,1,"BFEXTS_EA"],
    "BFCLR"         : [1,1,1,0,1,1,0,0,1,1,"BFCLR_EA"],
    "BFFFO"         : [1,1,1,0,1,1,0,1,1,1,"BFFFO_EA"],
    "BFSET"         : [1,1,1,0,1,1,1,0,1,1,"BFSET_EA"],
    "BFINS"         : [1,1,1,0,1,1,1,1,1,1,"BFINS_EA"],
    "ASL/ASR"       : [1,1,1,0,"ASL/ASR_COUNT/REGISTER","ASL/ASR_dr","ASL/ASR_SIZE","ASL/ASR_i/r",0,0,"ASL/ASR_REGISTER"],
    "LSL/LSR"       : [1,1,1,0,"LSL/LSR_COUNT/REGISTER","LSL/LSR_dr","LSL/LSR_SIZE","LSL/LSR_i/r",0,1,"LSL/LSR_REGISTER"],
    "ROXL/ROXR"     : [1,1,1,0,"ROXL/ROXR_COUNT/REGISTER","ROXL/ROXR_dr","ROXL/ROXR_SIZE","ROXL/ROXR_i/r",1,0,"ROXL/ROXR_REGISTER"],
    "ROL/ROR"       : [1,1,1,0,"ROL/ROR_COUNT/REGISTER","ROL/ROR_dr","ROL/ROR_SIZE","ROL/ROR_i/r",1,1,"ROL/ROR_REGISTER"],
}
# Note 1.0: The bits for the first word of CMP2 and CHK2 are the same.
#           We will figure out which one it actually is during the 
#           execute step.  The same goes for any opcode names with a /
#           in them.

INSTRUCTIONS = []
for i in xrange(2**16):
    INSTRUCTIONS.append( None )

def isstatic( _bits ):
    """Returns true if the bits are all ones and zeroes (no patterns)"""
    for b in _bits:
        if b not in [0,1]:
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

        #print( "\t%s" % bit_string )

        INSTRUCTIONS[ bit_value ] = _name
        
    i = 0

    while i in range( len( _bits ) ): # strange loop

        b = _bits[i]
        pattern_length = 1

        if b in PATTERNS:
            pat            = PATTERNS[b]["bits"]
            pattern_length = PATTERNS[b]["length"]

            for p in pat:
                bits_copy = deepcopy( _bits )
                bits_copy.pop(i)
                bits_copy[i:i] = p
                gen( bits_copy, _name )

            return # return, since a pattern has been found and fully populated

        i += pattern_length

    return _bits

for op in OPCODES:
    if op != None:
        print( "Generating bit patterns for %s... " % op )
        gen( OPCODES[op], op )

for i in xrange(len(INSTRUCTIONS)):
    if INSTRUCTIONS[i] != None:
        print( "%s -> %s" % ( bin(i)[2:], INSTRUCTIONS[i] ) )
