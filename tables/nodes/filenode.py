# -*- coding: utf-8 -*-

########################################################################
#
# License: BSD
# Created: October 2, 2004
# Author:  Ivan Vilata i Balaguer - reverse:net.selidor@ivan
#
# $Id$
#
########################################################################

"""A file interface to nodes for PyTables databases.

The FileNode module provides a file interface for using inside of
PyTables database files.  Use the new_node() function to create a brand
new file node which can be read and written as any ordinary Python
file.  Use the open_node() function to open an existing (i.e. created
with new_node()) node for read-only or read-write access.  Read acces
is always available.  Write access (enabled on new files and files
opened with mode 'a+') only allows appending data to a file node.

Currently only binary I/O is supported.

See :ref:`filenode_usersguide` for instructions on use.

.. versionchanged:: 3.0

    In version 3.0 the module as been copletely rwritten do be fully
    comliant with the :mod:`io` module interfeces.

"""

import io
import warnings

import numpy as np

import tables
from tables._past import previous_api


NodeType = 'file'
"""Value for NODE_TYPE node system attribute."""

NodeTypeVersions = [1, 2]
"""Supported values for NODE_TYPE_VERSION node system attribute."""


class RawPyTablesIO(io.RawIOBase):
    """Base class for raw binary I/O on HDF5 files using PyTables."""

    # A lambda to turn a size into a shape, for each version.
    _size_to_shape = [
        None,
        lambda l: (l, 1),
        lambda l: (l, ),
    ]

    def __init__(self, node, mode=None):
        super(RawPyTablesIO, self).__init__()

        self._check_node(node)
        self._check_attributes(node)

        if mode is None:
            mode = node._v_file.mode
        else:
            self._check_mode(mode)
            self._cross_check_mode(mode, node._v_file.mode)

        self._node = node
        self._mode = mode
        self._pos = 0
        self._version = int(node.attrs.NODE_TYPE_VERSION)
        self._vshape = self._size_to_shape[self._version]
        # @TODO: check
        #_vtype = tables.UInt8Atom().dtype.base.type
        self._vtype = node.atom.dtype.base.type

        # @TODO: remove
        assert(self._vtype == np.uint8)

    # read only attribute
    @property
    def mode(self):
        return self._mode

    #def tell(self) -> int:
    def tell(self):
        """Return current stream position."""

        self._checkClosed()
        return self._pos

    #def seek(self, pos: int, whence: int = 0) -> int:
    def seek(self, pos, whence=0):
        """Change stream position.

        Change the stream position to byte offset offset. offset is
        interpreted relative to the position indicated by whence.  Values
        for whence are:

        * 0 -- start of stream (the default); offset should be zero or positive
        * 1 -- current stream position; offset may be negative
        * 2 -- end of stream; offset is usually negative

        Return the new absolute position.

        """

        self._checkClosed()
        try:
            pos = pos.__index__()
        #except AttributeError as err:
            #raise TypeError("an integer is required") from err
        except AttributeError:
            raise TypeError("an integer is required")
        if whence == 0:
            if pos < 0:
                raise ValueError("negative seek position %r" % (pos,))
            self._pos = pos
        elif whence == 1:
            self._pos = max(0, self._pos + pos)
        elif whence == 2:
            self._pos = max(0, self._node.nrows + pos)
        else:
            raise ValueError("invalid whence value")
        return self._pos

    #def seekable(self) -> bool:
    def seekable(self):
        """Return whether object supports random access.

        If False, seek(), tell() and truncate() will raise IOError.
        This method may need to do a test seek().

        """

        return True

    #def fileno(self) -> int:
    def fileno(self):
        """Returns underlying file descriptor if one exists.

        An IOError is raised if the IO object does not use a file descriptor.

        """

        self._checkClosed()
        self._node._v_file.fileno()

    #def close(self) -> None:
    def close(self):
        """Flush and close the IO object.

        This method has no effect if the file is already closed.

        """

        if not self.closed:
            if getattr(self._node, '_v_file', None) is None:
                warnings.warn("host PyTables file is already closed!")

        try:
            super(RawPyTablesIO, self).close()
        finally:
            # Release node object to allow closing the file.
            self._node = None

    def flush(self):
        """Flushes the file node.

        See file.flush.__doc__ for more information.

        """

        self._checkClosed()
        self._node.flush()

    #def truncate(self, pos: int = None) -> int:
    def truncate(self, pos=None):
        """Truncate file to size bytes.

        Size defaults to the current IO position as reported by tell().
        Return the new size.

        Currently, this method only makes sense to grow the file node,
        since data can not be rewritten nor deleted.

        """

        self._checkClosed()
        self._checkWritable()

        if pos is None:
            pos = self._pos
        elif pos < 0:
            raise ValueError("negative truncate position %r" % (pos,))

        if pos < self._node.nrows:
            raise IOError("truncating is only allowed for growing a file")
        self._append_zeros(pos - self._node.nrows)

        return self.seek(pos)

    #def readable(self) -> bool:
    def readable(self):
        """Return whether object was opened for reading.

        If False, read() will raise IOError.

        """

        mode = self._mode
        return 'r' in mode or '+' in mode

    #def writable(self) -> bool:
    def writable(self):
        """Return whether object was opened for writing.

        If False, write() and truncate() will raise IOError.

        """

        mode = self._mode
        return 'w' in mode or 'a' in mode or '+' in mode

    #def readinto(self, b: bytearray) -> int:
    def readinto(self, b):
        """Read up to len(b) bytes into b.

        Returns number of bytes read (0 for EOF), or None if the object
        is set not to block as has no data to read.

        """

        self._checkClosed()
        self._checkReadable()

        if self._pos >= self._node.nrows:
            return 0

        n = len(b)
        start = self._pos
        stop = self._pos + n

        # XXX optimized path
        #if stop <= self._node.nrows and isinstance(b, np.ndarray):
        #    self._node.read(start, stop, out=b)
        #    self._pos += n
        #    return n

        if stop > self._node.nrows:
            stop = self._node.nrows
            n = stop - start

        # XXX This ought to work with anything that supports the buffer API
        b[:n] = self._node.read(start, stop).tostring()

        self._pos += n

        return n

    #def readline(self, limit: int = -1) -> bytes:
    def readline(self, limit=-1):
        """Read and return a line from the stream.

        If limit is specified, at most limit bytes will be read.

        The line terminator is always b'\n' for binary files; for text
        files, the newlines argument to open can be used to select the line
        terminator(s) recognized.

        """

        self._checkClosed()
        self._checkReadable()

        # @TODO: check
        #chunksize = self._line_chunksize
        chunksize = self._node.chunkshape[0]

        # @TODO: check
        lsep = b'\n'
        lseplen = len(lsep)

        # Set the remaining bytes to read to the specified size.
        remsize = limit

        partial = []
        finished = False

        while not finished:
            # Read a string limited by the remaining number of bytes.
            if limit <= 0:
                ibuff = self.read(chunksize)
            else:
                ibuff = self.read(min(remsize, chunksize))
            ibufflen = len(ibuff)
            remsize -= ibufflen

            if ibufflen >= lseplen:
                # Separator fits, look for EOL string.
                eolindex = ibuff.find(lsep)
            elif ibufflen == 0:
                # EOF was immediately reached.
                finished = True
                continue
            else:  # ibufflen < lseplen
                # EOF was hit and separator does not fit. ;)
                partial.append(ibuff)
                finished = True
                continue

            if eolindex >= 0:
                # Found an EOL. If there are trailing characters,
                # cut the input buffer and seek back;
                # else add the whole input buffer.
                trailing = ibufflen - lseplen - eolindex  # Bytes beyond EOL.
                if trailing > 0:
                    obuff = ibuff[:-trailing]
                    self.seek(-trailing, 1)
                    remsize += trailing
                else:
                    obuff = ibuff
                finished = True
            elif lseplen > 1 and (limit <= 0 or remsize > 0):
                # Seek back a little since the end of the read string
                # may have fallen in the middle of the line separator.
                obuff = ibuff[:-lseplen + 1]
                self.seek(-lseplen + 1, 1)
                remsize += lseplen - 1
            else:  # eolindex<0 and (lseplen<=1 or (limit>0 and remsize<=0))
                # Did not find an EOL, add the whole input buffer.
                obuff = ibuff

            # Append (maybe cut) buffer.
            partial.append(obuff)

            # If a limit has been specified and the remaining count
            # reaches zero, the reading is finished.
            if limit > 0 and remsize <= 0:
                finished = True

        return b''.join(partial)

    #def write(self, b: bytes) -> int:
    def write(self, b):
        """Write the given buffer to the IO stream.

        Returns the number of bytes written, which may be less than len(b).

        """

        self._checkClosed()
        self._checkWritable()

        if isinstance(b, unicode):
            raise TypeError("can't write str to binary stream")

        n = len(b)
        if n == 0:
            return 0

        pos = self._pos

        # Is the pointer beyond the real end of data?
        end2off = pos - self._node.nrows
        if end2off > 0:
            # Zero-fill the gap between the end of data and the pointer.
            self._append_zeros(end2off)

        # Append data.
        self._node.append(
            np.ndarray(buffer=b, dtype=self._vtype, shape=self._vshape(n)))

        self._pos += n

        return n

    def _checkClosed(self):
        """Checks if file node is open.

        Checks whether the file node is open or has been closed.
        In the second case, a ValueError is raised.
        If the host PyTables has been closed, ValueError is also raised.

        """

        super(RawPyTablesIO, self)._checkClosed()
        if getattr(self._node, '_v_file', None) is None:
            raise ValueError("host PyTables file is already closed!")

    def _check_node(self, node):
        if not isinstance(node, tables.EArray):
            raise TypeError('the "node" parameter should be a tables.EArray')
        if not isinstance(node.atom, tables.UInt8Atom):
            raise TypeError('only nodes with atom "UInt8Atom" are allowed')

    def _check_mode(self, mode):
        if not isinstance(mode, str):
            raise TypeError("invalid mode: %r" % mode)

        modes = set(mode)
        if modes - set("arwb+tU") or len(mode) > len(modes):
            raise ValueError("invalid mode: %r" % mode)

        reading = "r" in modes
        writing = "w" in modes
        appending = "a" in modes
        #updating = "+" in modes
        text = "t" in modes
        binary = "b" in modes

        if "U" in modes:
            if writing or appending:
                raise ValueError("can't use U and writing mode at once")
            reading = True

        if text and binary:
            raise ValueError("can't have text and binary mode at once")

        if reading + writing + appending > 1:
            raise ValueError("can't have read/write/append mode at once")

        if not (reading or writing or appending):
            raise ValueError("must have exactly one of read/write/append mode")

    def _cross_check_mode(self, mode, h5filemode):

        readable = bool('r' in mode or '+' in mode)
        writable = bool('w' in mode or 'a' in mode or '+' in mode)

        h5readable = bool('r' in h5filemode or '+' in h5filemode)
        h5writable = bool('w' in h5filemode or 'a' in h5filemode or
                          '+' in h5filemode)

        # @TPDP: check
        #~ if readable and not h5readable:
            #~ raise ValueError("RawPyTablesIO can't be open in read mode if "
                             #~ "the underlying hdf5 file is not readable")

        if writable and not h5writable:
            raise ValueError("RawPyTablesIO can't be open in write mode if "
                             "the underlying hdf5 file is not writable")

    def _check_attributes(self, node):
        """Checks file node-specific attributes.

        Checks for the presence and validity
        of the system attributes 'NODE_TYPE' and 'NODE_TYPE_VERSION'
        in the specified PyTables node (leaf).
        ValueError is raised if an attribute is missing or incorrect.

        """

        attrs = node.attrs
        ltype = getattr(attrs, 'NODE_TYPE', None)
        ltypever = getattr(attrs, 'NODE_TYPE_VERSION', None)

        if ltype != NodeType:
            raise ValueError("invalid type of node object: %s" % (ltype,))
        if ltypever not in NodeTypeVersions:
            raise ValueError(
                "unsupported type version of node object: %s" % (ltypever,))

    _checkAttributes = previous_api(_check_attributes)

    def _append_zeros(self, size):
        """_append_zeros(size) -> None.  Appends a string of zeros.

        Appends a string of 'size' zeros to the array,
        without moving the file pointer.

        """

        # Appending an empty array would raise an error.
        if size == 0:
            return

        # XXX This may be redone to avoid a potentially large in-memory array.
        self._node.append(
            np.zeros(dtype=self._vtype, shape=self._vshape(size)))


class FileNode(RawPyTablesIO):
    """This is the ancestor of ROFileNode and RAFileNode (see below).

    Instances of these classes are returned when new_node() or
    open_node() are called. It represents a new file node associated
    with a PyTables node, providing a standard Python file interface
    to it.

    The implementation of the reading/writing methods needed to implement a
    file-like object over a PyTables node is provided by the RawPyTablesIO
    base class.

    The attribute set of the node becomes available via the attrs property.
    You can add attributes there, but try to avoid attribute names in all
    caps or starting with '_', since they may clash with internal attributes.

    The node used as storage is also made available via the read-only
    attribute node.
    Please do not tamper with this object if it's avoidable, since you
    may break the operation of the file node object.

    Version 1 implements the file storage as a UInt8 uni-dimensional EArray.
    Version 2 uses an UInt8 N vector EArray.

    .. versionchanged:: 3.0

        The line_separator property is no more available.
        The only line separator used for binary I/O is '\n'.

    """

    # The attribute set property methods.
    def _get_attrs(self):
        """Returns the attribute set of the file node."""

        #sefl._checkClosed()
        return self._node.attrs

    getAttrs = previous_api(_get_attrs)

    def _set_attrs(self, value):
        """set_attrs(string) -> None.  Raises ValueError."""

        raise ValueError("changing the whole attribute set is not allowed")

    setAttrs = previous_api(_set_attrs)

    def _del_attrs(self):
        """del_attrs() -> None.  Raises ValueError."""

        raise ValueError("deleting the whole attribute set is not allowed")

    delAttrs = previous_api(_del_attrs)

    # The attribute set property.
    attrs = property(
        _get_attrs, _set_attrs, _del_attrs,
        "A property pointing to the attribute set of the file node.")

    @property
    def node(self):
        return self._node

    # @TODO: check
    #def __del__(self):
    #    if self.node is not None:
    #        self.close()

    def _set_attributes(self, node):
        """_set_attributes(node) -> None.  Adds file node-specific attributes.

        Sets the system attributes 'NODE_TYPE' and 'NODE_TYPE_VERSION'
        in the specified PyTables node (leaf).

        """

        attrs = node.attrs
        # System attributes are now writable.  ivb(2004-12-30)
        # attrs._g_setattr('NODE_TYPE', NodeType)
        # attrs._g_setattr('NODE_TYPE_VERSION', NodeTypeVersions[-1])
        attrs.NODE_TYPE = NodeType
        attrs.NODE_TYPE_VERSION = NodeTypeVersions[-1]

    _setAttributes = previous_api(_set_attributes)

    # --- compatibility ------------------------------------------------------
    @property
    def offset(self):
        warnings.warn('deprecated API:please use "tell" instead', stacklevel=1)
        return self._pas

    @offset.setter
    def offset(self, value):
        warnings.warn('deprecated API: please use "seek" instaed', stacklevel=1)
        self._pos = value



class ROFileNode(FileNode):
    """Creates a new read-only file node.

    Creates a new read-only file node associated with the specified
    PyTables node, providing a standard Python file interface to it.
    The node has to have been created on a previous occasion
    using the new_node() function.

    This constructor is not intended to be used directly.
    Use the open_node() function in read-only mode ('r') instead.

    """

    # Since FileNode provides all methods for read-only access,
    # only the constructor method and failing writing methods are needed.
    def __init__(self, node):
        super(ROFileNode, self).__init__(node, 'r')

    # @TODO: check
    #def __del__(self):
    #    super(ROFileNode, self).__del__()


class RAFileNode(FileNode):
    """Creates a new read-write file node.

    The first syntax opens the specified PyTables node, while the
    second one creates a new node in the specified PyTables file.
    In the second case, additional named arguments 'where' and 'name'
    must be passed to specify where the file node is to be created.
    Other named arguments such as 'title' and 'filters' may also be
    passed.  The special named argument 'expectedsize', indicating an
    estimate of the file size in bytes, may also be passed.

    Write access means reading as well as appending data is allowed.

    This constructor is not intended to be used directly.
    Use the new_node() or open_node() functions instead.

    """

    # The atom representing a byte in the array, for each version.
    _byte_shape = [
        None,
        (0, 1),
        (0,),
    ]

    __allowed_init_kwargs = [
        'where', 'name', 'title', 'filters', 'expectedsize']

    def __init__(self, node, h5file, **kwargs):
        if node is not None:
            # Open an existing node and get its version.
            self._check_attributes(node)
            self._version = node.attrs.NODE_TYPE_VERSION
        elif h5file is not None:
            # Check for allowed keyword arguments,
            # to avoid unwanted arguments falling through to array constructor.
            for kwarg in kwargs:
                if kwarg not in self.__allowed_init_kwargs:
                    raise TypeError(
                        "%s keyword argument is not allowed" % repr(kwarg))

            # Turn 'expectedsize' into 'expectedrows'.
            if 'expectedsize' in kwargs:
                # These match since one byte is stored per row.
                expectedrows = kwargs['expectedsize']
                kwargs = kwargs.copy()
                del kwargs['expectedsize']
                kwargs['expectedrows'] = expectedrows

            # Create a new array in the specified PyTables file.
            self._version = NodeTypeVersions[-1]
            shape = self._byte_shape[self._version]
            node = h5file.create_earray(
                atom=tables.UInt8Atom(), shape=shape, **kwargs)

            # Set the node attributes, else remove the array itself.
            try:
                self._set_attributes(node)
            except RuntimeError:
                h5file.remove_node(kwargs['where'], kwargs['name'])
                raise

        super(RAFileNode, self).__init__(node, 'a+')

    # @TODO:check
    #def __del__(self):
    #    super(RAFileNode, self).__del__()


def new_node(h5file, **kwargs):
    """Creates a new file node object in the specified PyTables file object.

    Additional named arguments where and name must be passed to specify where
    the file node is to be created. Other named arguments such as title and
    filters may also be passed.

    The special named argument expectedsize, indicating an estimate of the file
    size in bytes, may also be passed. It returns the file node object.

    """

    return RAFileNode(None, h5file, **kwargs)


newNode = previous_api(new_node)


def open_node(node, mode='r'):
    """Opens an existing file node.

    Returns a file node object from the existing specified PyTables node.
    If mode is not specified or it is 'r', the file can only be read,
    and the pointer is positioned at the beginning of the file.
    If mode is 'a+', the file can be read and appended, and the pointer
    is positioned at the end of the file.

    """

    if mode == 'r':
        return ROFileNode(node)
    elif mode == 'a+':
        return RAFileNode(node, None)
    else:
        raise IOError("invalid mode: %s" % (mode,))


openNode = previous_api(open_node)


## Local Variables:
## mode: python
## py-indent-offset: 4
## tab-width: 4
## End:
