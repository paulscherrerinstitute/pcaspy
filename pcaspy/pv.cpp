#include <stdio.h>
#include <epicsString.h>
#include <errlog.h>

#include "channel.h"
#include "pv.h"

AsyncWriteIO::AsyncWriteIO ( const casCtx & ctxIn, PV & pvIn ) :
	casAsyncWriteIO ( ctxIn ), pv ( pvIn )
{
}

AsyncWriteIO::~AsyncWriteIO()
{
	this->pv.removeAsyncWrite();
}

/* Application function table init */
int PV :: initialized = 0;
gddAppFuncTable<PV> PV :: ft;


PV :: PV () 
    : pAsyncWrite(NULL), 
    asg(NULL), 
    member(NULL)
{
    PV::initFT();
}

PV ::~PV () 
{
    if (member)
        asRemoveMember(&member); 
    if (asg)
        free(asg); 
}

// called by server application to specify access rights 
// by given ASG name. 
// this is called in Python subclass SimplePV
bool PV :: setAccessSecurityGroup (const char *asgName)
{
    asg = epicsStrDup(asgName); 
    if (asAddMember(&member, asg)) {
        member = NULL; 
        return false; 
    }
    return true; 
}

// called by server library when connection established
casChannel * PV :: createChannel ( const casCtx &ctx, 
        const char * const pUserName, 
        const char * const pHostName )
{ 
    return new Channel(ctx, this,  pUserName,  pHostName);
}

caStatus PV :: read ( const casCtx & ctx, gdd & protoIn)
{
    return PV::ft.read ( *this, protoIn );
}

// called by server application when it starts async write operation
void PV :: startAsyncWrite( const casCtx & ctx )
{
    pAsyncWrite = new AsyncWriteIO ( ctx,  *this );
}
// called by server application when it finishes async write operation
void PV :: endAsyncWrite(caStatus status)
{
    // Get copy of volatile pointer
    AsyncWriteIO *io = (AsyncWriteIO *)pAsyncWrite;
    if (io)
        io->postIOCompletion ( status );
    else
        errlogPrintf("%s has invalid AsyncWriteIO pointer\n", this->getName());
}
// called by AsyncWriteIO destructor to remove pending async write
void PV :: removeAsyncWrite()
{
    pAsyncWrite = NULL; 
}
// called by server application when it changes value and notifies clients
caStatus PV :: postEvent(gdd &value)
{
    caServer * pCAS = this->getCAS();
    if ( pCAS != NULL ) {
        casEventMask select ( pCAS->valueEventMask() | pCAS->logEventMask() );
        casPV::postEvent(select, value);
    }
    return S_casApp_success;
}

void PV :: initFT()
{
    if (!PV::initialized)
    {
        PV::ft.installReadFunc ("value", &PV::getValue);
        PV::ft.installReadFunc ("precision", &PV::getPrecision);
        PV::ft.installReadFunc ("graphicHigh", &PV::getHighLimit);
        PV::ft.installReadFunc ("graphicLow", &PV::getLowLimit);
        PV::ft.installReadFunc ("controlHigh", &PV::getHighLimit);
        PV::ft.installReadFunc ("controlLow", &PV::getLowLimit);
        PV::ft.installReadFunc ("alarmHigh", &PV::getHighLimit);
        PV::ft.installReadFunc ("alarmLow", &PV::getLowLimit);
        PV::ft.installReadFunc ("alarmHighWarning", &PV::getHighLimit);
        PV::ft.installReadFunc ("alarmLowWarning", &PV::getLowLimit);
        PV::ft.installReadFunc ("units", &PV::getUnits);
        PV::ft.installReadFunc ("enums", &PV::getEnums);
        PV::initialized = 1;
    }
}
// no-op because PV is live through the life time of server application
void PV :: destroy()
{
}
