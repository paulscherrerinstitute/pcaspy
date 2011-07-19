%include "aitTypes.i"
typedef long gddStatus;

%apply aitFloat64 &OUTPUT {aitFloat64 &d};
%apply aitIndex   &OUTPUT {aitIndex &first, aitIndex &count};

%include <std_string.i>

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
            elif type(value) in [bool, int, long, float]:
                self.setDimension(0)
                self.putNumeric(value)
            elif type(value) == str:
                self.setDimension(0)
                self.putString(value)
            elif type(value) == list:
                if self.primitiveType() == aitEnumInvalid:
                    if type(value[0]) in [bool, int, long, float]:
                        self.setPrimType(aitEnumFloat64)
                    else:
                        self.setPrimType(aitEnumString)
                self.setDimension(1)
                self.setBound(0,0,len(value))
                if self.primitiveType() == aitEnumFixedString:
                    self.putFStringArray([str(v) for v in value])
                elif self.primitiveType() == aitEnumString:
                    self.putStringArray([str(v) for v in value])
                else:
                    self.putNumericArray(value)

        def get(self):
            if self.isScalar():
                if self.primitiveType() in [aitEnumString, aitEnumFixedString]:
                    return self.getConvertString()
                else:
                    return self.getConvertNumeric()
            else:
                if self.primitiveType() in [aitEnumString, aitEnumFixedString]:
                    return self.getStringArray(self.getDataSizeElements())
                else:
                    return self.getNumericArray(self.getDataSizeElements())

        %}

    %extend {
        ~gdd() {
            self->unreference();
        }
    }
};
