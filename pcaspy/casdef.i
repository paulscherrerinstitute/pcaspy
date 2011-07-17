%module(directors="1") cas

%{
#define SWIG_FILE_WITH_INIT
#include <fdManager.h>
#include <casdef.h>
#include "pv.h"
%}

%feature("director") caServer;
%feature("director") casPV;
%feature("director") PV;
%feature("director") casChannel;

%include "errMdef.i"
%include "gdd.i"

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
    //virtual caStatus writeNotify (const casCtx &ctx, const gdd &value);

    virtual casChannel * createChannel ( const casCtx &ctx,
        const char * const pUserName, const char * const pHostName );
    
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

    virtual caStatus read (const casCtx &ctx, gdd &protoIn);
    caStatus postEvent (gdd &value);

    virtual caStatus getValue(gdd &value);
    virtual caStatus getPrecision(gdd &prec);
    virtual caStatus getHighLimit(gdd &hilim);
    virtual caStatus getLowLimit(gdd &lolim);
    virtual caStatus getUnits(gdd &units);
    virtual caStatus getEnums(gdd &enums);

    void startAsyncWrite(const casCtx &ctx);
    void endAsyncWrite(caStatus status);

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
    /*virtual caStatus writeNotify(const casCtx &ctx, const gdd &value);*/

    virtual void show ( unsigned level ) const;

    virtual void destroy ();
};

void process(double delay);
%{
void process(double delay) {
    fileDescriptorManager.process(delay);
}
%}

%pythoncode {
# rename original class casPV to _casPV because it is not meant for use
# instead PV should be used
_casPV = casPV
casPV = PV
}
