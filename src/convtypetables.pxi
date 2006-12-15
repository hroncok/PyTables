#  Ei!, emacs, this is -*-Python-*- mode
########################################################################
#
#       License: BSD
#       Created: Sep 15, 2006
#       Author:  Francesc Altet - faltet@carabos.com
#
#       $Id: convtypetables.pxi 1808 2006-09-15 10:33:19Z faltet $
#
########################################################################

"""Tables for type conversion between PyTables, NumPy & HDF5
"""

import sys

# Definitions that are platform-independent
from definitions cimport \
     NPY_BOOL, NPY_STRING, \
     NPY_INT8, NPY_INT16, NPY_INT32, NPY_INT64, \
     NPY_UINT8, NPY_UINT16, NPY_UINT32, NPY_UINT64, \
     NPY_FLOAT32, NPY_FLOAT64, NPY_COMPLEX64, NPY_COMPLEX128, \
     H5T_C_S1, H5T_UNIX_D32BE, H5T_UNIX_D64BE, \
     H5T_NO_CLASS, H5T_INTEGER, H5T_FLOAT, H5T_TIME, H5T_STRING, \
     H5T_BITFIELD, H5T_OPAQUE, H5T_COMPOUND, H5T_REFERENCE, \
     H5T_ENUM, H5T_VLEN, H5T_ARRAY

# Platform-dependent types
if sys.byteorder == "little":

  from definitions cimport \
       H5T_STD_B8LE, \
       H5T_STD_I8LE, H5T_STD_I16LE, H5T_STD_I32LE, H5T_STD_I64LE, \
       H5T_STD_U8LE, H5T_STD_U16LE, H5T_STD_U32LE, H5T_STD_U64LE, \
       H5T_IEEE_F32LE, H5T_IEEE_F64LE

  # Standard types, independent of the byteorder
  H5T_STD_B8   = H5T_STD_B8LE
  H5T_STD_I8   = H5T_STD_I8LE
  H5T_STD_I16  = H5T_STD_I16LE
  H5T_STD_I32  = H5T_STD_I32LE
  H5T_STD_I64  = H5T_STD_I64LE
  H5T_STD_U8   = H5T_STD_U8LE
  H5T_STD_U16  = H5T_STD_U16LE
  H5T_STD_U32  = H5T_STD_U32LE
  H5T_STD_U64  = H5T_STD_U64LE
  H5T_IEEE_F32 = H5T_IEEE_F32LE
  H5T_IEEE_F64 = H5T_IEEE_F64LE

else:  # sys.byteorder == "big"

  from definitions cimport \
       H5T_STD_B8BE, \
       H5T_STD_I8BE, H5T_STD_I16BE, H5T_STD_I32BE, H5T_STD_I64BE, \
       H5T_STD_U8BE, H5T_STD_U16BE, H5T_STD_U32BE, H5T_STD_U64BE, \
       H5T_IEEE_F32BE, H5T_IEEE_F64BE

  # Standard types, independent of the byteorder
  H5T_STD_B8   = H5T_STD_B8BE
  H5T_STD_I8   = H5T_STD_I8BE
  H5T_STD_I16  = H5T_STD_I16BE
  H5T_STD_I32  = H5T_STD_I32BE
  H5T_STD_I64  = H5T_STD_I64BE
  H5T_STD_U8   = H5T_STD_U8BE
  H5T_STD_U16  = H5T_STD_U16BE
  H5T_STD_U32  = H5T_STD_U32BE
  H5T_STD_U64  = H5T_STD_U64BE
  H5T_IEEE_F32 = H5T_IEEE_F32BE
  H5T_IEEE_F64 = H5T_IEEE_F64BE


#----------------------------------------------------------------------------

# Conversion from PyTables string types to HDF5 native types
# List only types that are susceptible of changing byteorder
# (complex & enumerated types are special and should not be listed here)
PTTypeToHDF5 = {
  'int8'   : H5T_STD_I8,   'uint8'  : H5T_STD_U8,
  'int16'  : H5T_STD_I16,  'uint16' : H5T_STD_U16,
  'int32'  : H5T_STD_I32,  'uint32' : H5T_STD_U32,
  'int64'  : H5T_STD_I64,  'uint64' : H5T_STD_U64,
  'float32': H5T_IEEE_F32, 'float64': H5T_IEEE_F64,
  # time datatypes cannot be distinguished if they are LE and BE
  # so, we (arbitrarily) always choose BE byteorder
  'time32' : H5T_UNIX_D32BE, 'time64' : H5T_UNIX_D64BE,
  }

# Special cases whose byteorder cannot be directly changed
PTSpecialKinds = ['bool', 'complex', 'string', 'enum']


# Names of HDF5 classes
HDF5ClassToString = {
  H5T_NO_CLASS  : 'H5T_NO_CLASS',
  H5T_INTEGER   : 'H5T_INTEGER',
  H5T_FLOAT     : 'H5T_FLOAT',
  H5T_TIME      : 'H5T_TIME',
  H5T_STRING    : 'H5T_STRING',
  H5T_BITFIELD  : 'H5T_BITFIELD',
  H5T_OPAQUE    : 'H5T_OPAQUE',
  H5T_COMPOUND  : 'H5T_COMPOUND',
  H5T_REFERENCE : 'H5T_REFERENCE',
  H5T_ENUM      : 'H5T_ENUM',
  H5T_VLEN      : 'H5T_VLEN',
  H5T_ARRAY     : 'H5T_ARRAY',
  }


# Conversion table from NumPy codes to NumPy type classes
NPCodeToType = {
  NPY_BOOL:      numpy.bool_,     NPY_STRING:     numpy.string_,
  NPY_INT8:      numpy.int8,      NPY_UINT8:      numpy.uint8,
  NPY_INT16:     numpy.int16,     NPY_UINT16:     numpy.uint16,
  NPY_INT32:     numpy.int32,     NPY_UINT32:     numpy.uint32,
  NPY_INT64:     numpy.int64,     NPY_UINT64:     numpy.uint64,
  NPY_FLOAT32:   numpy.float32,   NPY_FLOAT64:    numpy.float64,
  NPY_COMPLEX64: numpy.complex64, NPY_COMPLEX128: numpy.complex128,
  # Special cases:
  ord('t'): numpy.int32,          ord('T'):       numpy.float64,
##  ord('e'):      'Enum',  # fake type (the actual type canbe different)
  }


# # Conversion table from NumPy type classes to NumPy type codes
NPTypeToCode = {
  numpy.bool_:     NPY_BOOL,      numpy.string_:    NPY_STRING,
  numpy.int8:      NPY_INT8,      numpy.uint8:      NPY_UINT8,
  numpy.int16:     NPY_INT16,     numpy.uint16:     NPY_UINT16,
  numpy.int32:     NPY_INT32,     numpy.uint32:     NPY_UINT32,
  numpy.int64:     NPY_INT64,     numpy.uint64:     NPY_UINT64,
  numpy.float32:   NPY_FLOAT32,   numpy.float64:    NPY_FLOAT64,
  numpy.complex64: NPY_COMPLEX64, numpy.complex128: NPY_COMPLEX128,
  }


# Conversion from NumPy codes to PyTables string types
NPCodeToPTType = {
  NPY_BOOL:      'bool',      NPY_STRING:     'string',
  NPY_INT8:      'int8',      NPY_UINT8:      'uint8',
  NPY_INT16:     'int16',     NPY_UINT16:     'uint16',
  NPY_INT32:     'int32',     NPY_UINT32:     'uint32',
  NPY_INT64:     'int64',     NPY_UINT64:     'uint64',
  NPY_FLOAT32:   'float32',   NPY_FLOAT64:    'float64',
  NPY_COMPLEX64: 'complex64', NPY_COMPLEX128: 'complex128',
  # Special cases:
  ord('t'):      'time32',    ord('T'):       'time64',
  ord('e'):      'enum',
  }


# Conversion from PyTables string types to NumPy codes
PTTypeToNPCode = {}
for key, value in NPCodeToPTType.items():
  PTTypeToNPCode[value] = key

## Local Variables:
## mode: python
## py-indent-offset: 2
## tab-width: 2
## fill-column: 78
## End:
