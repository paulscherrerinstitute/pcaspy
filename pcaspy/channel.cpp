
#include "pv.h"
#include "channel.h"

Channel :: Channel(const casCtx &ctxIn,  
        PV *pvIn,  
        const char * const user, 
        const char * const host)
            : casChannel(ctxIn) 
{
    pPv = pvIn; 
    pUserName = user; 
    pHostName = host; 
}

bool Channel :: readAccess() const
{ 
    if (pPv) 
        return pPv->readAccess(pUserName,  pHostName);  
    else 
        return true; 
}

bool Channel :: writeAccess() const
{ 
    if (pPv) 
        return pPv->writeAccess(pUserName,  pHostName);  
    else 
        return true; 
}

