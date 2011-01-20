#ifndef EXPV_H
#define EXPV_H

#include <casdef.h>
#include <gddAppFuncTable.h>

class PV : public casPV {
    public:
        PV();
        virtual ~PV();

        virtual caStatus read ( const casCtx & ctx, gdd & protoIn);

        virtual caStatus getValue(gdd &value) { return S_casApp_success; };
        virtual caStatus getPrecision(gdd &prec) {return S_casApp_success;};
        virtual caStatus getHighLimit(gdd &hilim) {return S_casApp_success;};
        virtual caStatus getLowLimit(gdd &lolim) {return S_casApp_success;};
        virtual caStatus getUnits(gdd &units) {return S_casApp_success;};
        virtual caStatus getEnums(gdd &enums) {return S_casApp_success;};

        caStatus postEvent(gdd &value);
        void destroy();

        static void initFT();
    private:
        static gddAppFuncTable<PV> ft;
        static int initialized;
};

#endif
