%include "aitTypes.i"
typedef long gddStatus;

%apply aitFloat64 &OUTPUT {aitFloat64 &d};
%apply aitIndex   &OUTPUT {aitIndex &first, aitIndex &count};
%apply aitInt16   &OUTPUT {aitInt16 &stat, aitInt16 &sevr};

%newobject gdd::getTimeStamp();
%newobject gdd::createDD(aitUint32 app);

%include <std_string.i>

%pythoncode{
import warnings
import sys
if sys.version_info[0] > 2:
    str2char = lambda x: bytes(str(x),'utf8')
    numerics = (bool, int, float)
    import collections.abc
    is_sequence = lambda x: isinstance(x, collections.abc.Sequence)
else:
    str2char = str
    numerics = (bool, int, float, long)
    import operator
    is_sequence = operator.isSequenceType
}

%include "helper_typemaps.i"
%{
#include <gddApps.h>
%}
class gdd {
public:
        %extend {
            // default to be value typed
            gdd(void) {
                return new gdd(gddAppType_value);
            }
        }
        gdd(int app);
        gdd(int app,aitEnum prim);
        gdd(int app,aitEnum prim,int dimen);
        gdd(int app,aitEnum prim,int dimen,aitUint32* size_array);

        void setApplType(int t);
        unsigned applicationType(void) const;

        aitEnum primitiveType(void) const;
        void setPrimType(aitEnum t);

        unsigned dimension(void) const;
        void setDimension(int d,const gddBounds* = NULL);

        gddStatus setBound(unsigned dim_to_set, aitIndex first, aitIndex count);
        gddStatus getBound(unsigned dim_to_get, aitIndex& first, aitIndex& count) const;

        aitUint32 getDataSizeElements(void) const;

        void getTimeStamp(epicsTimeStamp* const ts);
        %extend {
            epicsTimeStamp * getTimeStamp() {
                epicsTimeStamp *ts = new epicsTimeStamp();
                self->getTimeStamp(ts);
                return ts;
            }
        }
        void setTimeStamp(const epicsTimeStamp* ts);
        %extend {
            // set current time
            void setTimeStamp() {
                aitTimeStamp current = epicsTime::getCurrent();
                self->setTimeStamp(&current);
            }
        }

        void setStatus(aitUint32);
        void setStatus(aitUint16 high, aitUint16 low);
        void getStatus(aitUint32&) const;
        void getStatus(aitUint16& high, aitUint16& low) const;

        void setStat(aitUint16);
        void setSevr(aitUint16);
        aitUint16 getStat(void) const;
        aitUint16 getSevr(void) const;
        void setStatSevr(aitInt16 stat, aitInt16 sevr);
        void getStatSevr(aitInt16& stat, aitInt16& sevr) const;

        int isScalar(void) const;
        int isContainer(void) const;
        int isAtomic(void) const;

        gddStatus clear(void); // clear all fields of the DD, including arrays
        void dump();

        gddStatus reference(void) const;
        gddStatus unreference(void) const;

        // get the data in the form the user wants (do conversion)
        %rename (getConvertNumeric) getConvert(aitFloat64& d);
        void getConvert(aitFloat64& d);
        %extend {
            std::string getConvertString() {
                aitString d;
                self->getConvert(d);
                return d.string();
            }
        }
        // convert the user data to the type in the DD and set value
        %rename (putConvertNumeric) putConvert(aitFloat64 d);
        void putConvert(aitFloat64 d);
        %extend {
            void putConvertString(const char * d) {
                self->putConvert(aitString(d));
            }
        };
        // put the user data into the DD and reset the primitive type
        %rename (putNumeric) put(aitFloat64 d);
        gddStatus put(aitFloat64 d);
        %extend {
            void putString(const char *d) {
                self->put(aitString(d));
            }
        }

        %rename (putDD) put(const gdd *dd);
        gddStatus put(const gdd *dd);

        // copy the user data into the already set up DD array
        //%rename (putNumericArray) put(const aitFloat64 * const dput);
        //%rename (putFStringArray) put(const aitFixedString * const dput);
        //%rename (putStringArray)  put(const aitString * const dput);
        //void put(const aitFloat64 * const dput);
        //void put(const aitFixedString * const dput);
        //void put(const aitString * const dput);

        %rename (putCharArray)    putRef(aitUint8 *dput, gddDestructor *dest);
        %rename (putNumericArray) putRef(aitFloat64 *dput, gddDestructor *dest);
        %rename (putFStringArray) putRef(aitFixedString *dput, gddDestructor *dest);
        %rename (putStringArray)  putRef(aitString *dput, gddDestructor *dest);
        void putRef(aitUint8 *dput, gddDestructor *dest);
        void putRef(aitFloat64 *dput, gddDestructor *dest);
        void putRef(aitFixedString *dput, gddDestructor *dest);
        void putRef(aitString *dput, gddDestructor *dest);
        %extend {
            void putCharDataBuffer(void *dput) {
                self->putRef(dput, aitEnumInt8, new pointerDestructor());
            }
            void putShortDataBuffer(void *dput) {
                self->putRef(dput, aitEnumInt16, new pointerDestructor());
            }
            void putIntDataBuffer(void *dput) {
                self->putRef(dput, aitEnumInt32, new pointerDestructor());
            }
            void putFloatDataBuffer(void *dput) {
                self->putRef(dput, aitEnumFloat32, new pointerDestructor());
            }
            void putDoubleDataBuffer(void *dput) {
                self->putRef(dput, aitEnumFloat64, new pointerDestructor());
            }
        }

        // copy the array data out of the DD
        //%rename (getNumericArray) get(aitFloat64 *dget);
        //%rename (getStringArray)  get(aitString  *dget);
        //void get(aitFloat64 *dget);
        //void get(aitString  *dget);

        %extend {
            void getCharArray(aitUint8 *dget, aitUint32 size) {
                self->get(dget);
            }

            void getNumericArray(aitFloat64 *dget, aitUint32 size) {
                self->get(dget);
            }
            void getStringArray(aitString *dget, aitUint32 size) {
                self->get(dget);
            }
            gdd * __getitem__(aitIndex index) {
                return self->getDD(index);
            }

            static gdd *createDD(aitUint32 app) {
                return gddApplicationTypeTable::app_table.getDD(app);
            }
        }
        %pythoncode %{
        def put(self, value):
            primitiveType = self.primitiveType()
            if type(value) == gdd:
                if value.isAtomic():
                    ndims = value.dimension()
                    self.setDimension(ndims)
                    for dim in range(ndims):
                        status, index, size = value.getBound(dim)
                        self.setBound(dim, index, size)
                self.putDD(value)
            elif isinstance(value, numerics):
                if self.isAtomic():
                    self.setBound(0, 0, 1);
                    self.putNumericArray([value])
                else:
                    self.putConvertNumeric(value)
            elif type(value) == str:
                if self.isScalar():
                    self.putConvertString(value)
                else:
                    # if atomic then string is converted to char array
                    valueChar = [ord(v) for v in value]
                    # null terminate
                    valueChar.append(0)
                    self.setDimension(1)
                    self.setBound(0, 0, len(valueChar))
                    self.putCharArray(valueChar)
            elif hasattr(value, 'shape'): # numpy data type
                if len(value.shape) == 0: # scalar
                    self.putConvertNumeric(value.astype(float))
                else:
                    self.setDimension(1)
                    self.setBound(0,0,value.size)
                    if self.primitiveType() == aitEnumFixedString:
                        self.putFStringArray([str2char(v) for v in value])
                    elif self.primitiveType() == aitEnumString:
                        self.putStringArray([str2char(v) for v in value])
                    else:
                        if value.dtype in ['i1', 'u1']:
                            self.putCharDataBuffer(value.data)
                        elif value.dtype in ['i2', 'u2']:
                            self.putShortDataBuffer(value.data)
                        elif value.dtype in ['i4', 'u4']:
                            self.putIntDataBuffer(value.data)
                        elif value.dtype == 'f4':
                            self.putFloatDataBuffer(value.data)
                        elif value.dtype == 'f8':
                            self.putDoubleDataBuffer(value.data)
                        else:
                            warnings.warn("gdd does not support data type %s. Conversion is involved." % value.dtype)
                            self.putNumericArray(value)
            elif is_sequence(value):
                if self.primitiveType() == aitEnumInvalid:
                    if isinstance(value[0], numerics):
                        self.setPrimType(aitEnumFloat64)
                    else:
                        self.setPrimType(aitEnumString)
                self.setDimension(1)
                self.setBound(0,0,len(value))
                if self.primitiveType() == aitEnumFixedString:
                    self.putFStringArray([str2char(v) for v in value])
                elif self.primitiveType() == aitEnumString:
                    self.putStringArray([str2char(v) for v in value])
                else:
                    self.putNumericArray(value)

        def get(self):
            primitiveType = self.primitiveType()
            if self.isScalar():
                if primitiveType in [aitEnumString, aitEnumFixedString]:
                    return self.getConvertString()
                else:
                    valueFloat = self.getConvertNumeric()
                    if primitiveType in [aitEnumFloat32, aitEnumFloat64]:
                        return valueFloat
                    else:
                        valueInt = int(valueFloat)
                        if primitiveType in [aitEnumUint8, aitEnumInt8]:
                            valueChar = valueInt & 0xFF
                            if valueChar == 0:
                                return ''
                            else:
                                return chr(valueChar)
                        else:
                            return valueInt
            else:
                if primitiveType in [aitEnumString, aitEnumFixedString]:
                    return self.getStringArray(self.getDataSizeElements())
                elif primitiveType in [aitEnumUint8, aitEnumInt8]:
                    valueChar = self.getCharArray(self.getDataSizeElements())
                    return ''.join([chr(x) for x in valueChar]).rstrip('\x00')
                else:
                    valueFloat =  self.getNumericArray(self.getDataSizeElements())
                    if primitiveType in [aitEnumFloat32, aitEnumFloat64]:
                        return valueFloat
                    else:
                        return [int(x) for x in valueFloat]

        %}

    %extend {
        ~gdd() {
            self->unreference();
        }
    }
};

