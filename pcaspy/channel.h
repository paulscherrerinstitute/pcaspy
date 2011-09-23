#ifndef CHANNEL_H
#define CHANNEL_H

#include <casdef.h>

class PV; 

class Channel : public casChannel {
    public:
        Channel(const casCtx &ctxIn,  PV *pvIn,  const char * const pUserNameIn, const char * const pHostNameIn); 

        bool readAccess() const;
        bool writeAccess() const;
    private:
        Channel & operator = ( const Channel & );
        Channel ( const Channel & );

        PV * pPv; 
        const char * pUserName; 
        const char * pHostName; 
}; 


#endif
