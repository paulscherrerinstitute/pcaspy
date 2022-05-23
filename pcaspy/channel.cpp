#include <stdio.h>
#include <string.h>

#include "pv.h"
#include "channel.h"

/* Macro asCheckPut and asCheckGet return TRUE/FALSE */
#ifndef TRUE
#define TRUE 1
#endif

#ifndef FALSE
#define FALSE 0
#endif

/* callback by as library when access rights changes
 * it posts this event to clients
 * */
void clientCallback(ASCLIENTPVT asClientPvt, asClientStatus /*s*/)
{
    Channel *channel = (Channel *)asGetClientPvt(asClientPvt);
    channel->postAccessRightsEvent();
}

Channel :: Channel(const casCtx &ctxIn,
        PV *pvIn,
        const char * const user,
        const char * const host)
            : casChannel(ctxIn),pUserName(NULL),pHostName(NULL)
{
    pPv = pvIn;
    if (user)
      pUserName = strdup(user);
    if (host)
      pHostName = strdup(host);

    /* add as client and register access rights callback */
    ASMEMBERPVT member = pvIn->getAccessSecurityGroup();
    if (member && asAddClient(&client,  member,  1,
                pUserName,  pHostName)  == 0) {
        asPutClientPvt(client,  this);
        asRegisterClientCallback(client, ::clientCallback);
    } else
        client = NULL;
}

Channel :: ~Channel()
{
    if (client)
        asRemoveClient(&client);
    free(pUserName);
    free(pHostName);
}


bool Channel :: readAccess() const
{
    if (client)
        return asCheckGet(client);
    else
        return true;
}

bool Channel :: writeAccess() const
{
    if (client)
        return asCheckPut(client);
    else
        return true;
}

