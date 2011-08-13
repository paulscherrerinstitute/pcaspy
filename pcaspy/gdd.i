%include "aitTypes.i"
typedef long gddStatus;

%apply aitFloat64 &OUTPUT {aitFloat64 &d};
%apply aitIndex   &OUTPUT {aitIndex &first, aitIndex &count};

%include <std_string.i>

%pythoncode{
import sys
import operator
if sys.version_info[0] > 2:
    str2char = lambda x: bytes(str(x),'utf8')
else: 
    str2char = str
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

	void getTimeStamp(aitTimeStamp* const ts) const;
	void setTimeStamp(const aitTimeStamp* const ts);
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

	// copy the user data into the already set up DD array
        //%rename (putNumericArray) put(const aitFloat64 * const dput);
        //%rename (putFStringArray) put(const aitFixedString * const dput);
        //%rename (putStringArray)  put(const aitString * const dput);
        //void put(const aitFloat64 * const dput);
        //void put(const aitFixedString * const dput);
        //void put(const aitString * const dput);

        %rename (putNumericArray) putRef(aitFloat64 *dput, gddDestructor *dest);
        %rename (putFStringArray) putRef(aitFixedString *dput, gddDestructor *dest);
        %rename (putStringArray)  putRef(aitString *dput, gddDestructor *dest);
        void putRef(aitFloat64 *dput, gddDestructor *dest);
        void putRef(aitFixedString *dput, gddDestructor *dest);
        void putRef(aitString *dput, gddDestructor *dest);

	gddStatus put(const gdd* dd);

	// copy the array data out of the DD
        //%rename (getNumericArray) get(aitFloat64 *dget);
        //%rename (getStringArray)  get(aitString  *dget);
        //void get(aitFloat64 *dget);
        //void get(aitString  *dget);

        %extend {
            void getNumericArray(aitFloat64 *dget, aitUint32 size) {
                self->get(dget);
            }
            void getStringArray(aitString *dget, aitUint32 size) {
                self->get(dget);
            }
        }
        %pythoncode %{
        def put(self, value):
            if type(value) == gdd:
                self.put(gdd)
            elif type(value) in [bool, int, float, long]:
                self.putConvertNumeric(value)
            elif type(value) == str:
                self.putConvertString(value)
            elif hasattr(value, 'shape'): # numpy data type
                if len(value.shape) == 0: # scalar
                    self.putConvertNumeric(value)
                else:
                    if len(value.shape) > 1: # ndarray
                        value = value.flatten()
                    self.setDimension(1)
                    self.setBound(0,0,len(value))
                    if self.primitiveType() == aitEnumFixedString:
                        self.putFStringArray([str2char(v) for v in value])
                    elif self.primitiveType() == aitEnumString:
                        self.putStringArray([str2char(v) for v in value])
                    else:
                        self.putNumericArray(value)
            elif operator.isSequenceType(value):
                if self.primitiveType() == aitEnumInvalid:
                    if type(value[0]) in [bool, int, float, long]:
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
                        return int(valueFloat)
            else:
                if primitiveType in [aitEnumString, aitEnumFixedString]:
                    return self.getStringArray(self.getDataSizeElements())
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

