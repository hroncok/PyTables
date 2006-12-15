import sys
import unittest
import os
import tempfile
import warnings

from numpy import *
from numpy import rec as records

from tables import *
import tables.tests.common as common
from tables.tests.common import verbose, allequal, areArraysEqual, \
     heavy, cleanup

# To delete the internal attributes automagically
unittest.TestCase.tearDown = cleanup

# Test Record class
class Record(IsDescription):
    var1 = StringCol(itemsize=4, dflt="abcd", pos=0) # 4-character String
    var2 = col_from_kind('int', dflt=1, pos=1)     # integer
    var3 = Int16Col(dflt=2, pos=2)                 # short integer
    var4 = Float64Col(dflt=3.1, pos=3)             # double (double-precision)
    var5 = Float32Col(dflt=4.2, pos=4)             # float  (single-precision)
    var6 = UInt16Col(dflt=5, pos=5)                # unsigned short integer
    var7 = StringCol(itemsize=1, dflt="e", pos=6)  # 1-character String
    var8 = BoolCol(dflt=True, pos=7)               # boolean
    var9 = ComplexCol(itemsize=8, dflt=(0.+1.j), pos=8) # Complex single precision
    var10 = ComplexCol(itemsize=16, dflt=(1.-0.j), pos=9) # Complex double precision

# A byte-reversed class definition
class RecordRevOrder(IsDescription):
    # Change the byteorder property for this table
    _v_byteorder = {"little":"big","big":"little"}[sys.byteorder]
    var1 = StringCol(itemsize=4, dflt="abcd", pos=0) # 4-character String
    var2 = col_from_kind('int', dflt=1, pos=1)     # integer
    var3 = Int16Col(dflt=2, pos=2)                 # short integer
    var4 = Float64Col(dflt=3.1, pos=3)             # double (double-precision)
    var5 = Float32Col(dflt=4.2, pos=4)             # float  (single-precision)
    var6 = UInt16Col(dflt=5, pos=5)                # unsigned short integer
    var7 = StringCol(itemsize=1, dflt="e", pos=6)  # 1-character String
    var8 = BoolCol(dflt=True, pos=7)               # boolean
    var9 = ComplexCol(itemsize=8, dflt=(0.+1.j), pos=8) # Complex single precision
    var10 = ComplexCol(itemsize=16, dflt=(1.-0.j), pos=9) # Complex double precision

#  Dictionary definition
RecordDescriptionDict = {
    'var1': StringCol(itemsize=4, dflt="abcd", pos=0), # 4-character String
    'var2': col_from_kind('int', dflt=1, pos=1), # integer
    'var3': Int16Col(dflt=2, pos=2),            # short integer
    'var4': col_from_kind('float', dflt=3.1, pos=3), # double (double-precision)
    'var5': Float32Col(dflt=4.2, pos=4),        # float  (single-precision)
    'var6': UInt16Col(dflt=5, pos=5),           # unsigned short integer
    'var7': StringCol(itemsize=1, dflt="e", pos=6), # 1-character String
    'var8': BoolCol(dflt=True, pos=7),          # boolean
    'var9': ComplexCol(itemsize=8, dflt=(0.+1.j), pos=8), # Complex single precision
    'var10': ComplexCol(itemsize=16, dflt=(1.-0.j), pos=9), # Complex double precision
    }

# A byte-reversed dictionary definition
RecordDescriptionDictRevOrder = {
    # Change the byteorder property for this table
    '_v_byteorder': {"little":"big","big":"little"}[sys.byteorder],
    'var1': StringCol(itemsize=4, dflt="abcd", pos=0), # 4-character String
    'var2': col_from_kind('int', dflt=1, pos=1), # integer
    'var3': Int16Col(dflt=2, pos=2),            # short integer
    'var4': col_from_kind('float', dflt=3.1, pos=3), # double (double-precision)
    'var5': Float32Col(dflt=4.2, pos=4),        # float  (single-precision)
    'var6': UInt16Col(dflt=5, pos=5),           # unsigned short integer
    'var7': StringCol(itemsize=1, dflt="e", pos=6), # 1-character String
    'var8': BoolCol(dflt=True, pos=7),          # boolean
    'var9': ComplexCol(itemsize=8, dflt=(0.+1.j), pos=8), # Complex single precision
    'var10': ComplexCol(itemsize=8, dflt=(1.-0.j), pos=9), # Complex double precision
    }


# Old fashion of defining tables (for testing backward compatibility)
class OldRecord(IsDescription):
    var1 = StringCol(itemsize=4, dflt="abcd", pos=0)
    var2 = col_from_type("int32", 1, 1, pos=1)
    var3 = col_from_type("int16", 1, 2, pos=2)
    var4 = col_from_type("float64", 1, 3.1, pos=3)
    var5 = col_from_type("float32", 1, 4.2, pos=4)
    var6 = col_from_type("uint16", 1, 5, pos=5)
    var7 = StringCol(itemsize=1, dflt="e", pos=6)
    var8 = col_from_type("bool", shape=1, dflt=1, pos=7)
    var9 = ComplexCol(itemsize=8, shape=1, dflt=(0.+1.j), pos=8)
    var10 = ComplexCol(itemsize=16, shape=1, dflt=(1.-0.j), pos = 9)

class OldRecordRevOrder(IsDescription):
    # Change the byteorder property for this table
    _v_byteorder = {"little":"big","big":"little"}[sys.byteorder]
    var1 = StringCol(itemsize=4, dflt="abcd", pos=0)
    var2 = col_from_type("int32", 1, 1, pos=1)
    var3 = col_from_type("int16", 1, 2, pos=2)
    var4 = col_from_type("float64", 1, 3.1, pos=3)
    var5 = col_from_type("float32", 1, 4.2, pos=4)
    var6 = col_from_type("uint16", 1, 5, pos=5)
    var7 = StringCol(itemsize=1, dflt="e", pos=6)
    var8 = col_from_type("bool", shape=1, dflt=1, pos=7)
    var9 = ComplexCol(itemsize=8, shape=1, dflt=(0.+1.j), pos=8)
    var10 = ComplexCol(itemsize=16, shape=1, dflt=(1.-0.j), pos = 9)

class BasicTestCase(common.PyTablesTestCase):
    #file  = "test.h5"
    mode  = "w"
    title = "This is the table title"
    expectedrows = 100
    appendrows = 20
    compress = 0
    shuffle = 0
    fletcher32 = 0
    complib = "zlib"  # Default compression library
    record = Record
    recordro = RecordRevOrder
    recarrayinit = 0
    maxshort = 1 << 15

    def setUp(self):

        # Create an instance of an HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, self.mode)
        self.rootgroup = self.fileh.root
        self.populateFile()
        self.fileh.close()

    def initRecArray(self):
        record = self.recordtemplate
        row = record[0]
        buflist = []
        # Fill the recarray
        for i in xrange(self.expectedrows):
            tmplist = []
            var1 = '%04d' % (self.expectedrows - i)
            tmplist.append(var1)
            var2 = i
            tmplist.append(var2)
            var3 = i % self.maxshort
            tmplist.append(var3)
            if isinstance(row['var4'], ndarray):
                tmplist.append([float(i), float(i*i)])
            else:
                tmplist.append(float(i))
            if isinstance(row['var5'], ndarray):
                tmplist.append(array((float(i),)*4))
            else:
                tmplist.append(float(i))
            # var6 will be like var3 but byteswaped
            tmplist.append(((var3>>8) & 0xff) + ((var3<<8) & 0xff00))
            var7 = var1[-1]
            tmplist.append(var7)
            if isinstance(row['var8'], ndarray):
                tmplist.append([0, 10])  # should be equivalent to [0,1]
            else:
                tmplist.append(10) # should be equivalent to 1
            if isinstance(row['var9'], ndarray):
                tmplist.append([0.+float(i)*1j, float(i)+0.j])
            else:
                tmplist.append(float(i)+0j)
            if isinstance(row['var10'], ndarray):
                tmplist.append([float(i)+0j, 1+float(i)*1j])
            else:
                tmplist.append(1+float(i)*1j)
            buflist.append(tmplist)

        self.record = records.array(buflist, dtype=record.dtype,
                                    shape = self.expectedrows)
        # The swapped version
        self.recordro = self.record.newbyteorder()
        return

    def populateFile(self):
        group = self.rootgroup
        if self.recarrayinit:
            # Initialize an starting buffer, if any
            self.initRecArray()
        for j in range(3):
            # Create a table
            filterprops = Filters(complevel = self.compress,
                                  shuffle = self.shuffle,
                                  fletcher32 = self.fletcher32,
                                  complib = self.complib)
            if j < 2:
                record = self.record
            else:
                # table2 will be byteswapped
                record = self.recordro
            table = self.fileh.createTable(group, 'table'+str(j), record,
                                           title = self.title,
                                           filters = filterprops,
                                           expectedrows = self.expectedrows)
            if not self.recarrayinit:
                # Get the row object associated with the new table
                row = table.row
                # Fill the table
                for i in xrange(self.expectedrows):
                    row['var1'] = '%04d' % (self.expectedrows - i)
                    row['var7'] = row['var1'][-1]
                    #row['var7'] = ('%04d' % (self.expectedrows - i))[-1]
                    row['var2'] = i
                    row['var3'] = i % self.maxshort
                    if isinstance(row['var4'], ndarray):
                        row['var4'] = [float(i), float(i*i)]
                    else:
                        row['var4'] = float(i)
                    if isinstance(row['var8'], ndarray):
                        row['var8'] = [0, 1]
                    else:
                        row['var8'] = 1
                    if isinstance(row['var9'], ndarray):
                        row['var9'] = [0.+float(i)*1j, float(i)+0.j]
                    else:
                        row['var9'] = float(i)+0.j
                    if isinstance(row['var10'], ndarray):
                        row['var10'] = [float(i)+0.j, 1.+float(i)*1j]
                    else:
                        row['var10'] = 1.+float(i)*1j
                    if isinstance(row['var5'], ndarray):
                        row['var5'] = array((float(i),)*4)
                    else:
                        row['var5'] = float(i)
                    # var6 will be like var3 but byteswaped
                    row['var6'] = ((row['var3']>>8) & 0xff) + \
                                  ((row['var3']<<8) & 0xff00)
                    #print("Saving -->", row)
                    row.append()

            # Flush the buffer for this table
            table.flush()
            # Create a new group (descendant of group)
            group2 = self.fileh.createGroup(group, 'group'+str(j))
            # Iterate over this new group (group2)
            group = group2


    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)
        cleanup(self)

    #----------------------------------------

    def test00_description(self):
        """Checking table description and descriptive fields"""

        self._verboseHeader()
        self.fileh = openFile(self.file)

        tbl = self.fileh.getNode('/table0')
        desc = tbl.description

        if isinstance(self.record, dict):
            columns = self.record
        elif isinstance(self.record, ndarray):
            # This way of getting a (dictionary) description
            # can be used as long as the method does not alter the table.
            # Maybe there is a better way of doing this.
            columns = tbl._descrFromRA(self.record)
            del columns['_v_byteorder']  # '_v_byteorder' is spureous
        else:
            # This is an ordinary description.
            columns = self.record.columns

        # Check table and description attributes at the same time.
        # These checks are only valid for non-nested tables.

        # Column names.
        expectedNames = ['var%d' % n
                         for n in range(1, len(columns) + 1)]
        self.assertEqual(expectedNames, list(tbl.colnames))
        self.assertEqual(expectedNames, list(desc._v_names))

        # Column instances.
        for colname in expectedNames:
            self.assert_( tbl.colinstances[colname]
                          is tbl.cols._f_col(colname) )

        # Column types.
        expectedTypes = [columns[colname].dtype
                         for colname in expectedNames]
        self.assertEqual(expectedTypes,
                         [tbl.coldtypes[v] for v in expectedNames])
        self.assertEqual(expectedTypes,
                         [desc._v_dtypes[v] for v in expectedNames])

        # Column string types.
        expectedTypes = [columns[colname].type
                         for colname in expectedNames]
        self.assertEqual(expectedTypes,
                         [tbl.coltypes[v] for v in expectedNames])
        self.assertEqual(expectedTypes,
                         [desc._v_types[v] for v in expectedNames])

        # Column defaults.
        for v in expectedNames:
            if verbose:
                print "dflt-->", columns[v].dflt, type(columns[v].dflt)
                print "coldflts-->", tbl.coldflts[v], type(tbl.coldflts[v])
                print "desc.dflts-->", desc._v_dflts[v], type(desc._v_dflts[v])
            assert areArraysEqual(tbl.coldflts[v], columns[v].dflt)
            assert areArraysEqual(desc._v_dflts[v], columns[v].dflt)

        # Column path names.
        self.assertEqual(expectedNames, list(desc._v_pathnames))

        # Column objects.
        for colName in expectedNames:
            expectedCol = columns[colName]
            col = desc._v_colObjects[colName]

            self.assertEqual(expectedCol.dtype, col.dtype)
            self.assertEqual(expectedCol.type, col.type)

    def test01_readTable(self):
        """Checking table read"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_readTable..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        table = self.fileh.getNode("/table0")

        # Choose a small value for buffer size
        table._v_nrowsinbuf = 3
        # Read the records and select those with "var2" file less than 20
        result = [ rec['var2'] for rec in table.iterrows()
                   if rec['var2'] < 20 ]
        if verbose:
            print "Nrows in", table._v_pathname, ":", table.nrows
            print "Last record in table ==>", rec
            print "Total selected records in table ==> ", len(result)
        nrows = self.expectedrows - 1
        assert (rec['var1'], rec['var2'], rec['var7']) == ("0001", nrows,"1")
        if isinstance(rec['var5'], ndarray):
            assert allequal(rec['var5'], array((float(nrows),)*4, float32))
        else:
            assert rec['var5'] == float(nrows)
        if isinstance(rec['var9'], ndarray):
            assert allequal(rec['var9'],
                            array([0.+float(nrows)*1.j,float(nrows)+0.j],
                                  complex64))
        else:
            assert (rec['var9']) == float(nrows)+0.j
        assert len(result) == 20

    def test01b_readTable(self):
        """Checking table read and cuts (multidimensional columns case)"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01b_readTable..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        table = self.fileh.getNode("/table0")

        # Choose a small value for buffer size
        table._v_nrowsinbuf = 3
        # Read the records and select those with "var2" file less than 20
        result = [ rec['var5'] for rec in table.iterrows()
                   if rec['var2'] < 20 ]
        if verbose:
            print "Nrows in", table._v_pathname, ":", table.nrows
            print "Last record in table ==>", rec
            print "rec['var5'] ==>", rec['var5'],
            print "nrows ==>", table.nrows
            print "Total selected records in table ==> ", len(result)
        nrows = table.nrows
        if isinstance(rec['var5'], ndarray):
            assert allequal(result[0], array((float(0),)*4, float32))
            assert allequal(result[1], array((float(1),)*4, float32))
            assert allequal(result[2], array((float(2),)*4, float32))
            assert allequal(result[3], array((float(3),)*4, float32))
            assert allequal(result[10], array((float(10),)*4, float32))
            assert allequal(rec['var5'], array((float(nrows-1),)*4, float32))
        else:
            assert rec['var5'] == float(nrows - 1)
        # Read the records and select those with "var2" file less than 20
        result = [ rec['var10'] for rec in table.iterrows()
                   if rec['var2'] < 20 ]
        if isinstance(rec['var10'], ndarray):
            assert allequal(result[0], array([float(0)+0.j, 1.+float(0)*1j],
                                             complex128))
            assert allequal(result[1], array([float(1)+0.j, 1.+float(1)*1j],
                                             complex128))
            assert allequal(result[2], array([float(2)+0.j, 1.+float(2)*1j],
                                             complex128))
            assert allequal(result[3], array([float(3)+0.j, 1.+float(3)*1j],
                                             complex128))
            assert allequal(result[10], array([float(10)+0.j, 1.+float(10)*1j],
                                              complex128))
            assert allequal(rec['var10'], array([float(nrows-1)+0.j,
                                                 1.+float(nrows-1)*1j],
                                                complex128))
        else:
            assert rec['var10'] == 1.+float(nrows-1)*1j
        assert len(result) == 20

    def test01c_readTable(self):
        """Checking nested iterators (reading)"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01c_readTable..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        table = self.fileh.getNode("/table0")

        # Read the records and select those with "var2" file less than 20
        result = []
        for rec in table.iterrows(stop=2):
            for rec2 in table.iterrows(stop=2):
                if rec2['var2'] < 20:
                    result.append([rec['var2'],rec2['var2']])
        if verbose:
            print "result ==>", result

        assert result == [[0, 0], [0, 1], [1, 0], [1, 1]]

    def test01d_readTable(self):
        """Checking nested iterators (reading, mixed conditions)"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01d_readTable..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        table = self.fileh.getNode("/table0")

        # Read the records and select those with "var2" file less than 20
        result = []
        for rec in table.iterrows(stop=2):
            for rec2 in table.where('var2 < 20', stop=2):
                result.append([rec['var2'],rec2['var2']])
        if verbose:
            print "result ==>", result

        assert result == [[0, 0], [0, 1], [1, 0], [1, 1]]

    def test01e_readTable(self):
        """Checking nested iterators (reading, both conditions)"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01e_readTable..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        table = self.fileh.getNode("/table0")

        # Read the records and select those with "var2" file less than 20
        result = []
        for rec in table.where('var3 < 2'):
            for rec2 in table.where('var2 < 3'):
                result.append([rec['var2'],rec2['var3']])
        if verbose:
            print "result ==>", result

        assert result == [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2]]

    def test01f_readTable(self):
        """Checking nested iterators (reading, break in the loop)"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01f_readTable..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        table = self.fileh.getNode("/table0")

        # Read the records and select those with "var2" file less than 20
        result = []
        for rec in table.where('var3 < 2'):
            for rec2 in table.where('var2 < 4'):
                if rec2['var2'] >= 3:
                    break
                result.append([rec['var2'],rec2['var3']])
        if verbose:
            print "result ==>", result

        assert result == [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2]]

    def test01g_readTable(self):
        """Checking iterator with an evanescent table."""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01g_readTable..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")

        # Read from an evanescent table
        result = [ rec['var2'] for rec in self.fileh.getNode("/table0")
                   if rec['var2'] < 20 ]

        assert len(result) == 20

    def test02_AppendRows(self):
        """Checking whether appending record rows works or not"""

        # Now, open it, but in "append" mode
        self.fileh = openFile(self.file, mode = "a")
        self.rootgroup = self.fileh.root
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_AppendRows..." % self.__class__.__name__

        # Get a table
        table = self.fileh.getNode("/group0/table1")
        # Get their row object
        row = table.row
        if verbose:
            print "Nrows in old", table._v_pathname, ":", table.nrows
            print "Record Format ==>", table.description._v_nestedFormats
            print "Record Size ==>", table.rowsize
        # Append some rows
        for i in xrange(self.appendrows):
            row['var1'] = '%04d' % (self.appendrows - i)
            row['var7'] = row['var1'][-1]
            row['var2'] = i
            row['var3'] = i % self.maxshort
            if isinstance(row['var4'], ndarray):
                row['var4'] = [float(i), float(i*i)]
            else:
                row['var4'] = float(i)
            if isinstance(row['var8'], ndarray):
                row['var8'] = [0, 1]
            else:
                row['var8'] = 1
            if isinstance(row['var9'], ndarray):
                row['var9'] = [0.+float(i)*1j, float(i)+0.j]
            else:
                row['var9'] = float(i)+0.j
            if isinstance(row['var10'], ndarray):
                row['var10'] = [float(i)+0.j, 1.+float(i)*1j]
            else:
                row['var10'] = 1.+float(i)*1j
            if isinstance(row['var5'], ndarray):
                row['var5'] = array((float(i),)*4)
            else:
                row['var5'] = float(i)
            row.append()

        # Flush the buffer for this table and read it
        table.flush()
        result = [ row['var2'] for row in table.iterrows()
                   if row['var2'] < 20 ]

        nrows = self.appendrows - 1
        assert (row['var1'], row['var2'], row['var7']) == ("0001", nrows, "1")
        if isinstance(row['var5'], ndarray):
            assert allequal(row['var5'], array((float(nrows),)*4, float32))
        else:
            assert row['var5'] == float(nrows)
        if self.appendrows <= 20:
            add = self.appendrows
        else:
            add = 20
        assert len(result) == 20 + add  # because we appended new rows

    # This test has been commented out because appending records without
    # flushing them explicitely is being warned from now on.
    # F. Altet 2006-08-03
    def _test02a_AppendRows(self):
        """Checking appending records without flushing explicitely"""

        # Now, open it, but in "append" mode
        self.fileh = openFile(self.file, mode = "a")
        self.rootgroup = self.fileh.root
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02a_AppendRows..." % self.__class__.__name__

        group = self.rootgroup
        for i in range(3):
            # Get a table
            table = self.fileh.getNode(group, 'table'+str(i))
            # Get the next group
            group = self.fileh.getNode(group, 'group'+str(i))
            # Get their row object
            row = table.row
            if verbose:
                print "Nrows in old", table._v_pathname, ":", table.nrows
                print "Record Format ==>", table.description._v_nestedFormats
                print "Record Size ==>", table.rowsize
            # Append some rows
            for i in xrange(self.appendrows):
                row['var1'] = '%04d' % (self.appendrows - i)
                row['var7'] = row['var1'][-1]
                row['var2'] = i
                row['var3'] = i % self.maxshort
                if isinstance(row['var4'], ndarray):
                    row['var4'] = [float(i), float(i*i)]
                else:
                    row['var4'] = float(i)
                if isinstance(row['var8'], ndarray):
                    row['var8'] = [0, 1]
                else:
                    row['var8'] = 1
                if isinstance(row['var9'], ndarray):
                    row['var9'] = [0.+float(i)*1j, float(i)+0.j]
                else:
                    row['var9'] = float(i)+0.j
                if isinstance(row['var10'], ndarray):
                    row['var10'] = [float(i)+0.j, 1.+float(i)*1j]
                else:
                    row['var10'] = 1.+float(i)*1j
                if isinstance(row['var5'], ndarray):
                    row['var5'] = array((float(i),)*4)
                else:
                    row['var5'] = float(i)
                row.append()
            table.flush()

        # Close the file and re-open it.
        self.fileh.close()

        self.fileh = openFile(self.file, mode = "a")
        table = self.fileh.root.table0
        # Flush the buffer for this table and read it
        result = [ row['var2'] for row in table.iterrows()
                   if row['var2'] < 20 ]

        nrows = self.appendrows - 1
        assert (row['var1'], row['var2'], row['var7']) == ("0001", nrows, "1")
        if isinstance(row['var5'], ndarray):
            assert allequal(row['var5'], array((float(nrows),)*4, float32))
        else:
            assert row['var5'] == float(nrows)
        if self.appendrows <= 20:
            add = self.appendrows
        else:
            add = 20
        assert len(result) == 20 + add  # because we appended new rows

    # This is meant to check bug report #1186892, but I did not
    # work...
    # It seems to work now. 2005-06-16
    def test02b_AppendRows(self):
        """Checking whether appending *and* reading rows works or not"""

        # Now, open it, but in "append" mode
        self.fileh = openFile(self.file, mode = "a")
        self.rootgroup = self.fileh.root
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02b_AppendRows..." % self.__class__.__name__

        # Get a table
        table = self.fileh.getNode("/group0/table1")
        if verbose:
            print "Nrows in old", table._v_pathname, ":", table.nrows
            print "Record Format ==>", table.description._v_nestedFormats
            print "Record Size ==>", table.rowsize
        # Set a small number of buffer to make this test faster
        table._v_nrowsinbuf=3
        # Get their row object
        row = table.row
        # Append some rows (3*table._v_nrowsinbuf is enough for
        # checking purposes)
        for i in xrange(3*table._v_nrowsinbuf):
            row['var1'] = '%04d' % (self.appendrows - i)
            row['var7'] = row['var1'][-1]
            #row['var7'] = table.cols['var1'][i][-1]
            row['var2'] = i
            row['var3'] = i % self.maxshort
            if isinstance(row['var4'], ndarray):
                row['var4'] = [float(i), float(i*i)]
            else:
                row['var4'] = float(i)
            if isinstance(row['var8'], ndarray):
                row['var8'] = [0, 1]
            else:
                row['var8'] = 1
            if isinstance(row['var9'], ndarray):
                row['var9'] = [0.+float(i)*1j, float(i)+0.j]
            else:
                row['var9'] = float(i)+0.j
            if isinstance(row['var10'], ndarray):
                row['var10'] = [float(i)+0.j, 1.+float(i)*1j]
            else:
                row['var10'] = 1.+float(i)*1j
            if isinstance(row['var5'], ndarray):
                row['var5'] = array((float(i),)*4)
            else:
                row['var5'] = float(i)
            row.append()
            # the next call can mislead the counters
            result = [ row2['var2'] for row2 in table ]
            # warning! the next will result into wrong results
            #result = [ row['var2'] for row in table ]
            # This is because the iterator for writing and for reading
            # cannot be shared!


        # Do not flush the buffer for this table and try to read it
        # We are forced now to flush tables after append operations
        # because of unsolved issues with the LRU cache that are too
        # difficult to track.
        # F. Altet 2006-08-03
        table.flush()
        result = [ row['var2'] for row in table.iterrows()
                   if row['var2'] < 20 ]
        if verbose:
            print "Result length ==>", len(result)
            print "Result contents ==>", result
        assert len(result) == 20+3*table._v_nrowsinbuf
        assert result == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                          10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                          0, 1, 2, 3, 4, 5, 6, 7, 8]
        # Check consistency of I/O buffers when doing mixed I/O operations
        # That is, the next should work in these operations
        # row['var1'] = '%04d' % (self.appendrows - i)
        # row['var7'] = row['var1'][-1]
        result7 = [ row['var7'] for row in table.iterrows()
                    if row['var2'] < 20 ]
        if verbose:
            print "Result7 length ==>", len(result7)
            print "Result7 contents ==>", result7
        assert result7 == ['0', '9', '8', '7', '6', '5', '4', '3', '2', '1',
                           '0', '9', '8', '7', '6', '5', '4', '3', '2', '1',
                           '0', '9', '8', '7', '6', '5', '4', '3', '2']

    # This test is commented out as it should not work anymore due to
    # the new policy of not doing a flush in the middle of a __del__
    # operation. F. Altet 2006-08-24
    def _test02c_AppendRows(self):
        """Checking appending with evanescent table objects"""

        # This test is kind of magic, but it is a good sanity check anyway.

        # Now, open it, but in "append" mode
        self.fileh = openFile(self.file, mode = "a")
        self.rootgroup = self.fileh.root
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02c_AppendRows..." % self.__class__.__name__

        # Get a table
        table = self.fileh.getNode("/group0/table1")
        if verbose:
            print "Nrows in old", table._v_pathname, ":", table.nrows
            print "Record Format ==>", table.description._v_nestedFormats
            print "Record Size ==>", table.rowsize
        # Set a small number of buffer to make this test faster
        table._v_nrowsinbuf=3
        # Get their row object
        self.row = table.row
        # delete the table reference
        del table
        # Append some rows
        for i in xrange(22):
            self.row['var2'] = 100+i
            self.row.append()
        # del self.row # force the table object to be destroyed (and the user warned!)
        # convert a warning in an error
        warnings.filterwarnings('error', category=PerformanceWarning)
        self.assertRaises(PerformanceWarning, self.__dict__.pop, 'row')
#         try:
#             self.__dict__.pop('row')  # force the table object to be destroyed
#         except PerformanceWarning:
#             if verbose:
#                 (type, value, traceback) = sys.exc_info()
#                 print "\nGreat!, the next PerformanceWarning was catched:"
#                 print value
#             # Ignore the warning and actually flush the table
#             warnings.filterwarnings("ignore", category=PerformanceWarning)
#             table = self.fileh.getNode("/group0/table1")
#             table.flush()
#         else:
#             self.fail("expected a PeformanceWarning")
        # reset the warning
        warnings.filterwarnings('default', category=PerformanceWarning)
        result = [ row['var2'] for row in table.iterrows()
                   if 100 <= row['var2'] < 122 ]
        if verbose:
            print "Result length ==>", len(result)
            print "Result contents ==>", result
        assert len(result) == 22
        assert [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
                111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121]

    # CAVEAT: The next test only works for tables with rows < 2**15
    def test03_endianess(self):
        """Checking if table is endianess aware"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_endianess..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        table = self.fileh.getNode("/group0/group1/table2")

        # Read the records and select the ones with "var6" column less than 20
        result = [ rec['var2'] for rec in table.iterrows() if rec['var6'] < 20]
        if verbose:
            print "Nrows in", table._v_pathname, ":", table.nrows
            print "Last record in table ==>", rec
            print "Selected records ==>", result
            print "Total selected records in table ==>", len(result)
        nrows = self.expectedrows - 1
        assert (rec['var1'], rec['var6']) == ("0001", nrows)
        assert len(result) == 20

    def test04_delete(self):
        """Checking whether a single row can be deleted"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04_delete..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "a")
        table = self.fileh.getNode("/table0")

        # Read the records and select the ones with "var2" column less than 20
        result = [ r['var2'] for r in table.iterrows() if r['var2'] < 20]

        if verbose:
            print "Nrows in", table._v_pathname, ":", table.nrows
            print "Last selected value ==>", result[-1]
            print "Total selected records in table ==>", len(result)

        nrows = table.nrows
        table._v_nrowsinbuf = 3  # small value of the buffer
        # Delete the twenty-th row
        table.removeRows(19)

        # Re-read the records
        result2 = [ r['var2'] for r in table.iterrows() if r['var2'] < 20]

        if verbose:
            print "Nrows in", table._v_pathname, ":", table.nrows
            print "Last selected value ==>", result2[-1]
            print "Total selected records in table ==>", len(result2)

        assert table.nrows == nrows - 1
        assert table.shape == (nrows - 1,)
        # Check that the new list is smaller than the original one
        assert len(result) == len(result2) + 1
        assert result[:-1] == result2

    def test04b_delete(self):
        """Checking whether a range of rows can be deleted"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04b_delete..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "a")
        table = self.fileh.getNode("/table0")

        # Read the records and select the ones with "var2" column less than 20
        result = [ r['var2'] for r in table.iterrows() if r['var2'] < 20]

        if verbose:
            print "Nrows in", table._v_pathname, ":", table.nrows
            print "Last selected value ==>", result[-1]
            print "Total selected records in table ==>", len(result)

        nrows = table.nrows
        table._v_nrowsinbuf = 4  # small value of the buffer
        # Delete the last ten rows
        table.removeRows(10, 20)

        # Re-read the records
        result2 = [ r['var2'] for r in table.iterrows() if r['var2'] < 20]

        if verbose:
            print "Nrows in", table._v_pathname, ":", table.nrows
            print "Last selected value ==>", result2[-1]
            print "Total selected records in table ==>", len(result2)

        assert table.nrows == nrows - 10
        assert table.shape == (nrows - 10,)
        # Check that the new list is smaller than the original one
        assert len(result) == len(result2) + 10
        assert result[:10] == result2

    def test04c_delete(self):
        """Checking whether removing a bad range of rows is detected"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04c_delete..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "a")
        table = self.fileh.getNode("/table0")

        # Read the records and select the ones with "var2" column less than 20
        result = [ r['var2'] for r in table.iterrows() if r['var2'] < 20]

        nrows = table.nrows
        table._v_nrowsinbuf = 5  # small value of the buffer
        # Delete a too large range of rows
        table.removeRows(10, nrows + 100)

        # Re-read the records
        result2 = [ r['var2'] for r in table.iterrows() if r['var2'] < 20]

        if verbose:
            print "Nrows in", table._v_pathname, ":", table.nrows
            print "Last selected value ==>", result2[-1]
            print "Total selected records in table ==>", len(result2)

        assert table.nrows == 10
        assert table.shape == (10,)
        # Check that the new list is smaller than the original one
        assert len(result) == len(result2) + 10
        assert result[:10] == result2

    def test04d_delete(self):
        """Checking whether removing rows several times at once is working"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04d_delete..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "a")
        table = self.fileh.getNode("/table0")

        # Read the records and select the ones with "var2" column less than 20
        result = [ r['var2'] for r in table if r['var2'] < 20]

        nrows = table.nrows
        nrowsinbuf = table._v_nrowsinbuf
        table._v_nrowsinbuf = 6  # small value of the buffer
        # Delete some rows
        table.removeRows(10, 15)
        # It's necessary to restore the value of buffer to use the row object
        # afterwards...
        table._v_nrowsinbuf = nrowsinbuf

        # Append some rows
        row = table.row
        for i in xrange(10, 15):
            row['var1'] = '%04d' % (self.appendrows - i)
            # This line gives problems on Windows. Why?
            #row['var7'] = row['var1'][-1]
            row['var2'] = i
            row['var3'] = i % self.maxshort
            if isinstance(row['var4'], ndarray):
                row['var4'] = [float(i), float(i*i)]
            else:
                row['var4'] = float(i)
            if isinstance(row['var8'], ndarray):
                row['var8'] = [0, 1]
            else:
                row['var8'] = 1
            if isinstance(row['var9'], ndarray):
                row['var9'] = [0.+float(i)*1j, float(i)+0.j]
            else:
                row['var9'] = float(i)+0.j
            if isinstance(row['var10'], ndarray):
                row['var10'] = [float(i)+0.j, 1.+float(i)*1j]
            else:
                row['var10'] = 1.+float(i)*1j
            if isinstance(row['var5'], ndarray):
                row['var5'] = array((float(i),)*4)
            else:
                row['var5'] = float(i)
            row.append()
        # Flush the buffer for this table
        table.flush()

        # Delete 5 rows more
        table.removeRows(5, 10)

        # Re-read the records
        result2 = [ r['var2'] for r in table if r['var2'] < 20 ]

        if verbose:
            print "Nrows in", table._v_pathname, ":", table.nrows
            print "Last selected value ==>", result2[-1]
            print "Total selected records in table ==>", len(result2)

        assert table.nrows == nrows - 5
        assert table.shape == (nrows - 5,)
        # Check that the new list is smaller than the original one
        assert len(result) == len(result2) + 5
        # The last values has to be equal
        assert result[10:15] == result2[10:15]

    def test05_filtersTable(self):
        """Checking tablefilters"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test05_filtersTable..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        table = self.fileh.getNode("/table0")

        # Check filters:
        if self.compress <> table.filters.complevel and verbose:
            print "Error in compress. Class:", self.__class__.__name__
            print "self, table:", self.compress, table.filters.complevel
        tinfo = whichLibVersion(self.complib)
        if tinfo is None:
            self.complib = "zlib"
        assert table.filters.complib == self.complib
        assert table.filters.complevel == self.compress
        if self.shuffle <> table.filters.shuffle and verbose:
            print "Error in shuffle. Class:", self.__class__.__name__
            print "self, table:", self.shuffle, table.filters.shuffle
        assert self.shuffle == table.filters.shuffle
        if self.fletcher32 <> table.filters.fletcher32 and verbose:
            print "Error in fletcher32. Class:", self.__class__.__name__
            print "self, table:", self.fletcher32, table.filters.fletcher32
        assert self.fletcher32 == table.filters.fletcher32

class BasicWriteTestCase(BasicTestCase):
    title = "BasicWrite"

class OldRecordBasicWriteTestCase(BasicTestCase):
    title = "OldRecordBasicWrite"
    record = OldRecord
    recordro = OldRecordRevOrder

class DictWriteTestCase(BasicTestCase):
    # This checks also unidimensional arrays as columns
    title = "DictWrite"
    record = RecordDescriptionDict
    recordro = RecordDescriptionDictRevOrder
    nrows = 21
    nrowsinbuf = 3  # Choose a small value for the buffer size
    start = 0
    stop = 10
    step = 3

class RecArrayOneWriteTestCase(BasicTestCase):
    title = "RecArrayOneWrite"
    record=records.array(
        None, shape=0,
        formats="a4,i4,i2,2f8,f4,i2,a1,b1,c8,c16",
        names='var1,var2,var3,var4,var5,var6,var7,var8,var9,var10')

class RecArrayTwoWriteTestCase(BasicTestCase):
    title = "RecArrayTwoWrite"
    expectedrows = 100
    recarrayinit = 1
    recordtemplate=records.array(
        None, shape=1,
        formats="a4,i4,i2,f8,f4,i2,a1,b1,2c8,c16",
        names='var1,var2,var3,var4,var5,var6,var7,var8,var9,var10')

class RecArrayThreeWriteTestCase(BasicTestCase):
    title = "RecArrayThreeWrite"
    expectedrows = 100
    recarrayinit = 1
    recordtemplate=records.array(
        None, shape=1,
        formats="a4,i4,i2,2f8,4f4,i2,a1,2b1,c8,c16",
        names='var1,var2,var3,var4,var5,var6,var7,var8,var9,var10')

class CompressLZOTablesTestCase(BasicTestCase):
    title = "CompressLZOTables"
    compress = 1
    complib = "lzo"

class CompressLZOShuffleTablesTestCase(BasicTestCase):
    title = "CompressLZOTables"
    compress = 1
    shuffle = 1
    complib = "lzo"

class CompressBZIP2TablesTestCase(BasicTestCase):
    title = "CompressBZIP2Tables"
    compress = 1
    complib = "bzip2"

class CompressBZIP2ShuffleTablesTestCase(BasicTestCase):
    title = "CompressBZIP2Tables"
    compress = 1
    shuffle = 1
    complib = "bzip2"

class CompressZLIBTablesTestCase(BasicTestCase):
    title = "CompressOneTables"
    compress = 1
    complib = "zlib"

class CompressZLIBShuffleTablesTestCase(BasicTestCase):
    title = "CompressOneTables"
    compress = 1
    shuffle = 1
    complib = "zlib"

class Fletcher32TablesTestCase(BasicTestCase):
    title = "Fletcher32Tables"
    fletcher32 = 1
    shuffle = 0
    complib = "zlib"

class AllFiltersTablesTestCase(BasicTestCase):
    title = "AllFiltersTables"
    compress = 1
    fletcher32 = 1
    shuffle = 1
    complib = "zlib"

class CompressTwoTablesTestCase(BasicTestCase):
    title = "CompressTwoTables"
    compress = 1
    # This checks also unidimensional arrays as columns
    record = RecordDescriptionDict
    recordro = RecordDescriptionDictRevOrder

class BigTablesTestCase(BasicTestCase):
    title = "BigTables"
    # 10000 rows takes much more time than we can afford for tests
    # reducing to 1000 would be more than enough
    # F. Altet 2004-01-19
    # Will be executed only in heavy mode
    expectedrows = 10000
    appendrows = 100

class BasicRangeTestCase(unittest.TestCase):
    #file  = "test.h5"
    mode  = "w"
    title = "This is the table title"
    record = Record
    maxshort = 1 << 15
    expectedrows = 100
    compress = 0
    shuffle = 1
    # Default values
    nrows = 20
    nrowsinbuf = 3  # Choose a small value for the buffer size
    start = 1
    stop = nrows
    checkrecarray = 0
    checkgetCol = 0

    def setUp(self):
        # Create an instance of an HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, self.mode)
        self.rootgroup = self.fileh.root
        self.populateFile()
        self.fileh.close()

    def populateFile(self):
        group = self.rootgroup
        for j in range(3):
            # Create a table
            filterprops = Filters(complevel = self.compress,
                                  shuffle = self.shuffle)
            table = self.fileh.createTable(group, 'table'+str(j), self.record,
                                           title = self.title,
                                           filters = filterprops,
                                           expectedrows = self.expectedrows)
            # Get the row object associated with the new table
            row = table.row

            # Fill the table
            for i in xrange(self.expectedrows):
                row['var1'] = '%04d' % (self.expectedrows - i)
                row['var7'] = row['var1'][-1]
                row['var2'] = i
                row['var3'] = i % self.maxshort
                if isinstance(row['var4'], ndarray):
                    row['var4'] = [float(i), float(i*i)]
                else:
                    row['var4'] = float(i)
                if isinstance(row['var5'], ndarray):
                    row['var5'] = array((float(i),)*4)
                else:
                    row['var5'] = float(i)
                # var6 will be like var3 but byteswaped
                row['var6'] = ((row['var3'] >> 8) & 0xff) + \
                              ((row['var3'] << 8) & 0xff00)
                row.append()

            # Flush the buffer for this table
            table.flush()
            # Create a new group (descendant of group)
            group2 = self.fileh.createGroup(group, 'group'+str(j))
            # Iterate over this new group (group2)
            group = group2


    def tearDown(self):
        if self.fileh.isopen:
            self.fileh.close()
        os.remove(self.file)
        cleanup(self)

    #----------------------------------------

    def check_range(self):

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        table = self.fileh.getNode("/table0")

        table._v_nrowsinbuf = self.nrowsinbuf
        r = slice(self.start, self.stop, self.step)
        resrange = r.indices(table.nrows)
        reslength = len(range(*resrange))
        if self.checkrecarray:
            recarray = table.read(self.start, self.stop, self.step)
            result = []
            for nrec in range(len(recarray)):
                if recarray['var2'][nrec] < self.nrows:
                    result.append(recarray['var2'][nrec])
        elif self.checkgetCol:
            column = table.read(self.start, self.stop, self.step, 'var2')
            result = []
            for nrec in range(len(column)):
                if column[nrec] < self.nrows:
                    result.append(column[nrec])
        else:
            result = [ rec['var2'] for rec in
                       table.iterrows(self.start, self.stop, self.step)
                       if rec['var2'] < self.nrows ]

        if self.start < 0:
            startr = self.expectedrows + self.start
        else:
            startr = self.start

        if self.stop == None:
            stopr = startr+1
        elif self.stop < 0:
            stopr = self.expectedrows + self.stop
        else:
            stopr = self.stop

        if self.nrows < stopr:
            stopr = self.nrows

        if verbose:
            print "Nrows in", table._v_pathname, ":", table.nrows
            if reslength:
                if self.checkrecarray:
                    print "Last record *read* in recarray ==>", recarray[-1]
                elif self.checkgetCol:
                    print "Last value *read* in getCol ==>", column[-1]
                else:
                    print "Last record *read* in table range ==>", rec
            print "Total number of selected records ==>", len(result)
            print "Selected records:\n", result
            print "Selected records should look like:\n", \
                  range(startr, stopr, self.step)
            print "start, stop, step ==>", self.start, self.stop, self.step
            print "startr, stopr, step ==>", startr, stopr, self.step

        assert result == range(startr, stopr, self.step)
        if startr < stopr and not (self.checkrecarray or self.checkgetCol):
            if self.nrows < self.expectedrows:
                assert rec['var2'] == range(self.start, self.stop, self.step)[-1]
            else:
                assert rec['var2'] == range(startr, stopr, self.step)[-1]

        # Close the file
        self.fileh.close()

    def test01_range(self):
        """Checking ranges in table iterators (case1)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_range..." % self.__class__.__name__

        # Case where step < nrowsinbuf < 2*step
        self.nrows = 21
        self.nrowsinbuf = 3
        self.start = 0
        self.stop = self.expectedrows
        self.step = 2

        self.check_range()

    def test02_range(self):
        """Checking ranges in table iterators (case2)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_range..." % self.__class__.__name__

        # Case where step < nrowsinbuf < 10*step
        self.nrows = 21
        self.nrowsinbuf = 31
        self.start = 11
        self.stop = self.expectedrows
        self.step = 3

        self.check_range()

    def test03_range(self):
        """Checking ranges in table iterators (case3)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_range..." % self.__class__.__name__

        # Case where step < nrowsinbuf < 1.1*step
        self.nrows = self.expectedrows
        self.nrowsinbuf = 11  # Choose a small value for the buffer size
        self.start = 0
        self.stop = self.expectedrows
        self.step = 10

        self.check_range()

    def test04_range(self):
        """Checking ranges in table iterators (case4)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04_range..." % self.__class__.__name__

        # Case where step == nrowsinbuf
        self.nrows = self.expectedrows
        self.nrowsinbuf = 11  # Choose a small value for the buffer size
        self.start = 1
        self.stop = self.expectedrows
        self.step = 11

        self.check_range()

    def test05_range(self):
        """Checking ranges in table iterators (case5)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test05_range..." % self.__class__.__name__

        # Case where step > 1.1*nrowsinbuf
        self.nrows = 21
        self.nrowsinbuf = 10  # Choose a small value for the buffer size
        self.start = 1
        self.stop = self.expectedrows
        self.step = 11

        self.check_range()

    def test06_range(self):
        """Checking ranges in table iterators (case6)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test06_range..." % self.__class__.__name__

        # Case where step > 3*nrowsinbuf
        self.nrows = 3
        self.nrowsinbuf = 3  # Choose a small value for the buffer size
        self.start = 2
        self.stop = self.expectedrows
        self.step = 10

        self.check_range()

    def test07_range(self):
        """Checking ranges in table iterators (case7)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test07_range..." % self.__class__.__name__

        # Case where start == stop
        self.nrows = 2
        self.nrowsinbuf = 3  # Choose a small value for the buffer size
        self.start = self.nrows
        self.stop = self.nrows
        self.step = 10

        self.check_range()

    def test08_range(self):
        """Checking ranges in table iterators (case8)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test08_range..." % self.__class__.__name__

        # Case where start > stop
        self.nrows = 2
        self.nrowsinbuf = 3  # Choose a small value for the buffer size
        self.start = self.nrows + 1
        self.stop = self.nrows
        self.step = 1

        self.check_range()

    def test09_range(self):
        """Checking ranges in table iterators (case9)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test09_range..." % self.__class__.__name__

        # Case where stop = None (last row)
        self.nrows = 100
        self.nrowsinbuf = 3  # Choose a small value for the buffer size
        self.start = 1
        self.stop = None
        self.step = 1

        self.check_range()

    def test10_range(self):
        """Checking ranges in table iterators (case10)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test10_range..." % self.__class__.__name__

        # Case where start < 0 and stop = None (last row)
        self.nrows = self.expectedrows
        self.nrowsinbuf = 5  # Choose a small value for the buffer size
        self.start = -6
        self.startr = self.expectedrows + self.start
        self.stop = 0
        self.stop = None
        self.stopr = self.expectedrows
        self.step = 2

        self.check_range()

    def test10a_range(self):
        """Checking ranges in table iterators (case10a)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test10a_range..." % self.__class__.__name__

        # Case where start < 0 and stop = 0
        self.nrows = self.expectedrows
        self.nrowsinbuf = 5  # Choose a small value for the buffer size
        self.start = -6
        self.startr = self.expectedrows + self.start
        self.stop = 0
        self.stopr = self.expectedrows
        self.step = 2

        self.check_range()

    def test11_range(self):
        """Checking ranges in table iterators (case11)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test11_range..." % self.__class__.__name__

        # Case where start < 0 and stop < 0
        self.nrows = self.expectedrows
        self.nrowsinbuf = 5  # Choose a small value for the buffer size
        self.start = -6
        self.startr = self.expectedrows + self.start
        self.stop = -2
        self.stopr = self.expectedrows + self.stop
        self.step = 1

        self.check_range()

    def test12_range(self):
        """Checking ranges in table iterators (case12)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test12_range..." % self.__class__.__name__

        # Case where start < 0 and stop < 0 and start > stop
        self.nrows = self.expectedrows
        self.nrowsinbuf = 5  # Choose a small value for the buffer size
        self.start = -1
        self.startr = self.expectedrows + self.start
        self.stop = -2
        self.stopr = self.expectedrows + self.stop
        self.step = 1

        self.check_range()

    def test13_range(self):
        """Checking ranges in table iterators (case13)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test13_range..." % self.__class__.__name__

        # Case where step < 0
        self.step = -11
        try:
            self.check_range()
        except ValueError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next ValueError was catched!"
                print value
            self.fileh.close()
        else:
            print rec
            self.fail("expected a ValueError")

        # Case where step == 0
        self.step = 0
        try:
            self.check_range()
        except ValueError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next ValueError was catched!"
                print value
            self.fileh.close()
        else:
            print rec
            self.fail("expected a ValueError")


class IterRangeTestCase(BasicRangeTestCase):
    pass

class RecArrayRangeTestCase(BasicRangeTestCase):
    checkrecarray = 1

class getColRangeTestCase(BasicRangeTestCase):
    checkgetCol = 1

    def test01_nonexistentField(self):
        """Checking non-existing Field in getCol method """

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_nonexistentField..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        self.root = self.fileh.root
        table = self.fileh.getNode("/table0")

        try:
            #column = table.read(field='non-existent-column')
            column = table.col('non-existent-column')
        except KeyError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next KeyError was catched!"
                print value
            self.fileh.close()
        else:
            print rec
            self.fail("expected a KeyError")


    def test02_getItemCol(self):
        """Using ``__getitem__`` to get a column."""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_getItemCol..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        self.root = self.fileh.root
        table = self.fileh.getNode("/table0")

        warnings.filterwarnings('error', category=DeprecationWarning)
        self.assertRaises(DeprecationWarning, (lambda o, i: o[i]), table, 'var1')
        warnings.filterwarnings('default', category=DeprecationWarning)

        self.fileh.close()


class getItemTestCase(unittest.TestCase):
    mode  = "w"
    title = "This is the table title"
    record = Record
    maxshort = 1 << 15
    expectedrows = 100
    compress = 0
    shuffle = 1
    # Default values
    nrows = 20
    nrowsinbuf = 3  # Choose a small value for the buffer size
    start = 1
    stop = nrows
    checkrecarray = 0
    checkgetCol = 0

    def setUp(self):
        # Create an instance of an HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, self.mode)
        self.rootgroup = self.fileh.root
        self.populateFile()
        self.fileh.close()

    def populateFile(self):
        group = self.rootgroup
        for j in range(3):
            # Create a table
            filterprops = Filters(complevel = self.compress,
                                  shuffle = self.shuffle)
            table = self.fileh.createTable(group, 'table'+str(j), self.record,
                                           title = self.title,
                                           filters = filterprops,
                                           expectedrows = self.expectedrows)
            # Get the row object associated with the new table
            row = table.row

            # Fill the table
            for i in xrange(self.expectedrows):
                row['var1'] = '%04d' % (self.expectedrows - i)
                row['var7'] = row['var1'][-1]
                row['var2'] = i
                row['var3'] = i % self.maxshort
                if isinstance(row['var4'], ndarray):
                    row['var4'] = [float(i), float(i*i)]
                else:
                    row['var4'] = float(i)
                if isinstance(row['var5'], ndarray):
                    row['var5'] = array((float(i),)*4)
                else:
                    row['var5'] = float(i)
                # var6 will be like var3 but byteswaped
                row['var6'] = ((row['var3'] >> 8) & 0xff) + \
                              ((row['var3'] << 8) & 0xff00)
                row.append()

            # Flush the buffer for this table
            table.flush()
            # Create a new group (descendant of group)
            group2 = self.fileh.createGroup(group, 'group'+str(j))
            # Iterate over this new group (group2)
            group = group2


    def tearDown(self):
        if self.fileh.isopen:
            self.fileh.close()
        os.remove(self.file)
        cleanup(self)

    #----------------------------------------

    def test01a_singleItem(self):
        """Checking __getitem__ method with single parameter (int) """

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01a_singleItem..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        table = self.fileh.root.table0
        result = table[2]
        assert result["var2"] == 2
        #assert result[1] == 2
        result = table[25]
        assert result["var2"] == 25
        #assert result[1] == 25
        result = table[self.expectedrows-1]
        assert result["var2"] == self.expectedrows - 1
        #assert result[1] == self.expectedrows - 1

    def test01b_singleItem(self):
        """Checking __getitem__ method with single parameter (neg. int)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01b_singleItem..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        table = self.fileh.root.table0
        result = table[-5]
        assert result["var2"] == self.expectedrows - 5
        #assert result[1] == self.expectedrows - 5
        result = table[-1]
        assert result["var2"] == self.expectedrows - 1
        #assert result[1] == self.expectedrows - 1
        result = table[-self.expectedrows]
        assert result["var2"] == 0
        #assert result[1] == 0

    def test01c_singleItem(self):
        """Checking __getitem__ method with single parameter (long)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01c_singleItem..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        table = self.fileh.root.table0
        result = table[2L]
        assert result["var2"] == 2
        #assert result[1L] == 2
        result = table[25L]
        assert result["var2"] == 25
        #assert result[1L] == 25
        result = table[self.expectedrows-1]
        assert result["var2"] == self.expectedrows - 1
        #assert result[1L] == self.expectedrows - 1

    def test01d_singleItem(self):
        """Checking __getitem__ method with single parameter (neg. long)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01d_singleItem..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        table = self.fileh.root.table0
        result = table[-5L]
        assert result["var2"] == self.expectedrows - 5
        #assert result[1L] == self.expectedrows - 5
        result = table[-1L]
        assert result["var2"] == self.expectedrows - 1
        #assert result[1L] == self.expectedrows - 1
        result = table[-self.expectedrows]
        assert result["var2"] == 0
        #assert result[1L] == 0

    def test02_twoItems(self):
        """Checking __getitem__ method with start, stop parameters """

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_twoItem..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        table = self.fileh.root.table0
        result = table[2:6]
        assert result["var2"].tolist() == range(2,6)
        result = table[2:-6]
        assert result["var2"].tolist() == range(2,self.expectedrows-6)
        result = table[2:]
        assert result["var2"].tolist() == range(2,self.expectedrows)
        result = table[-2:]
        assert result["var2"].tolist() == range(self.expectedrows-2,self.expectedrows)

    def test03_threeItems(self):
        """Checking __getitem__ method with start, stop, step parameters """

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_threeItem..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        table = self.fileh.root.table0
        result = table[2:6:3]
        assert result["var2"].tolist() == range(2,6,3)
        result = table[2::3]
        assert result["var2"].tolist() == range(2,self.expectedrows,3)
        result = table[:6:2]
        assert result["var2"].tolist() == range(0,6,2)
        result = table[::]
        assert result["var2"].tolist() == range(0,self.expectedrows,1)

    def test04_negativeStep(self):
        """Checking __getitem__ method with negative step parameter"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04_negativeStep..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        table = self.fileh.root.table0
        try:
            table[2:3:-3]
        except ValueError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next ValueError was catched!"
                print value
        else:
            self.fail("expected a ValueError")


    def test06a_singleItemCol(self):
        """Checking __getitem__ method in Col with single parameter """

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test06a_singleItemCol..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        colvar2 = self.fileh.root.table0.cols.var2
        assert colvar2[2] == 2
        assert colvar2[25] == 25
        assert colvar2[self.expectedrows-1] == self.expectedrows - 1

    def test06b_singleItemCol(self):
        """Checking __getitem__ method in Col with single parameter (negative)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test06b_singleItem..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        colvar2 = self.fileh.root.table0.cols.var2
        assert colvar2[-5] == self.expectedrows - 5
        assert colvar2[-1] == self.expectedrows - 1
        assert colvar2[-self.expectedrows] == 0

    def test07_twoItemsCol(self):
        """Checking __getitem__ method in Col with start, stop parameters """

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test07_twoItemCol..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        colvar2 = self.fileh.root.table0.cols.var2
        assert colvar2[2:6].tolist() == range(2,6)
        assert colvar2[2:-6].tolist() == range(2,self.expectedrows-6)
        assert colvar2[2:].tolist() == range(2,self.expectedrows)
        assert colvar2[-2:].tolist() == range(self.expectedrows-2,self.expectedrows)

    def test08_threeItemsCol(self):
        """Checking __getitem__ method in Col with start, stop, step parameters """

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test08_threeItemCol..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        colvar2 = self.fileh.root.table0.cols.var2
        assert colvar2[2:6:3].tolist() == range(2,6,3)
        assert colvar2[2::3].tolist() == range(2,self.expectedrows,3)
        assert colvar2[:6:2].tolist() == range(0,6,2)
        assert colvar2[::].tolist() == range(0,self.expectedrows,1)

    def test09_negativeStep(self):
        """Checking __getitem__ method in Col with negative step parameter"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test09_negativeStep..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        colvar2 = self.fileh.root.table0.cols.var2
        try:
            colvar2[2:3:-3]
        except ValueError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next ValueError was catched!"
                print value
        else:
            self.fail("expected a ValueError")


class Rec(IsDescription):
    col1 = col_from_kind('int', pos=1)
    col2 = StringCol(itemsize=3, pos=2)
    col3 = col_from_kind('float', pos=3)

class setItem(common.PyTablesTestCase):

    def tearDown(self):
        self.fileh.close()
        #del self.fileh, self.rootgroup
        os.remove(self.file)
        cleanup(self)

    def test01(self):
        "Checking modifying one table row with __setitem__"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify just one existing row
        table[2] = (456,'db2',1.2)
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'ded',1.3],
                          [456,'db2',1.2],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

    def test01b(self):
        "Checking modifying one table row with __setitem__ (long index)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify just one existing row
        table[2L] = (456,'db2',1.2)
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'ded',1.3],
                          [456,'db2',1.2],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

    def test02(self):
        "Modifying one row, with a step (__setitem__)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify two existing rows
        rows = records.array([[457,'db1',1.2],[6,'de2',1.3]],
                             formats="i4,a3,f8")
        table[1:3:2] = rows
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[457,'db1',1.2],
                          [457,'db1',1.2],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

    def test03(self):
        "Checking modifying several rows at once (__setitem__)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify two existing rows
        rows = records.array([[457,'db1',1.2],[5,'de1',1.3]],
                             formats="i4,a3,f8")
        #table.modifyRows(start=1, rows=rows)
        table[1:3] = rows
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[457,'db1',1.2],
                          [5,'de1',1.3],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

    def test04(self):
        "Modifying several rows at once, with a step (__setitem__)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify two existing rows
        rows = records.array([[457,'db1',1.2],[6,'de2',1.3]],
                             formats="i4,a3,f8")
        #table[1:4:2] = rows
        table[1::2] = rows
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[457,'db1',1.2],
                          [457,'db1',1.2],[6,'de2',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

    def test05(self):
        "Checking modifying one column (single element, __setitem__)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify just one existing column
        table.cols.col1[1] = -1
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[-1,'ded',1.3],
                          [457,'db1',1.2],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

    def test06a(self):
        "Checking modifying one column (several elements, __setitem__)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify just one existing column
        table.cols.col1[1:4] = [2,3,4]
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'ded',1.3],
                          [3,'db1',1.2],[4,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

    def test06b(self):
        "Checking modifying one column (iterator, __setitem__)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify just one existing column
        try:
            for row in table.iterrows():
                row['col1'] = row.nrow+1
                row.append()
            table.flush()
        except NotImplementedError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next NotImplementedError was catched!"
                print value
        else:
            self.fail("expected a NotImplementedError")

#         # Create the modified recarray
#         r1=records.array([[1,'dbe',1.2],[2,'ded',1.3],
#                           [3,'db1',1.2],[4,'de1',1.3]],
#                          formats="i4,a3,f8",
#                          names = "col1,col2,col3")
#         # Read the modified table
#         if self.reopen:
#             self.fileh.close()
#             self.fileh = openFile(self.file, "r")
#             table = self.fileh.root.recarray
#             table._v_nrowsinbuf = self.buffersize  # set buffer value
#         r2 = table.read()
#         if verbose:
#             print "Original table-->", repr(r2)
#             print "Should look like-->", repr(r1)
#         assert r1.tostring() == r2.tostring()
#         assert table.nrows == 4

    def test07(self):
        "Modifying one column (several elements, __setitem__, step)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[1,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])
        # Modify just one existing column
        table.cols.col1[1:4:2] = [2,3]
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'ded',1.3],
                          [457,'db1',1.2],[3,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

    def test08(self):
        "Modifying one column (one element, __setitem__, step)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify just one existing column
        table.cols.col1[1:4:3] = [2]
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'ded',1.3],
                          [457,'db1',1.2],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

    def test09(self):
        "Modifying beyond the table extend (__setitem__, step)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Try to modify beyond the extend
        # This will silently exclude the non-fitting rows
        rows = records.array([[457,'db1',1.2],[6,'de2',1.3],[457,'db1',1.2]],
                             formats="i4,a3,f8")
        table[1:6:2] = rows
        # How it should look like
        r1 = records.array([[456,'dbe',1.2],[457,'db1',1.2],
                            [457,'db1',1.2],[6,'de2',1.3]],
                           formats="i4,a3,f8")

        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

class setItem1(setItem):
    reopen=0
    buffersize = 1

class setItem2(setItem):
    reopen=1
    buffersize = 2

class setItem3(setItem):
    reopen=0
    buffersize = 1000

class setItem4(setItem):
    reopen=1
    buffersize = 1000


class updateRow(common.PyTablesTestCase):

    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)
        cleanup(self)

    def test01(self):
        "Checking modifying one table row with Row.update"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify just one existing row
        for row in table.iterrows(2):
            (row['col1'], row['col2'], row['col3']) = [456,'db2',1.2]
            row.update()
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'ded',1.3],
                          [456,'db2',1.2],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4


    def test02(self):
        "Modifying one row, with a step (Row.update)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify two existing rows
        for row in table.iterrows(1, 3, 2):
            if row.nrow == 1:
                (row['col1'], row['col2'], row['col3']) = [457,'db1',1.2]
            elif row.nrow == 3:
                (row['col1'], row['col2'], row['col3']) = [6,'de2',1.3]
            row.update()
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[457,'db1',1.2],
                          [457,'db1',1.2],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

    def test03(self):
        "Checking modifying several rows at once (Row.update)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify two existing rows
        for row in table.iterrows(1, 3):
            if row.nrow == 1:
                (row['col1'], row['col2'], row['col3']) = [457,'db1',1.2]
            elif row.nrow == 2:
                (row['col1'], row['col2'], row['col3']) = [5,'de1',1.3]
            row.update()
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[457,'db1',1.2],
                          [5,'de1',1.3],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

    def test04(self):
        "Modifying several rows at once, with a step (Row.update)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify two existing rows
        for row in table.iterrows(1, stop=4, step=2):
            if row.nrow == 1:
                (row['col1'], row['col2'], row['col3']) = [457,'db1',1.2]
            elif row.nrow == 3:
                (row['col1'], row['col2'], row['col3']) = [6,'de2',1.3]
            row.update()
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[457,'db1',1.2],
                          [457,'db1',1.2],[6,'de2',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

    def test05(self):
        "Checking modifying one column (single element, Row.update)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify just one existing column
        for row in table.iterrows(1):
            row['col1'] = -1
            row.update()
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[-1,'ded',1.3],
                          [457,'db1',1.2],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

    def test06(self):
        "Checking modifying one column (several elements, Row.update)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify just one existing column
        for row in table.iterrows(1,4):
            row['col1'] = row.nrow+1
            row.update()
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'ded',1.3],
                          [3,'db1',1.2],[4,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

    def test07(self):
        "Modifying values from a selection"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        # append new rows
        r=records.array([[456,'dbe',1.2],[1,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])
        # Modify just rows with col1 < 456
        for row in table.where('col1 < 456'):
            row['col1'] = 2
            row['col2'] = 'ada'
            row.update()
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'ada',1.3],
                          [457,'db1',1.2],[2,'ada',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

    def test08(self):
        "Modifying a large table (Row.update)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        nrows = 100
        # append new rows
        row = table.row
        for i in xrange(nrows):
            row['col1'] = i-1
            row['col2'] = 'a'+str(i-1)
            row['col3'] = -1.0
            row.append()
        table.flush()

        # Modify all the rows
        for row in table:
            row['col1'] = row.nrow
            row['col2'] = 'b'+str(row.nrow)
            row['col3'] = 0.0
            row.update()

        # Create the modified recarray
        r1=records.array(None, shape=nrows,
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        for i in xrange(nrows):
            r1['col1'][i] = i
            r1['col2'][i] = 'b'+str(i)
            r1['col3'][i] = 0.0
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == nrows

    def test08b(self):
        "Setting values on a large table without calling Row.update"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        nrows = 100
        # append new rows
        row = table.row
        for i in xrange(nrows):
            row['col1'] = i-1
            row['col2'] = 'a'+str(i-1)
            row['col3'] = -1.0
            row.append()
        table.flush()

        # Modify all the rows (actually don't)
        for row in table:
            row['col1'] = row.nrow
            row['col2'] = 'b'+str(row.nrow)
            row['col3'] = 0.0
            #row.update()

        # Create the modified recarray
        r1=records.array(None, shape=nrows,
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        for i in xrange(nrows):
            r1['col1'][i] = i-1
            r1['col2'][i] = 'a'+str(i-1)
            r1['col3'][i] = -1.0
        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == nrows

    def test09(self):
        "Modifying selected values on a large table"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        nrows = 100
        # append new rows
        row = table.row
        for i in xrange(nrows):
            row['col1'] = i-1
            row['col2'] = 'a'+str(i-1)
            row['col3'] = -1.0
            row.append()
        table.flush()

        # Modify selected rows
        for row in table.where('col1 > nrows-3'):
            row['col1'] = row.nrow
            row['col2'] = 'b'+str(row.nrow)
            row['col3'] = 0.0
            row.update()

        # Create the modified recarray
        r1=records.array(None, shape=nrows,
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        for i in xrange(nrows):
            r1['col1'][i] = i-1
            r1['col2'][i] = 'a'+str(i-1)
            r1['col3'][i] = -1.0
        # modify just the last line
        r1['col1'][i] = i
        r1['col2'][i] = 'b'+str(i)
        r1['col3'][i] = 0.0

        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == nrows

    def test09b(self):
        "Modifying selected values on a large table (alternate values)"

        self._verboseHeader()

        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")

        # Create a new table:
        table = self.fileh.createTable(self.fileh.root, 'recarray', Rec)
        table._v_nrowsinbuf = self.buffersize  # set buffer value

        nrows = 100
        # append new rows
        row = table.row
        for i in xrange(nrows):
            row['col1'] = i-1
            row['col2'] = 'a'+str(i-1)
            row['col3'] = -1.0
            row.append()
        table.flush()

        # Modify selected rows
        for row in table.iterrows(step=10):
            row['col1'] = row.nrow
            row['col2'] = 'b'+str(row.nrow)
            row['col3'] = 0.0
            row.update()

        # Create the modified recarray
        r1=records.array(None, shape=nrows,
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        for i in xrange(nrows):
            if i % 10 > 0:
                r1['col1'][i] = i-1
                r1['col2'][i] = 'a'+str(i-1)
                r1['col3'][i] = -1.0
            else:
                r1['col1'][i] = i
                r1['col2'][i] = 'b'+str(i)
                r1['col3'][i] = 0.0

        # Read the modified table
        if self.reopen:
            self.fileh.close()
            self.fileh = openFile(self.file, "r")
            table = self.fileh.root.recarray
            table._v_nrowsinbuf = self.buffersize  # set buffer value
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == nrows


class updateRow1(updateRow):
    reopen=0
    buffersize = 1

class updateRow2(updateRow):
    reopen=1
    buffersize = 2

class updateRow3(updateRow):
    reopen=0
    buffersize = 1000

class updateRow4(updateRow):
    reopen=1
    buffersize = 1000


class RecArrayIO(unittest.TestCase):

    def test00(self):
        "Checking saving a regular recarray"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test00..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a recarray
        r=records.array([[456,'dbe',1.2],[2,'de',1.3]],names='col1,col2,col3')

        # Save it in a table:
        fileh.createTable(fileh.root, 'recarray', r)

        # Read it again
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
        r2 = fileh.root.recarray.read()
        assert r.tostring() == r2.tostring()

        fileh.close()
        os.remove(file)

    def test01(self):
        "Checking saving a recarray with an offset in its buffer"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a recarray
        r=records.array([[456,'dbe',1.2],[2,'de',1.3]],names='col1,col2,col3')

        # Get an offsetted bytearray
        r1 = r[1:]

        # Save it in a table:
        fileh.createTable(fileh.root, 'recarray', r1)

        # Read it again
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
        r2 = fileh.root.recarray.read()

        assert r1.tostring() == r2.tostring()

        fileh.close()
        os.remove(file)

    def test02(self):
        "Checking saving a large recarray with an offset in its buffer"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a recarray
        r=records.array('a'*200000,'f4,3i4,a5,i2',3000)

        # Get an offsetted bytearray
        r1 = r[2000:]

        # Save it in a table:
        fileh.createTable(fileh.root, 'recarray', r1)

        # Read it again
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
        r2 = fileh.root.recarray.read()

        assert r1.tostring() == r2.tostring()

        fileh.close()
        os.remove(file)

    def test03(self):
        "Checking saving a strided recarray with an offset in its buffer"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a recarray
        r=records.array('a'*200000,'f4,3i4,a5,i2',3000)

        # Get an strided recarray
        r2 = r[::2]

        # Get an offsetted bytearray
        r1 = r2[1200:]

        # Save it in a table:
        fileh.createTable(fileh.root, 'recarray', r1)

        # Read it again
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
        r2 = fileh.root.recarray.read()

        assert r1.tostring() == r2.tostring()
        fileh.close()
        os.remove(file)

    def test04(self):
        "Checking appending several rows at once"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        class Rec(IsDescription):
            col1 = col_from_kind('int', pos=1)
            col2 = StringCol(itemsize=3, pos=2)
            col3 = col_from_kind('float', pos=3)

        # Save it in a table:
        table = fileh.createTable(fileh.root, 'recarray', Rec)

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])
        # Create the complete table
        r1=records.array([[456,'dbe',1.2],[2,'ded',1.3],
                          [457,'db1',1.2],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the original table
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
            table = fileh.root.recarray
        r2 = fileh.root.recarray.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

        fileh.close()
        os.remove(file)

    def test05(self):
        "Checking appending several rows at once (close file version)"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test05..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Save it in a table:
        table = fileh.createTable(fileh.root, 'recarray', Rec)

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        fileh.close()
        fileh = openFile(file, "r")
        table = fileh.root.recarray
        # Create the complete table
        r1=records.array([[456,'dbe',1.2],[2,'ded',1.3],
                          [457,'db1',1.2],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the original table
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
            table = fileh.root.recarray
        r2 = fileh.root.recarray.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

        fileh.close()
        os.remove(file)

    def test06a(self):
        "Checking modifying one table row (list version)"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test06a..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a new table:
        table = fileh.createTable(fileh.root, 'recarray', Rec)

        # append new rows
        r=records.array([(456,'dbe',1.2),(2,'ded',1.3)], formats="i4,a3,f8")
        table.append(r)
        table.append([(457,'db1',1.2),(5,'de1',1.3)])
        # Modify just one existing rows
        table.modifyRows(start=1, rows=[(456,'db1',1.2)])
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[456,'db1',1.2],
                          [457,'db1',1.2],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
            table = fileh.root.recarray
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

        fileh.close()
        os.remove(file)

    def test06b(self):
        "Checking modifying one table row (recarray version)"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test06b..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a new table:
        table = fileh.createTable(fileh.root, 'recarray', Rec)

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])
        # Modify just one existing rows
        table.modifyRows(start=2, rows=records.array([[456,'db2',1.2]],
                                                     formats="i4,a3,f8"))
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'ded',1.3],
                          [456,'db2',1.2],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
            table = fileh.root.recarray
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

        fileh.close()
        os.remove(file)

    def test07a(self):
        "Checking modifying several rows at once (list version)"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test07a..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a new table:
        table = fileh.createTable(fileh.root, 'recarray', Rec)

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])
        # Modify two existing rows
        table.modifyRows(start=1, rows=[(457,'db1',1.2),(5,'de1',1.3)])
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[457,'db1',1.2],
                          [5,'de1',1.3],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
            table = fileh.root.recarray
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

        fileh.close()
        os.remove(file)

    def test07b(self):
        "Checking modifying several rows at once (recarray version)"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test07b..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a new table:
        table = fileh.createTable(fileh.root, 'recarray', Rec)

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])
        # Modify two existing rows
        rows = records.array([[457,'db1',1.2],[5,'de1',1.3]],
                             formats="i4,a3,f8")
        table.modifyRows(start=1, rows=rows)
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[457,'db1',1.2],
                          [5,'de1',1.3],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
            table = fileh.root.recarray
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

        fileh.close()
        os.remove(file)

    def test08a(self):
        "Checking modifying one column (single column version)"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test08a..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a new table:
        table = fileh.createTable(fileh.root, 'recarray', Rec)

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify just one existing column
        table.modifyColumns(start=1, columns=[[2,3,4]], names=["col1"])
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'ded',1.3],
                          [3,'db1',1.2],[4,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
            table = fileh.root.recarray
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

        fileh.close()
        os.remove(file)

    def test08a2(self):
        "Checking modifying one column (single column version, modifyColumn)"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test08a2..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a new table:
        table = fileh.createTable(fileh.root, 'recarray', Rec)

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify just one existing column
        table.modifyColumn(start=1, column=[2,3,4], colname="col1")
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'ded',1.3],
                          [3,'db1',1.2],[4,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
            table = fileh.root.recarray
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

        fileh.close()
        os.remove(file)

    def test08b(self):
        "Checking modifying one column (single column version, recarray)"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test08b..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a new table:
        table = fileh.createTable(fileh.root, 'recarray', Rec)

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify just one existing column
        columns = records.fromarrays(array([[2,3,4]]), formats="i4")
        table.modifyColumns(start=1, columns=columns, names=["col1"])
        #table.cols.col1[1:] = [2,3,4]
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'ded',1.3],
                          [3,'db1',1.2],[4,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
            table = fileh.root.recarray
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

        fileh.close()
        os.remove(file)

    def test08b2(self):
        "Checking modifying one column (single column version, recarray, modifyColumn)"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test08b2..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a new table:
        table = fileh.createTable(fileh.root, 'recarray', Rec)

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify just one existing column
        columns = records.fromarrays(array([[2,3,4]]), formats="i4")
        table.modifyColumn(start=1, column=columns, colname="col1")
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'ded',1.3],
                          [3,'db1',1.2],[4,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
            table = fileh.root.recarray
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

        fileh.close()
        os.remove(file)

    def test08c(self):
        "Checking modifying one column (single column version, single element)"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test08c..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a new table:
        table = fileh.createTable(fileh.root, 'recarray', Rec)

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify just one existing column
        columns = records.fromarrays(array([[4]]), formats="i4")
        #table.modifyColumns(start=1, columns=columns, names=["col1"])
        table.modifyColumns(start=1, columns=[[4]], names=["col1"])
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[4,'ded',1.3],
                          [457,'db1',1.2],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
            table = fileh.root.recarray
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

        fileh.close()
        os.remove(file)

    def test09a(self):
        "Checking modifying table columns (multiple column version)"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test09a..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a new table:
        table = fileh.createTable(fileh.root, 'recarray', Rec)

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify a couple of columns
        columns = [["aaa","bbb","ccc"], [1.2, .1, .3]]
        table.modifyColumns(start=1, columns=columns, names=["col2", "col3"])
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'aaa',1.2],
                          [457,'bbb',.1],[5,'ccc',.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")

        # Read the modified table
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
            table = fileh.root.recarray
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

        fileh.close()
        os.remove(file)

    def test09b(self):
        "Checking modifying table columns (multiple columns, recarray)"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test09b..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a new table:
        table = fileh.createTable(fileh.root, 'recarray', Rec)

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify a couple of columns
        columns = records.array([["aaa",1.2],["bbb", .1], ["ccc", .3]],
                                formats="a3,f8")
        table.modifyColumns(start=1, columns=columns, names=["col2", "col3"])
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'aaa',1.2],
                          [457,'bbb',.1],[5,'ccc',.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
            table = fileh.root.recarray
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

        fileh.close()
        os.remove(file)

    def test09c(self):
        "Checking modifying table columns (single column, step)"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test09c..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a new table:
        table = fileh.createTable(fileh.root, 'recarray', Rec)

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])
        # Modify a couple of columns
        columns = records.array([["aaa",1.2],["bbb", .1]],
                                formats="a3,f8")
        table.modifyColumns(start=1, step=2, columns=columns,
                            names=["col2", "col3"])
        # Create the modified recarray
        r1=records.array([[456,'dbe',1.2],[2,'aaa',1.2],
                          [457,'db1',1.2],[5,'bbb',.1]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
            table = fileh.root.recarray
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

        fileh.close()
        os.remove(file)

    def test09d(self):
        "Checking modifying table columns (multiple columns, step)"

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test09d..." % self.__class__.__name__

        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a new table:
        table = fileh.createTable(fileh.root, 'recarray', Rec)

        # append new rows
        r=records.array([[456,'dbe',1.2],[2,'ded',1.3]], formats="i4,a3,f8")
        table.append(r)
        table.append([[457,'db1',1.2],[5,'de1',1.3]])

        # Modify a couple of columns
        columns = records.array([["aaa",1.3],["bbb", .1]],
                                formats="a3,f8")
        table.modifyColumns(start=0, step=2, columns=columns,
                            names=["col2", "col3"])
        # Create the modified recarray
        r1=records.array([[456,'aaa',1.3],[2,'ded',1.3],
                          [457,'bbb',.1],[5,'de1',1.3]],
                         formats="i4,a3,f8",
                         names = "col1,col2,col3")
        # Read the modified table
        if self.reopen:
            fileh.close()
            fileh = openFile(file, "r")
            table = fileh.root.recarray
        r2 = table.read()
        if verbose:
            print "Original table-->", repr(r2)
            print "Should look like-->", repr(r1)
        assert r1.tostring() == r2.tostring()
        assert table.nrows == 4

        fileh.close()
        os.remove(file)


class RecArrayIO1(RecArrayIO):
    reopen=0

class RecArrayIO2(RecArrayIO):
    reopen=1

class CopyTestCase(unittest.TestCase):

    def assertEqualColinstances(self, table1, table2):
        """Assert that column instance maps of both tables are equal."""
        cinst1, cinst2 = table1.colinstances, table2.colinstances
        self.assertEqual(len(cinst1), len(cinst2))
        for (cpathname, col1) in cinst1.items():
            self.assert_(cpathname in cinst2)
            col2 = cinst2[cpathname]
            self.assert_(type(col1) is type(col2))
            if isinstance(col1, Column):
                self.assertEqual(col1.name, col2.name)
                self.assertEqual(col1.pathname, col2.pathname)
                self.assertEqual(col1.dtype, col2.dtype)
                self.assertEqual(col1.type, col2.type)
            elif isinstance(col1, Cols):
                self.assertEqual(col1._v_colnames, col2._v_colnames)
                self.assertEqual(col1._v_colpathnames, col2._v_colpathnames)

    def test01_copy(self):
        """Checking Table.copy() method """

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_copy..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a recarray
        r=records.array([[456,'dbe',1.2],[2,'de',1.3]],names='col1,col2,col3')
        # Save it in a table:
        table1 = fileh.createTable(fileh.root, 'table1', r, "title table1")

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            table1 = fileh.root.table1

        # Copy to another table
        table2 = table1.copy('/', 'table2')

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            table1 = fileh.root.table1
            table2 = fileh.root.table2

        if verbose:
            print "table1-->", table1.read()
            print "table2-->", table2.read()
            #print "dirs-->", dir(table1), dir(table2)
            print "attrs table1-->", repr(table1.attrs)
            print "attrs table2-->", repr(table2.attrs)

        # Check that all the elements are equal
        for row1 in table1:
            nrow = row1.nrow   # current row
            # row1 is a Row instance, while table2[] is a
            # RecArray.Record instance
            #print "reprs-->", repr(row1), repr(table2.read(nrow))
            for colname in table1.colnames:
                # Both ways to compare works well
                #assert row1[colname] == table2[nrow][colname)
                assert row1[colname] == table2.read(nrow, field=colname)[0]

        # Assert other properties in table
        assert table1.nrows == table2.nrows
        assert table1.shape == table2.shape
        assert table1.colnames == table2.colnames
        assert table1.coldtypes == table2.coldtypes
        self.assertEqualColinstances(table1, table2)
        assert repr(table1.description) == repr(table2.description)

        # This could be not the same when re-opening the file
        #assert table1.description._v_ColObjects == table2.description._v_ColObjects
        # Leaf attributes
        assert table1.title == table2.title
        assert table1.filters.complevel == table2.filters.complevel
        assert table1.filters.complib == table2.filters.complib
        assert table1.filters.shuffle == table2.filters.shuffle
        assert table1.filters.fletcher32 == table2.filters.fletcher32

        # Close the file
        fileh.close()
        os.remove(file)

    def test02_copy(self):
        """Checking Table.copy() method (where specified)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_copy..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a recarray
        r=records.array([[456,'dbe',1.2],[2,'de',1.3]],names='col1,col2,col3')
        # Save it in a table:
        table1 = fileh.createTable(fileh.root, 'table1', r, "title table1")

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            table1 = fileh.root.table1

        # Copy to another table in another group
        group1 = fileh.createGroup("/", "group1")
        table2 = table1.copy(group1, 'table2')

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "r")
            table1 = fileh.root.table1
            table2 = fileh.root.group1.table2

        if verbose:
            print "table1-->", table1.read()
            print "table2-->", table2.read()
            print "attrs table1-->", repr(table1.attrs)
            print "attrs table2-->", repr(table2.attrs)

        # Check that all the elements are equal
        for row1 in table1:
            nrow = row1.nrow   # current row
            for colname in table1.colnames:
                # Both ways to compare works well
                #assert row1[colname] == table2[nrow][colname)
                assert row1[colname] == table2.read(nrow, field=colname)[0]

        # Assert other properties in table
        assert table1.nrows == table2.nrows
        assert table1.shape == table2.shape
        assert table1.colnames == table2.colnames
        assert table1.coldtypes == table2.coldtypes
        self.assertEqualColinstances(table1, table2)
        assert repr(table1.description) == repr(table2.description)

        # Leaf attributes
        assert table1.title == table2.title
        assert table1.filters.complevel == table2.filters.complevel
        assert table1.filters.complib == table2.filters.complib
        assert table1.filters.shuffle == table2.filters.shuffle
        assert table1.filters.fletcher32 == table2.filters.fletcher32

        # Close the file
        fileh.close()
        os.remove(file)

    def test03_copy(self):
        """Checking Table.copy() method (table larger than buffer)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_copy..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a recarray exceeding buffers capability
        # This works, but takes too much CPU for a test
        # It is better to reduce the buffer size (table1._v_nrowsinbuf)
#         r=records.array('aaaabbbbccccddddeeeeffffgggg'*20000,
#                         formats='2i2,i4, (2,3)u2, (1,)f4, f8',shape=700)
        r=records.array('aaaabbbbccccddddeeeeffffgggg'*200,
                        formats='2i2,i4, (2,3)u2, (1,)f4, f8',shape=7)
        # Save it in a table:
        table1 = fileh.createTable(fileh.root, 'table1', r, "title table1")

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            table1 = fileh.root.table1

        # Copy to another table in another group and other title
        group1 = fileh.createGroup("/", "group1")
        table1._v_nrowsinbuf = 2  # small value of buffer
        table2 = table1.copy(group1, 'table2', title="title table2")
        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "r")
            table1 = fileh.root.table1
            table2 = fileh.root.group1.table2

        if verbose:
            print "table1-->", table1.read()
            print "table2-->", table2.read()
            print "attrs table1-->", repr(table1.attrs)
            print "attrs table2-->", repr(table2.attrs)

        # Check that all the elements are equal
        for row1 in table1:
            nrow = row1.nrow   # current row
            for colname in table1.colnames:
                #assert allequal(row1[colname], table2[nrow][colname])
                assert allequal(row1[colname], table2.read(nrow, field=colname)[0])

        # Assert other properties in table
        assert table1.nrows == table2.nrows
        assert table1.shape == table2.shape
        assert table1.colnames == table2.colnames
        assert table1.coldtypes == table2.coldtypes
        self.assertEqualColinstances(table1, table2)
        assert repr(table1.description) == repr(table2.description)

        # Leaf attributes
        assert "title table2" == table2.title
        assert table1.filters.complevel == table2.filters.complevel
        assert table1.filters.complib == table2.filters.complib
        assert table1.filters.shuffle == table2.filters.shuffle
        assert table1.filters.fletcher32 == table2.filters.fletcher32

        # Close the file
        fileh.close()
        os.remove(file)

    def test04_copy(self):
        """Checking Table.copy() method (different compress level)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04_copy..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a recarray
        r=records.array([[456,'dbe',1.2],[2,'de',1.3]],names='col1,col2,col3')
        # Save it in a table:
        table1 = fileh.createTable(fileh.root, 'table1', r, "title table1")

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            table1 = fileh.root.table1

        # Copy to another table in another group
        group1 = fileh.createGroup("/", "group1")
        table2 = table1.copy(group1, 'table2',
                             filters=Filters(complevel=6))

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "r")
            table1 = fileh.root.table1
            table2 = fileh.root.group1.table2

        if verbose:
            print "table1-->", table1.read()
            print "table2-->", table2.read()
            print "attrs table1-->", repr(table1.attrs)
            print "attrs table2-->", repr(table2.attrs)

        # Check that all the elements are equal
        for row1 in table1:
            nrow = row1.nrow   # current row
            for colname in table1.colnames:
                # Both ways to compare works well
                #assert row1[colname] == table2[nrow][colname)
                assert row1[colname] == table2.read(nrow, field=colname)[0]

        # Assert other properties in table
        assert table1.nrows == table2.nrows
        assert table1.shape == table2.shape
        assert table1.colnames == table2.colnames
        assert table1.coldtypes == table2.coldtypes
        self.assertEqualColinstances(table1, table2)
        assert repr(table1.description) == repr(table2.description)

        # Leaf attributes
        assert table1.title == table2.title
        assert 6 == table2.filters.complevel
        assert table1.filters.complib == table2.filters.complib
        assert 1 == table2.filters.shuffle
        assert table1.filters.fletcher32 == table2.filters.fletcher32

        # Close the file
        fileh.close()
        os.remove(file)

    def test05_copy(self):
        """Checking Table.copy() method (user attributes copied)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test05_copy..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a recarray
        r=records.array([[456,'dbe',1.2],[2,'de',1.3]],names='col1,col2,col3')
        # Save it in a table:
        table1 = fileh.createTable(fileh.root, 'table1', r, "title table1")
        # Add some user attributes
        table1.attrs.attr1 = "attr1"
        table1.attrs.attr2 = 2

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            table1 = fileh.root.table1

        # Copy to another table in another group
        group1 = fileh.createGroup("/", "group1")
        table2 = table1.copy(group1, 'table2',
                             copyuserattrs=1,
                             filters=Filters(complevel=6))

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "r")
            table1 = fileh.root.table1
            table2 = fileh.root.group1.table2

        if verbose:
            print "table1-->", table1.read()
            print "table2-->", table2.read()
            print "attrs table1-->", repr(table1.attrs)
            print "attrs table2-->", repr(table2.attrs)

        # Check that all the elements are equal
        for row1 in table1:
            nrow = row1.nrow   # current row
            for colname in table1.colnames:
                #assert row1[colname] == table2[nrow][colname)
                assert row1[colname] == table2.read(nrow, field=colname)[0]

        # Assert other properties in table
        assert table1.nrows == table2.nrows
        assert table1.shape == table2.shape
        assert table1.colnames == table2.colnames
        assert table1.coldtypes == table2.coldtypes
        self.assertEqualColinstances(table1, table2)
        assert repr(table1.description) == repr(table2.description)

        # Leaf attributes
        assert table1.title == table2.title
        assert 6 == table2.filters.complevel
        assert table1.filters.complib == table2.filters.complib
        assert 1 == table2.filters.shuffle
        assert table1.filters.fletcher32 == table2.filters.fletcher32
        # User attributes
        table2.attrs.attr1 == "attr1"
        table2.attrs.attr2 == 2

        # Close the file
        fileh.close()
        os.remove(file)

    def test05b_copy(self):
        """Checking Table.copy() method (user attributes not copied)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test05b_copy..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a recarray
        r=records.array([[456,'dbe',1.2],[2,'de',1.3]],names='col1,col2,col3')
        # Save it in a table:
        table1 = fileh.createTable(fileh.root, 'table1', r, "title table1")
        # Add some user attributes
        table1.attrs.attr1 = "attr1"
        table1.attrs.attr2 = 2

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            table1 = fileh.root.table1

        # Copy to another table in another group
        group1 = fileh.createGroup("/", "group1")
        table2 = table1.copy(group1, 'table2',
                             copyuserattrs=0,
                             filters=Filters(complevel=6))

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "r")
            table1 = fileh.root.table1
            table2 = fileh.root.group1.table2

        if verbose:
            print "table1-->", table1.read()
            print "table2-->", table2.read()
            print "attrs table1-->", repr(table1.attrs)
            print "attrs table2-->", repr(table2.attrs)

        # Check that all the elements are equal
        for row1 in table1:
            nrow = row1.nrow   # current row
            for colname in table1.colnames:
                #assert row1[colname] == table2[nrow][colname)
                assert row1[colname] == table2.read(nrow, field=colname)[0]

        # Assert other properties in table
        assert table1.nrows == table2.nrows
        assert table1.shape == table2.shape
        assert table1.colnames == table2.colnames
        assert table1.coldtypes == table2.coldtypes
        self.assertEqualColinstances(table1, table2)
        assert repr(table1.description) == repr(table2.description)

        # Leaf attributes
        assert table1.title == table2.title
        assert 6 == table2.filters.complevel
        assert table1.filters.complib == table2.filters.complib
        assert 1 == table2.filters.shuffle
        assert table1.filters.fletcher32 == table2.filters.fletcher32
        # User attributes
#         table2.attrs.attr1 == None
#         table2.attrs.attr2 == None
        hasattr(table2.attrs, "attr1") == 0
        hasattr(table2.attrs, "attr2") == 0

        # Close the file
        fileh.close()
        os.remove(file)

class CloseCopyTestCase(CopyTestCase):
    close = 1

class OpenCopyTestCase(CopyTestCase):
    close = 0

class CopyIndexTestCase(unittest.TestCase):

    def test01_index(self):
        """Checking Table.copy() method with indexes"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_index..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a recarray exceeding buffers capability
        r=records.array('aaaabbbbccccddddeeeeffffgggg'*200,
                        formats='2i2, (1,)i4, (2,3)u2, (1,)f4, (1,)f8',shape=10)
                        # The line below exposes a bug in numpy
                        #formats='2i2, i4, (2,3)u2, f4, f8',shape=10)
        # Save it in a table:
        table1 = fileh.createTable(fileh.root, 'table1', r, "title table1")

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            table1 = fileh.root.table1

        # Copy to another table
        table1._v_nrowsinbuf = self.nrowsinbuf
        table2 = table1.copy("/", 'table2',
                             start=self.start,
                             stop=self.stop,
                             step=self.step)
        if verbose:
            print "table1-->", table1.read()
            print "table2-->", table2.read()
            print "attrs table1-->", repr(table1.attrs)
            print "attrs table2-->", repr(table2.attrs)

        # Check that all the elements are equal
        r2 = r[self.start:self.stop:self.step]
        for nrow in range(r2.shape[0]):
            for colname in table1.colnames:
                assert allequal(r2[nrow][colname],
                                table2[nrow][colname])

        # Assert the number of rows in table
        if verbose:
            print "nrows in table2-->", table2.nrows
            print "and it should be-->", r2.shape[0]
        assert r2.shape[0] == table2.nrows

        # Close the file
        fileh.close()
        os.remove(file)

    def test02_indexclosef(self):
        """Checking Table.copy() method with indexes (close file version)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_indexclosef..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a recarray exceeding buffers capability
        r=records.array('aaaabbbbccccddddeeeeffffgggg'*200,
                        formats='2i2, i4, (2,3)u2, f4, f8',shape=10)
        # Save it in a table:
        table1 = fileh.createTable(fileh.root, 'table1', r, "title table1")

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            table1 = fileh.root.table1

        # Copy to another table
        table1._v_nrowsinbuf = self.nrowsinbuf
        table2 = table1.copy("/", 'table2',
                             start=self.start,
                             stop=self.stop,
                             step=self.step)

        fileh.close()
        fileh = openFile(file, mode = "r")
        table1 = fileh.root.table1
        table2 = fileh.root.table2

        if verbose:
            print "table1-->", table1.read()
            print "table2-->", table2.read()
            print "attrs table1-->", repr(table1.attrs)
            print "attrs table2-->", repr(table2.attrs)

        # Check that all the elements are equal
        r2 = r[self.start:self.stop:self.step]
        for nrow in range(r2.shape[0]):
            for colname in table1.colnames:
                assert allequal(r2[nrow][colname],
                                table2[nrow][colname])

        # Assert the number of rows in table
        if verbose:
            print "nrows in table2-->", table2.nrows
            print "and it should be-->", r2.shape[0]
        assert r2.shape[0] == table2.nrows

        # Close the file
        fileh.close()
        os.remove(file)

class CopyIndex1TestCase(CopyIndexTestCase):
    nrowsinbuf = 2
    close = 1
    start = 0
    stop = 7
    step = 1

class CopyIndex2TestCase(CopyIndexTestCase):
    nrowsinbuf = 2
    close = 0
    start = 0
    stop = -1
    step = 1

class CopyIndex3TestCase(CopyIndexTestCase):
    nrowsinbuf = 3
    close = 1
    start = 1
    stop = 7
    step = 1

class CopyIndex4TestCase(CopyIndexTestCase):
    nrowsinbuf = 4
    close = 0
    start = 0
    stop = 6
    step = 1

class CopyIndex5TestCase(CopyIndexTestCase):
    nrowsinbuf = 2
    close = 1
    start = 3
    stop = 7
    step = 1

class CopyIndex6TestCase(CopyIndexTestCase):
    nrowsinbuf = 2
    close = 0
    start = 3
    stop = 6
    step = 2

class CopyIndex7TestCase(CopyIndexTestCase):
    nrowsinbuf = 2
    close = 1
    start = 0
    stop = 7
    step = 10

class CopyIndex8TestCase(CopyIndexTestCase):
    nrowsinbuf = 2
    close = 0
    start = 6
    stop = 3
    step = 1

class CopyIndex9TestCase(CopyIndexTestCase):
    nrowsinbuf = 2
    close = 1
    start = 3
    stop = 4
    step = 1

class CopyIndex10TestCase(CopyIndexTestCase):
    nrowsinbuf = 1
    close = 0
    start = 3
    stop = 4
    step = 2

class CopyIndex11TestCase(CopyIndexTestCase):
    nrowsinbuf = 2
    close = 1
    start = -3
    stop = -1
    step = 2

class CopyIndex12TestCase(CopyIndexTestCase):
    nrowsinbuf = 3
    close = 0
    start = -1   # Should point to the last element
    stop = None  # None should mean the last element (including it)
    step = 1

class LargeRowSize(unittest.TestCase):

    def test00(self):
        "Checking saving a Table with a moderately large rowsize"
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a recarray
        r=records.array([[arange(100)]*2])

        # Save it in a table:
        fileh.createTable(fileh.root, 'largerow', r)

        # Read it again
        r2 = fileh.root.largerow.read()

        assert r.tostring() == r2.tostring()

        fileh.close()
        os.remove(file)

    def test01(self):
        "Checking saving a Table with an extremely large rowsize"
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create a recarray
        r=records.array([[arange(40000)]*4])   # 640 KB

        # Save it in a table:
#         try:
#             fileh.createTable(fileh.root, 'largerow', r)
#         except ValueError:
#             if verbose:
#                 (type, value, traceback) = sys.exc_info()
#               print "\nGreat!, the next ValueError was catched!"
#                 print value
#         else:
#             self.fail("expected a ValueError")
        # From PyTables 1.3 on, we allow row sizes equal or larger than 640 KB
        fileh.createTable(fileh.root, 'largerow', r)

        # Read it again
        r2 = fileh.root.largerow.read()
        assert r.tostring() == r2.tostring()

        fileh.close()
        os.remove(file)


class DefaultValues(unittest.TestCase):
    record = Record

    def test00(self):
        "Checking saving a Table with default values"
        file = tempfile.mktemp(".h5")
        #file = "/tmp/test.h5"
        fileh = openFile(file, "w")

        # Create a table
        table = fileh.createTable(fileh.root, 'table', self.record)

        table._v_nrowsinbuf=46   # minimum amount that reproduces a problem
        # Take a number of records a bit greater
        nrows = int(table._v_nrowsinbuf * 1.1)
        # Fill the table with nrows records
        for i in xrange(nrows):
            if i == 3 or i == 4:
                table.row['var2'] = 2
            # This injects the row values.
            table.row.append()

        # We need to flush the buffers in table in order to get an
        # accurate number of records on it.
        table.flush()

        # Create a recarray with the same default values
        r=records.array([["abcd", 1, 2, 3.1, 4.2, 5, "e", 1, 1j, 1+0j]]*nrows,
                          formats='a4,i4,i2,f8,f4,i2,a1,b1,c8,c16')

        # Assign the value exceptions
        r["f1"][3] = 2
        r["f1"][4] = 2

        # Read the table in another recarray
        #r2 = table.read()
        r2 = table[::]  # Equivalent to table.read()

        # This generates too much output. Activate only when
        # self._v_nrowsinbuf is very small (<10)
        if verbose:
            print "First 10 table values:"
            for row in table.iterrows(0, 10):
                print row
            print "The last 5 read recarray values:"
            #print r2[:5]
            print r2[-5:]
            print "Records should look like:"
            #print r[:5]
            print r[-5:]

        assert r.tostring() == r2.tostring()
        fileh.close()
        os.remove(file)

class OldRecordDefaultValues(DefaultValues):
    title = "OldRecordDefaultValues"
    record = OldRecord

class Record2(IsDescription):
    var1 = StringCol(itemsize=4, dflt="abcd")   # 4-character String
    var2 = col_from_kind('int', dflt=1)         # integer
    var3 = Int16Col(dflt=2)                     # short integer
    var4 = Float64Col(dflt=3.1)                 # double (double-precision)

class LengthTestCase(unittest.TestCase):
    record = Record
    nrows = 20

    def setUp(self):
        # Create an instance of an HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")
        self.rootgroup = self.fileh.root
        self.populateFile()

    def populateFile(self):
        group = self.rootgroup
        # Create a table
        table = self.fileh.createTable(self.fileh.root, 'table',
                                       self.record, title = "__length__ test")
        # Get the row object associated with the new table
        row = table.row

        # Fill the table
        for i in xrange(self.nrows):
            row.append()

        # Flush the buffer for this table
        table.flush()
        self.table = table

    def tearDown(self):
        if self.fileh.isopen:
            self.fileh.close()
        os.remove(self.file)
        cleanup(self)

    #----------------------------------------

    def test01_lengthrows(self):
        """Checking __length__ in Table"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_lengthrows..." % self.__class__.__name__

        # Number of rows
        len(self.table) == self.nrows

    def test02_lengthcols(self):
        """Checking __length__ in Cols"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_lengthcols..." % self.__class__.__name__

        # Number of columns
        if self.record is Record:
            len(self.table.cols) == 8
        elif self.record is Record2:
            len(self.table.cols) == 4

    def test03_lengthcol(self):
        """Checking __length__ in Column"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_lengthcol..." % self.__class__.__name__

        # Number of rows for all columns column
        for colname in self.table.colnames:
            len(getattr(self.table.cols, colname)) == self.nrows


class Length1TestCase(LengthTestCase):
    record = Record
    nrows = 20

class Length2TestCase(LengthTestCase):
    record = Record2
    nrows = 100


class WhereAppendTestCase(common.TempFileMixin, common.PyTablesTestCase):
    """Tests `Table.whereAppend()` method."""


    class SrcTblDesc(IsDescription):
        id = col_from_kind('int')
        v1 = col_from_kind('float')
        v2 = StringCol(itemsize=8)


    def setUp(self):
        super(WhereAppendTestCase, self).setUp()

        tbl = self.h5file.createTable('/', 'test', self.SrcTblDesc)
        row = tbl.row

        row['id'] = 1
        row['v1'] = 1.5
        row['v2'] = 'a' * 8
        row.append()

        row['id'] = 2
        row['v1'] = 2.5
        row['v2'] = 'b' * 6
        row.append()

        tbl.flush()


    def test00_same(self):
        """Query with same storage."""

        DstTblDesc = self.SrcTblDesc

        tbl1 = self.h5file.root.test
        tbl2 = self.h5file.createTable('/', 'test2', DstTblDesc)

        tbl1.whereAppend(tbl2, 'id > 1')

        # Rows resulting from the query are those in the new table.
        it2 = iter(tbl2)
        for r1 in tbl1.where('id > 1'):
            r2 = it2.next()
            assert (r1['id'] == r2['id'] and r1['v1'] == r2['v1']
                    and r1['v2'] == r2['v2'])

        # There are no more rows.
        self.assertRaises(StopIteration, it2.next)


    def test01_compatible(self):
        """Query with compatible storage."""

        class DstTblDesc(IsDescription):
            id = col_from_kind('float')  # float, not int
            v1 = col_from_kind('float')
            v2 = StringCol(itemsize=16)  # a longer column
            v3 = col_from_kind('float')  # extra column

        tbl1 = self.h5file.root.test
        tbl2 = self.h5file.createTable('/', 'test2', DstTblDesc)

        tbl1.whereAppend(tbl2, 'id > 1')

        # Rows resulting from the query are those in the new table.
        it2 = iter(tbl2)
        for r1 in tbl1.where('id > 1'):
            r2 = it2.next()
            assert (r1['id'] == r2['id'] and r1['v1'] == r2['v1']
                    and r1['v2'] == r2['v2'])

        # There are no more rows.
        self.assertRaises(StopIteration, it2.next)


    def test02_lessPrecise(self):
        """Query with less precise storage."""

        class DstTblDesc(IsDescription):
            id = col_from_kind('int')
            v1 = col_from_kind('int')  # int, not float
            v2 = StringCol(itemsize=8)

        tbl1 = self.h5file.root.test
        tbl2 = self.h5file.createTable('/', 'test2', DstTblDesc)

        tbl1.whereAppend(tbl2, 'id > 1')

        # Rows resulting from the query are those in the new table.
        it2 = iter(tbl2)
        for r1 in tbl1.where('id > 1'):
            r2 = it2.next()
            assert (r1['id'] == r2['id'] and int(r1['v1']) == r2['v1']
                    and r1['v2'] == r2['v2'])

        # There are no more rows.
        self.assertRaises(StopIteration, it2.next)


    def test03_incompatible(self):
        """Query with incompatible storage."""

        class DstTblDesc(IsDescription):
            id = StringCol(itemsize=4)  # string, not int
            v1 = col_from_kind('float')
            v2 = StringCol(itemsize=8)

        tbl1 = self.h5file.root.test
        tbl2 = self.h5file.createTable('/', 'test2', DstTblDesc)

        self.assertRaises(NotImplementedError,
                          tbl1.whereAppend, tbl2, 'v1 == "1"')


    def test04_noColumn(self):
        """Query with storage lacking columns."""

        class DstTblDesc(IsDescription):
            # no ``id`` field
            v1 = col_from_kind('float')
            v2 = StringCol(itemsize=8)

        tbl1 = self.h5file.root.test
        tbl2 = self.h5file.createTable('/', 'test2', DstTblDesc)

        self.assertRaises(KeyError, tbl1.whereAppend, tbl2, 'id > 1')


    def test05_otherFile(self):
        """Appending to a table in another file."""

        h5fname2 = tempfile.mktemp(suffix='.h5')
        h5file2 = openFile(h5fname2, 'w')

        try:
            tbl1 = self.h5file.root.test
            tbl2 = h5file2.createTable('/', 'test', self.SrcTblDesc)

            # RW to RW.
            tbl1.whereAppend(tbl2, 'id > 1')

            # RW to RO.
            h5file2.close()
            h5file2 = openFile(h5fname2, 'r')
            tbl2 = h5file2.root.test
            self.assertRaises(FileModeError,
                              tbl1.whereAppend, tbl2, 'id > 1')

            # RO to RO.
            self._reopen('r')
            tbl1 = self.h5file.root.test
            self.assertRaises(FileModeError,
                              tbl1.whereAppend, tbl2, 'id > 1')

            # RO to RW.
            h5file2.close()
            h5file2 = openFile(h5fname2, 'a')
            tbl2 = h5file2.root.test
            tbl1.whereAppend(tbl2, 'id > 1')
        finally:
            h5file2.close()
            os.remove(h5fname2)



class DerivedTableTestCase(unittest.TestCase):

    def setUp(self):
        self.file = tempfile.mktemp('.h5')
        self.fileh = openFile(self.file, 'w', title='DeriveFromTable')

        self.fileh.createTable('/', 'original', Record)

    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)

    def test00(self):
        """Deriving a table from the description of another."""

        tbl1 = self.fileh.root.original
        tbl2 = self.fileh.createTable('/', 'derived', tbl1.description)

        self.assertEqual(tbl1.description, tbl2.description)


class ChunkshapeTestCase(unittest.TestCase):

    def setUp(self):
        self.file = tempfile.mktemp('.h5')
        self.fileh = openFile(self.file, 'w', title='Chunkshape test')
        self.fileh.createTable('/', 'table', Record, chunkshape=13)

    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)

    def test00(self):
        """Test setting the chunkshape in a table (no reopen)."""

        tbl = self.fileh.root.table
        if verbose:
            print "chunkshape-->", tbl._v_chunkshape
        assert tbl._v_chunkshape == (13,)

    def test01(self):
        """Test setting the chunkshape in a table (reopen)."""

        self.fileh.close()
        self.fileh = openFile(self.file, 'r')
        tbl = self.fileh.root.table
        if verbose:
            print "chunkshape-->", tbl._v_chunkshape
        assert tbl._v_chunkshape == (13,)



#----------------------------------------------------------------------

def suite():
    theSuite = unittest.TestSuite()
    niter = 1
    #heavy = 1  # uncomment this only for testing purposes

    #theSuite.addTest(unittest.makeSuite(setItem1))
    #theSuite.addTest(unittest.makeSuite(WhereAppendTestCase))
    #theSuite.addTest(unittest.makeSuite(BasicWriteTestCase))
    #theSuite.addTest(unittest.makeSuite(LargeRowSize))
    for n in range(niter):
        theSuite.addTest(unittest.makeSuite(BasicWriteTestCase))
        theSuite.addTest(unittest.makeSuite(OldRecordBasicWriteTestCase))
        theSuite.addTest(unittest.makeSuite(DictWriteTestCase))
        theSuite.addTest(unittest.makeSuite(RecArrayOneWriteTestCase))
        theSuite.addTest(unittest.makeSuite(RecArrayTwoWriteTestCase))
        theSuite.addTest(unittest.makeSuite(RecArrayThreeWriteTestCase))
        theSuite.addTest(unittest.makeSuite(CompressLZOTablesTestCase))
        theSuite.addTest(unittest.makeSuite(CompressLZOShuffleTablesTestCase))
        theSuite.addTest(unittest.makeSuite(CompressZLIBTablesTestCase))
        theSuite.addTest(unittest.makeSuite(CompressZLIBShuffleTablesTestCase))
        theSuite.addTest(unittest.makeSuite(Fletcher32TablesTestCase))
        theSuite.addTest(unittest.makeSuite(AllFiltersTablesTestCase))
        theSuite.addTest(unittest.makeSuite(CompressTwoTablesTestCase))
        theSuite.addTest(unittest.makeSuite(IterRangeTestCase))
        theSuite.addTest(unittest.makeSuite(RecArrayRangeTestCase))
        theSuite.addTest(unittest.makeSuite(getColRangeTestCase))
        theSuite.addTest(unittest.makeSuite(getItemTestCase))
        theSuite.addTest(unittest.makeSuite(setItem1))
        theSuite.addTest(unittest.makeSuite(setItem2))
        theSuite.addTest(unittest.makeSuite(setItem3))
        theSuite.addTest(unittest.makeSuite(setItem4))
        theSuite.addTest(unittest.makeSuite(updateRow1))
        theSuite.addTest(unittest.makeSuite(updateRow2))
        theSuite.addTest(unittest.makeSuite(updateRow3))
        theSuite.addTest(unittest.makeSuite(updateRow4))
        theSuite.addTest(unittest.makeSuite(RecArrayIO1))
        theSuite.addTest(unittest.makeSuite(RecArrayIO2))
        theSuite.addTest(unittest.makeSuite(OpenCopyTestCase))
        theSuite.addTest(unittest.makeSuite(CloseCopyTestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex1TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex2TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex3TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex4TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex5TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex6TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex7TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex8TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex9TestCase))
        theSuite.addTest(unittest.makeSuite(DefaultValues))
        theSuite.addTest(unittest.makeSuite(OldRecordDefaultValues))
        theSuite.addTest(unittest.makeSuite(Length1TestCase))
        theSuite.addTest(unittest.makeSuite(Length2TestCase))
        theSuite.addTest(unittest.makeSuite(WhereAppendTestCase))
        theSuite.addTest(unittest.makeSuite(DerivedTableTestCase))
        theSuite.addTest(unittest.makeSuite(ChunkshapeTestCase))

    if heavy:
        theSuite.addTest(unittest.makeSuite(CompressBZIP2TablesTestCase))
        theSuite.addTest(unittest.makeSuite(CompressBZIP2ShuffleTablesTestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex10TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex11TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex12TestCase))
        theSuite.addTest(unittest.makeSuite(LargeRowSize))
        theSuite.addTest(unittest.makeSuite(BigTablesTestCase))

    return theSuite


if __name__ == '__main__':
    unittest.main( defaultTest='suite' )
