%module(directors="1") cas

%{
#define SWIG_FILE_WITH_INIT
#include <fdManager.h>
#include <casdef.h>
#include <asLib.h>
#include <asCa.h>
#include "pv.h"
%}
%include <epicsVersion.h>


#define MAX_ENUM_STRING_SIZE        26
#define MAX_ENUM_STATES             16


%feature("director") caServer;
%feature("director") casPV;
%feature("director") PV;
%feature("director") casChannel;

/* print exceptions originated from Python */
%feature("director:except") {
    if ($error != NULL) {
        PyErr_Print();
        Swig::DirectorMethodException::raise("Exception Calling Python Code");
    }
}

%include "errMdef.i"
%include "gdd.i"

#define DBE_VALUE    (1<<0)
#define DBE_ARCHIVE  (1<<1)
#define DBE_LOG      DBE_ARCHIVE
#define DBE_ALARM    (1<<2)
#define DBE_PROPERTY (1<<3)

%include "cstring.i"

%defaultdtor caNetAddr;
class caNetAddr {
public:
    caNetAddr();
    caNetAddr operator = ( const caNetAddr & naIn );

    %cstring_output_maxsize(char *pString, unsigned stringLength)
    void stringConvert (char *pString, unsigned stringLength) const;
};

typedef aitUint32 caStatus;
/* pvExistReturn */
enum pvExistReturnEnum { pverExistsHere, pverDoesNotExistHere, pverAsyncCompletion };
class caServer {
public:
    caServer();
    virtual ~caServer()=0;

    virtual pvExistReturn pvExistTest ( const casCtx & ctx,
        const caNetAddr & clientAddress, const char * pPVAliasName );

    virtual pvAttachReturn pvAttach ( const casCtx &ctx,
        const char *pPVAliasName );

    casEventMask registerEvent ( const char *pName );
    casEventMask valueEventMask () const; // DBE_VALUE
    casEventMask logEventMask () const;  // DBE_LOG
    casEventMask alarmEventMask () const; // DBE_ALARM

    void setDebugLevel ( unsigned level );
    unsigned getDebugLevel () const;

    virtual void show ( unsigned level ) const;

    unsigned subscriptionEventsPosted () const;
    unsigned subscriptionEventsProcessed () const;

    class epicsTimer & createTimer ();

    void generateBeaconAnomaly ();
};

class casPV {
public:
    casPV ();
    virtual ~casPV ();

    virtual void show ( unsigned level ) const;

    virtual caStatus interestRegister ();
    virtual void interestDelete ();

    virtual caStatus beginTransaction ();
    virtual void endTransaction ();

    virtual caStatus read (const casCtx &ctx, gdd &prototype);
    virtual caStatus write (const casCtx &ctx, const gdd &value);
    #if EPICS_VERSION > 3 || \
        EPICS_VERSION == 3 && EPICS_REVISION > 14 || \
        EPICS_VERSION == 3 && EPICS_REVISION == 14 && EPICS_MODIFICATION >= 11
        #define EPICS_HAS_WRITENOTIFY 1
    virtual caStatus writeNotify (const casCtx &ctx, const gdd &value);
    #else
        #define EPICS_HAS_WRITENOTIFY 0
    #endif

    virtual aitEnum bestExternalType () const;

    virtual unsigned maxDimension () const; // return zero if scalar
    virtual aitIndex maxBound ( unsigned dimension ) const;

    virtual void destroy ();

    virtual const char * getName () const = 0;

    caServer * getCAS () const;
};

class PV : public casPV {
public:
    PV();
    virtual ~PV();

    caStatus read (const casCtx &ctx, gdd &protoIn);
    caStatus postEvent (int mask, gdd &value);

    virtual caStatus getValue(gdd &value);
    virtual caStatus getPrecision(gdd &prec);
    virtual caStatus getHighLimit(gdd &hilim);
    virtual caStatus getLowLimit(gdd &lolim);
    virtual caStatus getHighAlarmLimit(gdd &hilim);
    virtual caStatus getLowAlarmLimit(gdd &lolim);
    virtual caStatus getHighWarnLimit(gdd &hilim);
    virtual caStatus getLowWarnLimit(gdd &lolim);
    virtual caStatus getUnits(gdd &units);
    virtual caStatus getEnums(gdd &enums);

    bool setAccessSecurityGroup(const char *);

    void startAsyncWrite(const casCtx &ctx);
    void endAsyncWrite(caStatus status);
    bool hasAsyncWrite();

    void destroy ();
};

class casChannel {
public:
    casChannel (const casCtx & ctx);
    virtual ~casChannel ();

    virtual void setOwner ( const char * const pUserName,
        const char * const pHostName );

    virtual bool readAccess () const;
    virtual bool writeAccess () const;

    virtual bool confirmationRequested () const;

    virtual caStatus beginTransaction ();
    virtual void endTransaction ();

    virtual caStatus read (const casCtx &ctx, gdd &prototype);
    virtual caStatus write (const casCtx &ctx, const gdd &value);
    #if EPICS_VERSION > 3 || \
        EPICS_VERSION == 3 && EPICS_REVISION > 14 || \
        EPICS_VERSION == 3 && EPICS_REVISION == 14 && EPICS_MODIFICATION >= 11
    virtual caStatus writeNotify(const casCtx &ctx, const gdd &value);
    #endif

    virtual void show ( unsigned level ) const;

    virtual void destroy ();
};

void asCaStart();
void asCaStop();

long asInitFile(const char *filename, const char *substitutions);

void process(double delay);
%{
void process(double delay) {
    fileDescriptorManager.process(delay);
}
%}

// rename original class casPV to _casPV because it is
// not meant for use instead PV should be used.
%pythoncode {
_casPV = casPV
casPV = PV
}
