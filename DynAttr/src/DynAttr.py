#!/bin/env python
#    "$Name:  $";
#    "$Header:  $";
#=============================================================================
#
# file :        DynAttr.py
#
# description : Python source for the DynAttr dynamic attribute server
#
# project :     TANGO Device Server

import PyTango
import sys
import numpy as np


def fromPyTango2NumpyType(pytango_type):
    """ Return the numpy type based on the PyTango type

    usage:
        attr=PyTango.AttributeProxy('')
        sample=attr.read()
        fromPyTango2NumpyType(sample.type)
    """
    data_type = np.int32
    if(pytango_type == PyTango.CmdArgType.DevBoolean):
        data_type = np.bool
    elif(pytango_type == PyTango.CmdArgType.DevUChar):
        data_type = np.uint8
    elif(pytango_type == PyTango.CmdArgType.DevUShort):
        data_type = np.uint16
    elif(pytango_type == PyTango.CmdArgType.DevULong):
        data_type = np.uint32
    elif(pytango_type == PyTango.CmdArgType.DevULong64):
        data_type = np.uint64
    elif(pytango_type == PyTango.CmdArgType.DevShort):
        data_type = np.int16
    elif(pytango_type == PyTango.CmdArgType.DevLong):
        data_type = np.int32
    elif(pytango_type == PyTango.CmdArgType.DevLong64):
        data_type = np.int64
    elif(pytango_type == PyTango.CmdArgType.DevFloat):
        data_type = np.float32
    elif(pytango_type == PyTango.CmdArgType.DevDouble):
        data_type = np.float64
        # FIXME version 1.2.1 does not support float64 ( ? but 1.2.0 does...)
    return data_type


def fromNumpyType2PyTango(numpy_type):
    """ Return the PyTango type based on numpy type

    usage:
        attr = numpy.ones((2,2))
        fromNumpyType2PyTango(attr.type)
    """
    data_type = PyTango.ArgType.DevDouble
    if numpy_type == np.bool:
        data_type = PyTango.ArgType.DevBoolean
    elif numpy_type == np.uint8:
        data_type = PyTango.ArgType.DevUChar
    elif numpy_type == np.uint16:
        data_type = PyTango.ArgType.DevUShort
    elif numpy_type == np.uint32:
        data_type = PyTango.ArgType.DevULong
    elif numpy_type == np.uint64:
        data_type = PyTango.ArgType.DevULong64
    elif numpy_type == np.int16:
        data_type = PyTango.ArgType.DevShort
    elif numpy_type == np.int32:
        data_type = PyTango.ArgType.DevLong
    elif numpy_type == np.int64:
        data_type = PyTango.ArgType.DevLong64
    elif numpy_type == np.float32:
        data_type = PyTango.ArgType.DevFloat
    elif numpy_type == np.float64:
        data_type = PyTango.ArgType.DevDouble
    return data_type


def fromNp2Tg(numpy_type):
    data_type = "DOUBLE"
    if numpy_type == np.bool:
        data_type = "BOOL"
    if numpy_type == np.uint8:
        data_type = "UCHAR"
    elif numpy_type == np.uint16:
        data_type = "USHORT"
    elif numpy_type == np.uint32:
        data_type = "ULONG"
    elif numpy_type == np.uint64:
        data_type = "ULONG64"
    elif numpy_type == np.int16:
        data_type = "SHORT"
    elif numpy_type == np.int32:
        data_type = "LONG"
    elif numpy_type == np.int64:
        data_type = "LONG64"
    elif numpy_type == np.float32:
        data_type = "FLOAT"
    elif numpy_type == np.float64:
        data_type = "DOUBLE"
    return data_type


def fromTg2Tango(ttype):
    ttype = ttype.upper()
    if ttype == "BOOL":
        data_type = PyTango.ArgType.DevBoolean
    elif ttype == "UCHAR":
        data_type = PyTango.ArgType.DevUChar
    elif ttype == "USHORT":
        data_type = PyTango.ArgType.DevUShort
    elif ttype == "ULONG":
        data_type = PyTango.ArgType.DevULong
    elif ttype == "ULONG64":
        data_type = PyTango.ArgType.DevULong64
    elif ttype == "SHORT":
        data_type = PyTango.ArgType.DevShort
    elif ttype == "LONG":
        data_type = PyTango.ArgType.DevLong
    elif ttype == "LONG64":
        data_type = PyTango.ArgType.DevLong64
    elif ttype == "FLOAT":
        data_type = PyTango.ArgType.DevFloat
    elif ttype == "DOUBLE":
        data_type = PyTango.ArgType.DevDouble
    else:
        raise
    return data_type


def processInputStringArray(inp_array):
    """ Process an input array and return the values for the creation of
    PyTango Attribute.

    The input array must have:
        name = The name of the new PyTango Attribute.
        data_type = string DOUBLE,SHORT or LONG strings
        optionals:
        [X size] = number of data for 1 and 2 d arrays
        [Y size] = number of data for 2 d arrays

    it will return:
        (name,PyTangoType,[int,[int]])
    """
    #FIXME: process bad input
    #print "processing inp",inp_array
    name = inp_array[0].lower()
    try:
        typ = fromTg2Tango(inp_array[1].upper())
    except:
        PyTango.Except.throw_exception("BadInput",
        "BadInput: (name,data_type,[xsize,[ysize]]), received: " +
        str(inp_array) + " name = " + str(name) + " type = " + str(inp_array[1].upper()),
        "processInputStringArray")

    if (len(inp_array) > 3):
        y_size = int(inp_array[3])
        x_size = int(inp_array[2])
        return (name, typ, x_size, y_size)
    elif (len(inp_array) > 2):
        x_size = int(inp_array[2])
        return (name, typ, x_size)
    else:
        return (name, typ)


class CaseLessDict(dict):
    def __init__(self):
        super(CaseLessDict, self).__init__()

    def __setitem__(self, key, v):
        super(CaseLessDict, self).__setitem__(key.lower(), v)

    def __getitem__(self, key):
        return super(CaseLessDict, self).__getitem__(key.lower())


#==================================================================
#   DynAttr Class Description:
#
#         Creation and management of dynamic attributes that will be used for
#         pre and post-processing of Fermi data.
#
#==================================================================
#     Device States Description:
#
#   DevState.ON :     Working
#   DevState.FAULT :
#==================================================================
class DynAttr(PyTango.Device_4Impl):

#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    def __init__(self, cl, name):
        PyTango.Device_4Impl.__init__(self, cl, name)
        DynAttr.init_device(self)

#------------------------------------------------------------------
#    Device destructor
#------------------------------------------------------------------
    def delete_device(self):
        return

#------------------------------------------------------------------
#    Device initialization
#------------------------------------------------------------------
    def init_device(self):
        self.set_state(PyTango.DevState.ON)
        self.get_device_properties(self.get_device_class())
        self.myattrs = CaseLessDict()
        self.createDefaultAttributes(self.Default_Attributes)

#------------------------------------------------------------------
#    Always excuted hook method
#------------------------------------------------------------------
    def always_executed_hook(self):
        pass

#==================================================================
#
#    DynAttr read/write attribute methods
#
#==================================================================
#------------------------------------------------------------------
#    Read Attribute Hardware
#------------------------------------------------------------------
    def read_attr_hardware(self, data):
        pass

#------------------------------------------------------------------
#    Read Scalar attribute
#------------------------------------------------------------------
    def read_Scalar(self, attr):
        data = self.myattrs[attr.get_name()]
        attr.set_value(data)

#------------------------------------------------------------------
#    Write Scalar attribute
#------------------------------------------------------------------
    def write_Scalar(self, attr):
        self.myattrs[attr.get_name()] = attr.get_write_value(PyTango.ExtractAs.Numpy)

#------------------------------------------------------------------
#    Read Spectrum attribute
#------------------------------------------------------------------
    def read_Spectrum(self, attr):
        data = self.myattrs[attr.get_name()]
        attr.set_value(data, len(data))

#------------------------------------------------------------------
#    Write Spectrum attribute
#------------------------------------------------------------------
    def write_Spectrum(self, attr):
        self.myattrs[attr.get_name()] = attr.get_write_value(PyTango.ExtractAs.Numpy)

#------------------------------------------------------------------
#    Read Image attribute
#------------------------------------------------------------------
    def read_Image(self, attr):
        data = self.myattrs[attr.get_name()]  # [:]
        #assert isinstance(data, np.ndarray)
        #find_zero = np.where(data == 0)
        #data[find_zero] = data.max()
        attr.set_value(data)

#------------------------------------------------------------------
#    Write Image attribute
#------------------------------------------------------------------
    def write_Image(self, attr):
        self.myattrs[attr.get_name()] = attr.get_write_value(PyTango.ExtractAs.Numpy)

#==================================================================
#
#    DynAttr command methods
#
#==================================================================

#------------------------------------------------------------------
#    NewScalar command:
#
#    Description:
#    argin:  DevVarStringArray
#              Name - name of the new scalar attribute
#              Type - the type of the attribute
#------------------------------------------------------------------
    def NewScalar(self, argin):
        # Process input parameters
        (name, typ) = processInputStringArray(argin)

        # Check if attribute exist
        if name in self.myattrs:
            PyTango.Except.throw_exception("Exist",
                                           "Attribute " + name + " already defined",
                                           "NewAttribute")

        # Create new attribute
        attr = PyTango.Attr(name,
                            typ,
                            PyTango.AttrWriteType.READ_WRITE)

        # Add attribute to list
        self.add_attribute(attr, self.read_Scalar, self.write_Scalar, None)
        self.myattrs[name] = 0

#------------------------------------------------------------------
#    NewSpectrum command:
#
#    Description:
#    argin:  DevVarStringArray
#              Name - name of the new scalar attribute
#              Type - the type of the attribute
#              MaxDim - maximum length of the spectrum
#------------------------------------------------------------------
    def NewSpectrum(self, argin):
        # Process input parameters
        (name, typ, siz) = processInputStringArray(argin)

        # Check if attribute exist
        if name in self.myattrs:
            PyTango.Except.throw_exception("Exist",
                                           "Attribute " + name + " already defined",
                                           "NewAttribute")
        # Create new attribute
        attr = PyTango.SpectrumAttr(name,
                                    typ,
                                    PyTango.AttrWriteType.READ_WRITE,
                                    siz)

        # Add attribute to list
        self.add_attribute(attr, self.read_Spectrum, self.write_Spectrum, None)
        self.myattrs[name] = np.zeros(siz, fromPyTango2NumpyType(typ))

#------------------------------------------------------------------
#    NewImage command:
#
#    Description:
#    argin:  DevVarStringArray
#              Name - name of the new scalar attribute
#              Type - the type of the attribute
#              MaxDimX - maximum X dimension of the image
#              MaxDimY - maximum Y dimension of the image
#------------------------------------------------------------------
    def NewImage(self, argin):
        # Process input parameters
        (name, typ, sizx, sizy) = processInputStringArray(argin)

        # Check if attribute exist
        if name in self.myattrs:
            PyTango.Except.throw_exception("Exist",
                                           "Attribute " + name + " already defined",
                                           "NewAttribute")

        # Create new attribute
        attr = PyTango.ImageAttr(name,
                                 typ,
                                 PyTango.AttrWriteType.READ_WRITE,
                                 sizx,
                                 sizy)

        # Add attribute to list
        self.add_attribute(attr, self.read_Image, self.write_Image, None)
        self.myattrs[name] = np.zeros((sizy, sizx), fromPyTango2NumpyType(typ))

#------------------------------------------------------------------
#    ClearAll command:
#
#    Description:
#    argin:  DevVarStringArray
#              Name - name of the new scalar attribute
#              Type - the type of the attribute
#              MaxDimX - maximum X dimension of the image
#              MaxDimY - maximum Y dimension of the image
#------------------------------------------------------------------
    def ClearAll(self):
        # Cycle over attributes
        for k in self.myattrs.keys():
            try:
                self.remove_attribute(k.lower())
            except:
                pass
        self.myattrs = CaseLessDict()

#------------------------------------------------------------------
#    DeleteAttribute command:
#
#    Description:
#    argin:  DevVarStringArray
#              Name - name of the new scalar attribute
#              Type - the type of the attribute
#              MaxDimX - maximum X dimension of the image
#              MaxDimY - maximum Y dimension of the image
#------------------------------------------------------------------
    def DeleteAttribute(self, argin):
        name = str(argin)
        if name in self.myattrs:
            self.remove_attribute(name.lower())
            del self.myattrs[name]

#------------------------------------------------------------------
#    createDefaultAttributes method
#------------------------------------------------------------------
    def createDefaultAttributes(self, attribute_list):
        try:
            for newattr in attribute_list:
                tokens = newattr.split(",")
                attr_type = tokens.pop(0)
                if (attr_type == "NewScalar"):
                    self.NewScalar(tokens)
                elif (attr_type == "NewSpectrum"):
                    self.NewSpectrum(tokens)
                elif (attr_type == "NewImage"):
                    self.NewImage(tokens)
        except:
            pass


#==================================================================
#
#    DynAttrClass class definition
#
#==================================================================
class DynAttrClass(PyTango.DeviceClass):

    #    Class Properties
    class_property_list = {
        }

    #    Device Properties
    device_property_list = {
        'Default_Attributes':
            [PyTango.DevVarStringArray,
            "Default attributes that will be created at startup",
            [True]],
        }

    #    Command definitions
    cmd_list = {
        'NewScalar':
            [
                [PyTango.DevVarStringArray,
                 "Usage NewScalar(name, type)\n" \
                 "  - name: name of the new scalar attribute\n" \
                 "  - type: type of the new attribute.\n" \
                 "    May be BOOL, UCHAR, (U)SHORT, (U)LONG, (U)LONG64,\n" \
                 "    FLOAT, DOUBLE.\n"],
                [PyTango.DevVoid, "No value returned.\n"]
            ],
        'NewSpectrum':
            [
                [PyTango.DevVarStringArray,
                 "Usage NewSpectrum(name, type, maxsize)\n" \
                 "  - name: name of the new spectrum attribute\n" \
                 "  - type: type of the new attribute.\n" \
                 "    May be BOOL, UCHAR, (U)SHORT, (U)LONG, (U)LONG64,\n" \
                 "    FLOAT, DOUBLE.\n" \
                 "  - maxsize: the maximum length of the spectrum.\n"],
                [PyTango.DevVoid, "No value returned.\n"]
            ],
        'NewImage':
            [
                [PyTango.DevVarStringArray,
                 "Usage NewImage(name, type, max_x, max_y)\n" \
                 "  - name: name of the new image attribute\n" \
                 "  - type: type of the new attribute.\n" \
                 "    May be BOOL, UCHAR, (U)SHORT, (U)LONG, (U)LONG64,\n" \
                 "    FLOAT, DOUBLE.\n" \
                 "  - max_x: the maximum X dimension of the image.\n" \
                 "  - max_y: the maximum Y dimension of the image.\n"],
                [PyTango.DevVoid, ""]
            ],
        'ClearAll':
            [[PyTango.DevVoid, "Usage: ClearAll()\n"],
             [PyTango.DevVoid, "No value returned.\n"]],
        'DeleteAttribute':
            [[PyTango.DevString, "Usage: DeleteAttribute(name)\n  - name: the name of the attribute to remove.\n"],
             [PyTango.DevVoid, "No value returned.\n"]],
        }

    #    Attribute definitions
    attr_list = {
        }

#------------------------------------------------------------------
#    DynAttrClass Constructor
#------------------------------------------------------------------
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name)


class DynHDFAttr(DynAttr):
    #------------------------------------------------------------------
    #    Device constructor
    #------------------------------------------------------------------
    def __init__(self, cl, name):
        PyTango.Device_4Impl.__init__(self, cl, name)
        DynAttr.init_device(self)
        self.bunch_number = -1
        self.bunches = [-1]
        self.index = 0
        self.f = None
        # Import H5PY. No need to have the dependency if we do not use the
        # DynHDFAttr server.
        self.h5 = __import__("h5py")

    #------------------------------------------------------------------
    #    Read BunchNumber attribute
    #------------------------------------------------------------------
    def read_BunchNumber(self, attr):
        attr.set_value(self.bunches[self.index])

    #------------------------------------------------------------------
    #    Write BunchNumber attribute
    #------------------------------------------------------------------
    def write_BunchNumber(self, attr):
        val = attr.get_write_value(PyTango.ExtractAs.Numpy)
        ind = [index for index in range(len(self.bunches)) if self.bunches[index] == val]
        if ind:
            self.index = ind[0]
            self.updateAttribs__()
        else:
            PyTango.Except.throw_exception("FINISHED",
                                           "There is no more data",
                                           "NextBunch")

    #------------------------------------------------------------------
    #    Update attributes
    #------------------------------------------------------------------
    def updateAttribs__(self):
        for groups in self.f.values():
            for dataset in groups.values():
                attr_name = str(dataset.name.split('/')[-1])
                self.myattrs[attr_name] = dataset[self.index]

    #------------------------------------------------------------------
    #    ProcessHDF command
    #------------------------------------------------------------------
    def ProcessHDF(self, file_name):
        self.f = self.h5.File(file_name, 'r')
        self.bunches = self.f['bunches'][:]
        self.index = 0
        attr_name = ''
        for groups in self.f.values():
            for dataset in groups.values():
                attr_name = str(dataset.name.split('/')[-1])
                attr_typ = fromNp2Tg(dataset.dtype.type)
                if len(dataset.shape) == 1:
                    #scalars:
                    if attr_name not in self.myattrs:
                        self.NewScalar([attr_name, attr_typ])
                if (len(dataset.shape) == 2):
                    #spectrum:
                    if attr_name not in self.myattrs:
                        self.NewSpectrum([attr_name, attr_typ, dataset.shape[1]])
                if (len(dataset.shape) == 3):
                    #spectrum:
                    if attr_name not in self.myattrs:
                        self.NewImage([attr_name, attr_typ, dataset.shape[1], dataset.shape[2]])
                self.myattrs[attr_name] = dataset[0]

    #------------------------------------------------------------------
    #    NextBunch command
    #------------------------------------------------------------------
    def NextBunch(self):
        try:
            new_index = self.index + 1
            self.bunches[new_index]
        except IndexError:
            PyTango.Except.throw_exception("FINISHED",
                                           "There is no more data",
                                           "NextBunch")
        self.index = new_index
        self.updateAttribs__()
        return self.index


class DynHDFAttrClass(DynAttrClass):

    #    Class Properties
    class_property_list = {
        }

    #    Device Properties
    device_property_list = {
        }

    #    Command definitions
    cmd_list = {
        'NewScalar':
            [[PyTango.DevVarStringArray, "Name - of the new scalar attribute\nDOUBLE, SHORT, LONG for the type of the attribute\n"],
             [PyTango.DevVoid, ""]],
        'NewSpectrum':
            [[PyTango.DevVarStringArray, "Name - of the new scalar attribute\nDOUBLE, SHORT, LONG for the type of the attribute\nMaxDim of the spectrum"],
             [PyTango.DevVoid, ""]],
        'NewImage':
            [[PyTango.DevVarStringArray, "Name - of the new scalar attribute\nDOUBLE, SHORT, LONG for the type of the attribute\nMaxDimX of the image\nMaxDimY of the image"],
             [PyTango.DevVoid, ""]],
        'ClearAll':
            [[PyTango.DevVoid, ""],
             [PyTango.DevVoid, ""]],
        'ProcessHDF':
            [[PyTango.DevString, "Path of hdf file."],
             [PyTango.DevVoid, ""]],
        'NextBunch':
            [[PyTango.DevVoid, ""],
             [PyTango.DevLong, "The current BunchNumber"]],
        }

    #    Attribute definitions
    attr_list = {
        'BunchNumber':
            [[PyTango.DevLong,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
                'description':"Bunch Number, index",
            }],
        }

#==================================================================
#
#    DynAttr class main method
#
#==================================================================
if __name__ == '__main__':
    try:
        py = PyTango.Util(sys.argv)
        py.add_TgClass(DynAttrClass, DynAttr, 'DynAttr')
        py.add_TgClass(DynHDFAttrClass, DynHDFAttr, 'DynHDFAttr')

        U = PyTango.Util.instance()
        U.server_init()
        U.server_run()

    except PyTango.DevFailed, e:
        print '-------> Received a DevFailed exception:', e
    except Exception, e:
        print '-------> An unforeseen exception occured....', e