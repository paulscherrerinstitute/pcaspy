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
typedef unsigned int        epicsUInt32;


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

%#include <epicsTime.h>

#define POSIX_TIME_AT_EPICS_EPOCH 631152000u

/* epics time stamp for C interface*/
typedef struct epicsTimeStamp {
    epicsUInt32 secPastEpoch; /* seconds since 0000 Jan 1, 1990 */
    epicsUInt32 nsec;         /* nanoseconds within second */

%extend {
    epicsTimeStamp() {
        epicsTimeStamp *ts = (epicsTimeStamp*) malloc(sizeof(epicsTimeStamp));
        epicsTimeGetCurrent(ts);
        return ts;
    }

    epicsTimeStamp(epicsUInt32 secPastEpoch, epicsUInt32 nsec) {
        epicsTimeStamp *ts = (epicsTimeStamp*) malloc(sizeof(epicsTimeStamp));
        ts->secPastEpoch = secPastEpoch;
        ts->nsec = nsec;
        return ts;
    }

    ~epicsTimeStamp() {
        free(self);
    }
}
%pythoncode {
    def __str__(self):
        return '%d,%d' % (self.secPastEpoch, self.nsec)
}
} epicsTimeStamp;


