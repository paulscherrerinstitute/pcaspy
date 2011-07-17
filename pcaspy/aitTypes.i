typedef signed char         aitInt8;
typedef unsigned char       aitUint8;
typedef short               aitInt16;
typedef unsigned short      aitUint16;
typedef aitUint16           aitEnum16;
typedef int                 aitInt32;
typedef unsigned int        aitUint32;
typedef float               aitFloat32;
typedef double              aitFloat64;
typedef unsigned int        aitIndex;
typedef void*               aitPointer;
typedef aitUint32           aitStatus;


typedef enum {
	aitEnumInvalid=0,
	aitEnumInt8,
	aitEnumUint8,
	aitEnumInt16,
	aitEnumUint16,
	aitEnumEnum16,
	aitEnumInt32,
	aitEnumUint32,
	aitEnumFloat32,
	aitEnumFloat64,
	aitEnumFixedString,
	aitEnumString,
	aitEnumContainer
} aitEnum;


class aitTimeStamp {
public:
    aitTimeStamp ();
    aitTimeStamp (const unsigned long tv_secIn, const unsigned long tv_nsecIn);
    void getTV(long &tv_secOut, long &uSecOut) const;
};
