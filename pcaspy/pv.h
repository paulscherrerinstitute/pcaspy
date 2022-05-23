#ifndef PV_H
#define PV_H

#include <casdef.h>
#include <gddAppFuncTable.h>
#include <caeventmask.h>
#include <asLib.h>

class PV;

class AsyncWriteIO : public casAsyncWriteIO {
    public:
        AsyncWriteIO(const casCtx & ctxIn,  PV & pvIn);
        ~AsyncWriteIO();
    private:
        PV & pv;
};

class PV : public casPV {
    public:
        PV();
        virtual ~PV();

        /* Override base class function to implement application function table */
        caStatus read ( const casCtx & ctx, gdd & protoIn);
        /* application function table */
        static void initFT();
        virtual caStatus getClass(gdd &klass) { klass.put(""); return S_casApp_success; };
        virtual caStatus getValue(gdd &value) { return S_casApp_success; };
        virtual caStatus getPrecision(gdd &prec) {return S_casApp_success;};
        virtual caStatus getHighLimit(gdd &hilim) {return S_casApp_success;};
        virtual caStatus getLowLimit(gdd &lolim) {return S_casApp_success;};
        virtual caStatus getHighAlarmLimit(gdd &hilim) {return S_casApp_success;};
        virtual caStatus getLowAlarmLimit(gdd &lolim) {return S_casApp_success;};
        virtual caStatus getHighWarnLimit(gdd &hilim) {return S_casApp_success;};
        virtual caStatus getLowWarnLimit(gdd &lolim) {return S_casApp_success;};
        virtual caStatus getUnits(gdd &units) {return S_casApp_success;};
        virtual caStatus getEnums(gdd &enums) {return S_casApp_success;};

        /* Post value/alarm change event */
        caStatus postEvent(int mask, gdd &value);

        /* Server library calls this function when all channel are disconnected
         * or server is shutting down.
         * The base class executes "delete this" by default.
         *
         * We want PV to exist through the lifetime of application,
         * this is a no-op method. The PV instance is deleted by explicitly
         * calling delete.
         */
        void destroy();

        /* Async write */
        void startAsyncWrite(const casCtx & ctx);
        bool hasAsyncWrite() {return pAsyncWrite != NULL;};
        void endAsyncWrite(caStatus status);
        void removeAsyncWrite();

        /* Access security group */
        ASMEMBERPVT getAccessSecurityGroup() { return member; }
        bool setAccessSecurityGroup(const char *asgName);

        casChannel * createChannel ( const casCtx &ctx,
                                    const char * const pUserName,
                                    const char * const pHostName);

    private:
        volatile AsyncWriteIO * pAsyncWrite;
        /* application function table */
        static gddAppFuncTable<PV> ft;
        static int initialized;
        /* access security group name and member pointer*/
        char *asg;
        ASMEMBERPVT member;
};

#endif
