#!/usr/bin/python3

#  This file is part of AEJS (http://aejs.org/).
#
#  AEJS is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  AEJS is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with AEJS.  If not, see <http://www.gnu.org/licenses/>.

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
#
# Oh, and please forgive the sloppy formatting.  Typing this
# takes a long time so I tried to get it done as quickly as
# possible.

#**************************
#
# Common patterns
#
#**************************

COMMON_PATTERNS = {#{{{
    # one bit
    "b" : [ [0],[1], ],

    "S" : [ # size
            [0,0], 
            [0,1], 
            [1,0], ],

"vector3" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
            [1,0,1],
            [1,1,0],
            [1,1,1], ],

"vector4" : [
            [0,0,0,0],
            [0,0,0,1],
            [0,0,1,0],
            [0,0,1,1],
            [0,1,0,0],
            [0,1,0,1],
            [0,1,1,0],
            [0,1,1,1],
            [1,0,0,0],
            [1,0,0,1],
            [1,0,1,0],
            [1,0,1,1],
            [1,1,0,0],
            [1,1,0,1],
            [1,1,1,0],
            [1,1,1,1], ],

"OPMODE": [ # used in MOVEP, and perhaps other ops
            [1,0,0],
            [1,0,1],
            [1,1,0],
            [1,1,1], ],


}#}}}

#**************************
#
# Operand patterns
#
#**************************

PATTERNS = {#{{{

# ORI {{{

"ORI_S" : [
            [0,0],
            [0,1],
            [1,0], ],

"ORI_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"ORI_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"ORI_ABS_REG" : [ # condition
            [0,0,0],
            [0,0,1], ],
#}}}
# ANDI {{{

"ANDI_S" : [ # condition
            [0,0],
            [0,1],
            [1,0], ],

"ANDI_EA" : [ # condition
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"ANDI_ABS_REG" ], ],

# The register number when the addressing mode is absolute (Mode 111)
"ANDI_ABS_REG" : [ # condition
            [0,0,0],
            [0,0,1], ],
#}}}
# SUBI {{{

"SUBI_S" : [ # condition
            [0,0],
            [0,1],
            [1,0], ],

"SUBI_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"SUBI_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"SUBI_ABS_REG" : [
            [0,0,0],
            [0,0,1],],#}}}
# RTM {{{
"RTM_b" : COMMON_PATTERNS["b"],
"RTM_vector3" : COMMON_PATTERNS["vector3"],
          #}}}
# CALLM {{{

"CALLM_EA" : [
            [0,1,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"CALLM_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"CALLM_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
          ],#}}}
# ADDI {{{

"ADDI_S" : [
            [0,0],
            [0,1],
            [1,0], ],

"ADDI_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"ADDI_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"ADDI_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# CMP2/CHK2 {{{

"CMP2/CHK2_S" : [
            [0,0],
            [0,1],
            [1,0], ],

"CMP2/CHK2_EA" : [
            [0,1,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"CMP2/CHK2_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"CMP2/CHK2_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
          ],#}}}
# EORI {{{

"EORI_S" : [
            [0,0],
            [0,1],
            [1,0], ],

"EORI_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"EORI_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"EORI_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# CMPI {{{

"CMPI_S" : [
            [0,0],
            [0,1],
            [1,0], ],

"CMPI_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,1,"vector3"],
            [1,0,0,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"CMPI_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"CMPI_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
          ],#}}}
# BTST_DYNAMIC {{{

"BTST_vector3" : COMMON_PATTERNS[ "vector3" ],

"BTST_DYNAMIC_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"BTST_DYNAMIC_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"BTST_DYNAMIC_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
          ],#}}}
# BTST_STATIC {{{

"BTST_STATIC_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"BTST_STATIC_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"BTST_STATIC_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
          ],#}}}
# BCHG_DYNAMIC {{{

"BCHG_vector3" : COMMON_PATTERNS[ "vector3" ],

"BCHG_DYNAMIC_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"BCHG_DYNAMIC_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"BCHG_DYNAMIC_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# BCHG_STATIC {{{

"BCHG_STATIC_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"BCHG_STATIC_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"BCHG_STATIC_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# BCLR_DYNAMIC {{{

"BCLR_vector3" : COMMON_PATTERNS[ "vector3" ],

"BCLR_DYNAMIC_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"BCLR_DYNAMIC_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"BCLR_DYNAMIC_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# BCLR_STATIC {{{

"BCLR_STATIC_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"BCLR_STATIC_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"BCLR_STATIC_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# EORI {{{

"EORI_S" : [
            [0,0],
            [0,1],
            [1,0], ],

"EORI_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"EORI_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"EORI_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# BSET_DYNAMIC {{{

"BSET_vector3" : COMMON_PATTERNS[ "vector3" ],

"BSET_DYNAMIC_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"BSET_DYNAMIC_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"BSET_DYNAMIC_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# BSET_STATIC {{{

"BSET_STATIC_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"BSET_STATIC_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"BSET_STATIC_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# MOVES {{{

"MOVES_S" : [
            [0,0],
            [0,1],
            [1,0], ],

"MOVES_EA" : [
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"MOVES_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"MOVES_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# CAS {{{

"CAS_S" : [
            [0,1],
            [1,0],
            [1,1], ],

"CAS_EA" : [
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"CAS_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"CAS_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# CAS2 {{{

"CAS2_S" : [
            [1,0],
            [1,1], ],#}}}
# MOVEP {{{

"MOVEP_vector3" : COMMON_PATTERNS["vector3"],
"MOVEP_OPMODE" : COMMON_PATTERNS["OPMODE"],

        #}}}
# MOVEA {{{

"MOVEA_S" : [
            [1,0],
            [1,1], ],

"MOVEA_DN" : COMMON_PATTERNS["vector3"],

"MOVEA_SOURCE" : [
            [0,0,0,"vector3"],
            [0,0,1,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"MOVEA_ABS_REG" ],],

"MOVEA_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [1,0,0],
            [0,1,0],
            [0,1,1],
          ],
#}}}
# MOVE {{{

"MOVE_S" : [
            [0,1],
            [1,0],
            [1,1], ],

"MOVE_DESTINATION" : [
            ["vector3",0,0,0],
            ["vector3",0,1,0],
            ["vector3",0,1,1],
            ["vector3",1,0,0],
            ["vector3",1,0,1],
            ["vector3",1,1,0],
            ["MOVE_DESTINATION_ABS_REG",1,1,1],],

"MOVE_DESTINATION_ABS_REG" : [
            [0,0,0],
            [0,0,1],],

"MOVE_SOURCE" : [
            [0,0,0,"vector3"],
            [0,0,1,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"MOVE_ABS_REG" ],],

"MOVE_SOURCE_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [1,0,0],
            [0,1,0],
            [0,1,1],
          ],
#}}}
# MOVE_from_SR {{{

"MOVE_from_SR_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"MOVE_from_SR_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"MOVE_from_SR_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# MOVE_from_CCR {{{

"MOVE_from_CCR_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"MOVE_from_CCR_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"MOVE_from_CCR_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# NEGX {{{

"NEGX_S" : [
            [0,0],
            [0,1],
            [1,0], ],

"NEGX_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"NEGX_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"NEGX_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# CLR {{{

"CLR_S" : [
            [0,0],
            [0,1],
            [1,0], ],

"CLR_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"CLR_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"CLR_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# MOVE_to_CCR {{{

"MOVE_to_CCR_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"MOVE_to_CCR_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"MOVE_to_CCR_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
          ],#}}}
# NEG {{{

"NEG_S" : [
            [0,0],
            [0,1],
            [1,0], ],

"NEG_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"NEG_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"NEG_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# NOT {{{

"NOT_S" : [
            [0,0],
            [0,1],
            [1,0], ],

"NOT_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"NOT_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"NOT_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# MOVE_to_SR {{{

"MOVE_to_SR_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"MOVE_to_SR_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"MOVE_to_SR_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
          ],#}}}
# EXT/EXTB {{{

"EXT/EXTB_REGISTER" : COMMON_PATTERNS["vector3"],
"EXT/EXTB_OPMODE" : [
            [0,1,0],
            [0,1,1],
            [1,1,1],
          ],#}}}
# LINK_WORD {{{

"LINK_WORD_REGISTER" : COMMON_PATTERNS["vector3"],

#}}}
# LINK_LONG {{{

"LINK_LONG_REGISTER" : COMMON_PATTERNS["vector3"],

#}}}
# NBCD {{{

"NBCD_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"NBCD_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"NBCD_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# SWAP {{{

"SWAP_REGISTER" : COMMON_PATTERNS["vector3"],

#}}}
# BKPT {{{

"BKPT_VECTOR" : COMMON_PATTERNS["vector3"], # vectors are 0..7 just like register numbers

#}}}
# PEA {{{

"PEA_EA" : [
            [0,1,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"PEA_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"PEA_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
          ],#}}}
# TAS {{{

"TAS_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"TAS_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"TAS_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# TST {{{

"TST_S" : [
            [0,0],
            [0,1],
            [1,0], ],

"TST_EA" : [
            [0,0,0,"vector3"],
            [0,0,1,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"TST_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"TST_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
          ],#}}}
# MULU_WORD {{{

"MULU_WORD_REGISTER" : COMMON_PATTERNS[ "vector3" ],

"MULU_WORD_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"MULU_WORD_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"MULU_WORD_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
          ],#}}}
# MUL_LONG {{{

"MUL_LONG_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"MUL_LONG_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"MUL_LONG_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
          ],#}}}
# MULS_WORD {{{

"MULS_WORD_REGISTER" : COMMON_PATTERNS[ "vector3" ],

"MULS_WORD_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"MULS_WORD_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"MULS_WORD_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
          ],#}}}
# DIVS_WORD {{{

"DIVS_WORD_REGISTER" : COMMON_PATTERNS[ "vector3" ],

"DIVS_WORD_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"DIVS_WORD_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"DIVS_WORD_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
          ],#}}}
# DIVU_WORD {{{

"DIVU_WORD_REGISTER" : COMMON_PATTERNS[ "vector3" ],

"DIVU_WORD_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"DIVU_WORD_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"DIVU_WORD_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
          ],#}}}
# DIV_LONG {{{

"DIV_LONG_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"DIV_LONG_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"DIV_LONG_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
          ],#}}}
# TRAP {{{

"TRAP_VECTOR" : COMMON_PATTERNS["vector4"], 

#}}}
# UNLK {{{

"UNLK_REGISTER" : COMMON_PATTERNS[ "vector3" ],

#}}}
# MOVE_USP {{{

"MOVE_USP_dr" : COMMON_PATTERNS["b"],
"MOVE_USP_REGISTER" : COMMON_PATTERNS["vector3"],

#}}}
# MOVEC {{{

"MOVEC_dr" : COMMON_PATTERNS[ "b" ],

#}}}
# JSR {{{

"JSR_EA" : [
            [0,1,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"JSR_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"JSR_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
          ],#}}}
# JMP {{{

"JMP_EA" : [
            [0,1,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"JMP_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"JMP_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
          ],#}}}
# MOVEM {{{

"MOVEM_dr" : COMMON_PATTERNS[ "b" ],
"MOVEM_S"  : COMMON_PATTERNS[ "b" ],

"MOVEM_EA" : [
            [0,1,0,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"MOVEM_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"MOVEM_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# LEA {{{

"LEA_REGISTER"  : COMMON_PATTERNS[ "vector3" ],

"LEA_EA" : [
            [0,1,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"LEA_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"LEA_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
          ],#}}}
# CHK {{{

"CHK_REGISTER"  : COMMON_PATTERNS[ "vector3" ],

"CHK_S" : [
            [1,1],
            [1,0], ],


"CHK_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"CHK_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"CHK_ABS_REG" : [
            [0,0,0],
            [0,0,1],
            [0,1,0],
            [0,1,1],
            [1,0,0],
          ],#}}}
# ADDQ {{{

"ADDQ_DATA"  : COMMON_PATTERNS[ "vector3" ],

"ADDQ_S" : [
            [0,0],
            [0,1],
            [1,0], ],

"ADDQ_EA" : [
            [0,0,0,"vector3"],
            [0,0,1,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"ADDQ_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"ADDQ_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# SUBQ {{{

"SUBQ_DATA"  : COMMON_PATTERNS[ "vector3" ],

"SUBQ_S" : [
            [0,0],
            [0,1],
            [1,0], ],

"SUBQ_EA" : [
            [0,0,0,"vector3"],
            [0,0,1,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"SUBQ_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"SUBQ_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# DBcc {{{

"DBcc_CONDITION" : COMMON_PATTERNS[ "vector4" ],
"DBcc_REGISTER"  : COMMON_PATTERNS[ "vector3" ],

#}}}
# TRAPcc {{{

"TRAPcc_CONDITION" : COMMON_PATTERNS[ "vector4" ],
"TRAPcc_OPCODE" : [
            [0,1,0],
            [0,1,1],
            [1,0,0], ],

#}}}
# Scc {{{

"Scc_CONDITION" : COMMON_PATTERNS[ "vector4" ],

"Scc_EA" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"Scc_ABS_REG" ],
          ],

# The register number when the addressing mode is absolute (Mode 111)
"Scc_ABS_REG" : [
            [0,0,0],
            [0,0,1],
          ],#}}}
# BSR {{{

"BSR_8BIT_DISPLACEMENT" : [ ["vector4","vector4"], ], # = vector8 :)

#}}}
# BRA/BSR/Bcc {{{

"BRA/BSR/Bcc_CONDITION"  : COMMON_PATTERNS[ "vector4" ],
"BRA/BSR/Bcc_8BIT_DISPLACEMENT" : [ ["vector4","vector4"], ], # = vector8 :)

#}}}
# MOVEQ {{{

"MOVEQ_REGISTER" : [ ["vector3"] ], # = vector7 : )
"MOVEQ_DATA"     : [ ["vector4", "vector4" ], ], # = vector7 : )

#}}}
# SBCD {{{

"SBCD_REGISTER_DyAy" : [ [ "vector3"] ],
"SBCD_RM"            : [ [ "b" ] ],
"SBCD_REGISTER_DxAx" : [ [ "vector3" ] ],

#}}}
# PACK {{{

"PACK_REGISTER_DyAy" : [ [ "vector3"] ],
"PACK_RM"            : [ [ "b" ] ],
"PACK_REGISTER_DxAx" : [ [ "vector3" ] ],

#}}}
# UNPK {{{

"UNPK_REGISTER_DyAy" : [ [ "vector3"] ],
"UNPK_RM"            : [ [ "b" ] ],
"UNPK_REGISTER_DxAx" : [ [ "vector3" ] ],

#}}}
# OR {{{

# This is one of the more complicated opcodes, since
# there are two addressing mode tables.  Which one gets used 
# depends on the opmode.

"OR_REGISTER" : [ [ "vector3"] ],
"OR_OPMODE_EA" : [ 
                [0,0,0,"OR_EA_SRC"],
                [0,0,1,"OR_EA_SRC"],
                [0,1,0,"OR_EA_SRC"],

                [1,0,0,"OR_EA_DEST"],
                [1,0,1,"OR_EA_DEST"],
                [1,1,0,"OR_EA_DEST"],
            ],
"OR_EA_SRC" : [
            [0,0,0,"vector3"],
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"OR_ABS_REG_SRC" ],
          ],

"OR_EA_DEST" : [
            [0,1,0,"vector3"],
            [0,1,1,"vector3"],
            [1,0,0,"vector3"],
            [1,0,1,"vector3"],
            [1,1,0,"vector3"],
            [1,1,1,"OR_ABS_REG_DEST" ],
          ],

# If the location specified is a source operand, only data 
# addressing modes can be used as listed in the following tables [page 256 of 68kpm]
"OR_ABS_REG_SRC" : [ 

            [0,0,0],
            [0,0,1],
            [1,0,0],
            [0,1,0],
            [0,1,1],
        ],

# If the location specified is a destination operand, only memory 
# alterable addressing modes can be used as listed in the following 
# tables [page 257 of 68kpm]
"OR_ABS_REG_DEST" : [
            [0,0,0],
            [0,0,1],
        ],
#}}}

}#}}}

# Include COMMON_PATTERNS in PATTERNS
PATTERNS.update( COMMON_PATTERNS )

OPCODES = {
    "ORI to CCR"    : [0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0],#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{#{{{
    "ORI to SR"     : [0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0],#}}}
    "ORI"           : [0,0,0,0,0,0,0,0,"ORI_S","ORI_EA"],#}}}
    "ANDI to CCR"   : [0,0,0,0,0,0,1,0,0,0,1,1,1,1,0,0],#}}}
    "ANDI to SR"    : [0,0,0,0,0,0,1,0,0,1,1,1,1,1,0,0],#}}}
    "ANDI"          : [0,0,0,0,0,0,1,0,"ANDI_S","ANDI_EA"],#}}}
    "SUBI"          : [0,0,0,0,0,1,0,0,"SUBI_S","SUBI_EA"],#}}}
    "RTM"           : [0,0,0,0,0,1,1,0,1,1,0,0,"RTM_b","RTM_vector3"],#}}}
    "CALLM"         : [0,0,0,0,0,1,1,0,1,1,"CALLM_EA"],#}}}
    "ADDI"          : [0,0,0,0,0,1,1,0,"ADDI_S","ADDI_EA"],#}}}
    "CMP2/CHK2"     : [0,0,0,0,0,"CMP2/CHK2_S",0,1,1,"CMP2/CHK2_EA"], # See Note 1.0#}}}
    "EORI_to_CCR"   : [0,0,0,0,1,0,1,0,0,0,1,1,1,1,0,0],#}}}
    "EORI_to_SR"    : [0,0,0,0,1,0,1,0,0,1,1,1,1,1,0,0],#}}}
    "EORI"          : [0,0,0,0,1,0,1,0,"EORI_S","EORI_EA"],#}}}
    "CMPI"          : [0,0,0,0,1,1,0,0,"CMPI_S","CMPI_EA"],#}}}
    "BTST_DYNAMIC"  : [0,0,0,0,"BTST_vector3",1,0,0,"BTST_DYNAMIC_EA"],#}}}
    "BTST_STATIC"   : [0,0,0,0,1,0,0,0,0,0,"BTST_STATIC_EA"],#}}}
    "BCHG_STATIC"   : [0,0,0,0,1,0,0,0,0,1,"BCHG_STATIC_EA"],#}}}
    "BCHG_DYNAMIC"  : [0,0,0,0,"BCHG_vector3",1,0,1,"BCHG__DYNAMIC_EA"],#}}}
    "BCLR"          : [0,0,0,0,1,0,0,0,1,0,"BCLR_EA"],#}}}
    "BCLR"          : [0,0,0,0,"BCLR_vector3",1,1,0,"BCLR_EA"],#}}}
    "BSET_STATIC"   : [0,0,0,0,1,0,0,0,1,1,"BSET_STATIC_EA"],#}}}
    "BSET_DYNAMIC"  : [0,0,0,0,"BSET_vector3",1,1,1,"BSET_DYNAMIC_EA"],#}}}
    "MOVES"         : [0,0,0,0,1,1,1,0,"MOVES_S","MOVES_EA"],#}}}
    "CAS"           : [0,0,0,0,1,"CAS_S",0,1,1,"CAS_EA"],#}}}
    "CAS2"          : [0,0,0,0,1,"CAS2_S",0,1,1,1,1,1,1,0,0],#}}}
    "MOVEP"         : [0,0,0,0,"MOVEP_vector3","MOVEP_OPMODE",0,0,1,"MOVEP_vector3"],#}}}
    "MOVEA"         : [0,0,"MOVEA_S","MOVEA_DN",0,0,1,"MOVEA_SOURCE"],#}}}
    "MOVE"          : [0,0,"MOVE_S","MOVE_DESTINATION","MOVE_SOURCE"],#}}}
    "MOVE_from_SR"  : [0,1,0,0,0,0,0,0,1,1,"MOVE_from_SR_EA"],#}}}
    "MOVE_from_CCR" : [0,1,0,0,0,0,1,0,1,1,"MOVE_from_CCR_EA"],#}}}
    "NEGX"          : [0,1,0,0,0,0,0,0,"NEGX_S1","NEGX_EA"],#}}}
    "CLR"           : [0,1,0,0,0,0,1,0,"CLR_S","CLR_EA"],#}}}
    "MOVE_to_CCR"   : [0,1,0,0,0,1,0,0,1,1,"MOVE_to_CCR_EA"],#}}}
    "NEG"           : [0,1,0,0,0,1,0,0,"NEG_S","NEG_EA"],#}}}
    "NOT"           : [0,1,0,0,0,1,1,0,"NOT_S","NOT_EA"],#}}}
    "MOVE_to_SR"    : [0,1,0,0,0,1,1,0,1,1,"MOVE_to_SR_EA"],#}}}
    "EXT/EXTB"      : [0,1,0,0,1,0,0,"EXT/EXTB_OPMODE",0,0,0,"EXT/EXTB_REGISTER"],#}}}
    "LINK_LONG"     : [0,1,0,0,1,0,0,0,0,0,0,0,1,"LINK_REGISTER"],#}}}
    "LINK_WORD"     : [0,1,0,0,1,1,1,0,0,1,0,1,0,"LINK_REGISTER"],#}}}
    "NBCD"          : [0,1,0,0,1,0,0,0,0,0,"NBCD_EA"],#}}}
    "SWAP"          : [0,1,0,0,1,0,0,0,0,1,0,0,0,"SWAP_REGISTER"],#}}}
    "BKPT"          : [0,1,0,0,1,0,0,0,0,1,0,0,1,"BKPT_VECTOR"],#}}}
    "PEA"           : [0,1,0,0,1,0,0,0,0,1,"PEA_EA"],#}}}
    "BGND"          : [0,1,0,0,1,0,1,0,1,1,1,1,1,0,1,0],#}}}
    "ILLEGAL"       : [0,1,0,0,1,0,1,0,1,1,1,1,1,1,0,0],#}}}
    "TAS"           : [0,1,0,0,1,0,1,0,1,1,"TAS_EA"],#}}}
    "TST"           : [0,1,0,0,1,0,1,0,"TST_S","TST_EA"],#}}}
    "MULU_WORD"     : [1,1,0,0,"MULU_WORD_REGISTER",0,1,1,"MULU_WORD_EA"],#}}}
    "MUL_LONG"      : [0,1,0,0,1,1,0,0,0,0,"MUL_LONG_EA"], # this matches MULS.long and MULU.long#}}}
    "MULS_WORD"     : [1,1,0,0,"MULS_WORD_REGISTER",1,1,1,"MULS_WORD_EA"],#}}}
    "DIVS_WORD"     : [1,0,0,0,"DIVS_WORD_REGISTER",1,1,1,"DIVS_WORD_EA"],#}}}
    "DIVU_WORD"     : [1,0,0,0,"DIVU_WORD_REGISTER",0,1,1,"DIVU_WORD_EA"],#}}}
    "DIV_LONG"      : [0,1,0,0,1,1,0,0,0,1,"DIV_LONG_EA"],#}}}
    "TRAP"          : [0,1,0,0,1,1,1,0,0,1,0,0,"TRAP_VECTOR"],#}}}
    "UNLK"          : [0,1,0,0,1,1,1,0,0,1,0,1,1,"UNLK_REGISTER"],#}}}
    "MOVE_USP"      : [0,1,0,0,1,1,1,0,0,1,1,0,"MOVE_USP_dr","MOVE_USP_REGISTER"],#}}}
    "RESET"         : [0,1,0,0,1,1,1,0,0,1,1,1,0,0,0,0],#}}}
    "NOP"           : [0,1,0,0,1,1,1,0,0,1,1,1,0,0,0,1],#}}}
    "STOP"          : [0,1,0,0,1,1,1,0,0,1,1,1,0,0,1,0],#}}}
    "RTE"           : [0,1,0,0,1,1,1,0,0,1,1,1,0,0,1,1],#}}}
    "RTD"           : [0,1,0,0,1,1,1,0,0,1,1,1,0,1,0,0],#}}}
    "RTS"           : [0,1,0,0,1,1,1,0,0,1,1,1,0,1,0,1],#}}}
    "TRAPV"         : [0,1,0,0,1,1,1,0,0,1,1,1,0,1,1,0],#}}}
    "RTR"           : [0,1,0,0,1,1,1,0,0,1,1,1,0,1,1,1],#}}}
    "MOVEC"         : [0,1,0,0,1,1,1,0,0,1,1,1,1,0,1,"MOVEC_dr"],#}}}
    "JSR"           : [0,1,0,0,1,1,1,0,1,0,"JSR_EA"],#}}}
    "JMP"           : [0,1,0,0,1,1,1,0,1,1,"JMP_EA"],#}}}
    "MOVEM"         : [0,1,0,0,1,"MOVEM_dr",0,0,1,"MOVEM_S","MOVEM_EA"],#}}}
    "LEA"           : [0,1,0,0,"LEA_REGISTER",1,1,1,"LEA_EA"],#}}}
    "CHK"           : [0,1,0,0,"CHK_REGISTER","CHK_S",0,"CHK_EA"],#}}}
    "ADDQ"          : [0,1,0,1,"ADDQ_DATA",0,"ADDQ_S","ADDQ_EA"],#}}}
    "SUBQ"          : [0,1,0,1,"SUBQ_DATA",1,"SUBQ_S","SUBQ_EA"],#}}}
    "DBcc"          : [0,1,0,1,"DBcc_CONDITION",1,1,0,0,1,"DBcc_REGISTER"],#}}}
    "TRAPcc"        : [0,1,0,1,"TRAPcc_CONDITION",1,1,1,1,1,"TRAPcc_OPCODE"],#}}}
    "Scc"           : [0,1,0,1,"Scc_CONDITION",1,1,"Scc_EA"],#}}}
    "BRA/BSR/Bcc"   : [0,1,1,0,"BRA/BSR/Bcc_CONDITION","BRA/BSR/Bcc_8BIT_DISPLACEMENT"],#}}}
    "MOVEQ"         : [0,1,1,1,"MOVEQ_REGISTER",0,"MOVEQ_DATA"],#}}}
    "SBCD"          : [1,0,0,0,"SBCD_REGISTER_DyAy",1,0,0,0,0,"SBCD_RM","SBCD_REGISTER_DxAx"],#}}}
    "PACK"          : [1,0,0,0,"PACK_REGISTER_DyAy",1,0,1,0,0,"PACK_RM","PACK_REGISTER_DxAx"],#}}}
    "UNPK"          : [1,0,0,0,"UNPK_REGISTER_DyAy",1,1,0,0,0,"UNPK_RM","UNPK_REGISTER_DxAx"],#}}}
    "OR"            : [1,0,0,0,"OR_REGISTER","OR_OPMODE_EA"],#}}}
    "SUBX"          : [1,0,0,1,"SUBX_REGISTER_DyAy",1,"SUBX_S",0,0,"SUBX_RM","SUBX_REGISTER_DxAx"],
    "SUB"           : [1,0,0,1,"SUB_REGISTER","SUB_OPMODE","SUB_EA"],
    "SUBA"          : [1,0,0,1,"SUBA_REGISTER", "SUBA_OPMODE","SUBA_EA"],
    "CMPM"          : [1,0,1,1,"CMPM_REGISTER_Ax",1,"CMPM_S",0,0,1,"CMPM_REGISTER_Ay"],
    "CMP"           : [1,0,1,1,"CMP_REGISTER","CMP_OPMODE","CMP_EA"],
    "CMPA"          : [1,0,1,1,"CMPA_REGISTER","CMPA_OPMODE","CMPA_EA"],
    "EOR"           : [1,0,1,1,"EOR_REGISTER","EOR_OPMODE","EOR_EA"],
    "ABCD"          : [1,1,0,0,"ABCD_REGISTER_Rx",1,0,0,0,0,"ABCD_RM","ABCD_REGISTER_Ry"],
    "EXG"           : [1,1,0,0,"EXG_REGISTER_Rx",1,"EXG_OPMODE","EXG_REGISTER_Ry"],
    "AND"           : [1,1,0,0,"AND_REGISTER","AND_OPMODE","AND_EA"],
    "ADDX"          : [1,1,0,1,"ADDX_REGISTER_Rx",1,"ADDX_S",0,0,"ADDX_RM","ADDX_REGISTER_Ry"],
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
    "ASL/ASR"       : [1,1,1,0,"ASL/ASR_COUNT/REGISTER","ASL/ASR_dr","ASL/ASR_S","ASL/ASR_i/r",0,0,"ASL/ASR_REGISTER"],
    "LSL/LSR"       : [1,1,1,0,"LSL/LSR_COUNT/REGISTER","LSL/LSR_dr","LSL/LSR_S","LSL/LSR_i/r",0,1,"LSL/LSR_REGISTER"],
    "ROXL/ROXR"     : [1,1,1,0,"ROXL/ROXR_COUNT/REGISTER","ROXL/ROXR_dr","ROXL/ROXR_S","ROXL/ROXR_i/r",1,0,"ROXL/ROXR_REGISTER"],
    "ROL/ROR"       : [1,1,1,0,"ROL/ROR_COUNT/REGISTER","ROL/ROR_dr","ROL/ROR_S","ROL/ROR_i/r",1,1,"ROL/ROR_REGISTER"],
}
# Note 1.0: The bits for the first word of CMP2 and CHK2 are the same.
#           We will figure out which one it actually is during the 
#           execute step.  The same goes for any opcode names with a /
#           in them.

INSTRUCTIONS = []
for i in range(2**16):
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
            pat            = PATTERNS[b]
            pattern_length = len( [ bit for bit in pat if bit in [0,1] ] )

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
        gen( OPCODES[op], op )

for i in range(len(INSTRUCTIONS)):
    if INSTRUCTIONS[i] != None:
        print( "{:016b} = 0x{:04X} = {:5d} -> {:s}".format( i, i, i, INSTRUCTIONS[i] ) )

# vim: set foldmethod=marker:
