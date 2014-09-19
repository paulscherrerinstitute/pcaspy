#ifndef CHANNEL_H
#define CHANNEL_H

#include <casdef.h>
#include <asLib.h>

class PV; 

class Channel : public casChannel {
    public:
        Channel(const casCtx &ctxIn,  PV *pvIn,  
                const char * const pUserNameIn, 
                const char * const pHostNameIn); 
        ~Channel(); 

        /* server library calls these methods to determine
         * client's access rights.
         */
        bool readAccess() const;
        bool writeAccess() const;
    private:
        Channel & operator = ( const Channel & );
        Channel ( const Channel & );

        PV * pPv; 
        char * pUserName; 
        char * pHostName; 

        ASCLIENTPVT client; 
}; 

#endif
