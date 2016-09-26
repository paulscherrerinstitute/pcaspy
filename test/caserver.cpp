#include <fdManager.h>
#include <gddApps.h>
#include <gddAppFuncTable.h>
#include <casdef.h>

#include <string>
#include <map>

class myServer : public caServer
{
    public:
        virtual ~myServer();
        virtual pvExistReturn pvExistTest(const casCtx &ctx,
                const caNetAddr &clientAddress,
                const char *pPVAliasName) {
            
            if (pvs.find(pPVAliasName) != pvs.end())
                return pverExistsHere;
            else
                return pverDoesNotExistHere;
        }

        virtual pvAttachReturn pvAttach(const casCtx &ctx,
                const char *pPVAliasName) {
            if (pvs.find(pPVAliasName) != pvs.end())
                return pvAttachReturn(*pvs[pPVAliasName]);
            else
                return S_casApp_pvNotFound;
        }

        void addPV(const char *name, casPV *pv) { pvs.insert(std::pair<std::string, casPV*>(name, pv)); }
        void process(double delay) { fileDescriptorManager.process(delay); }
    private:
        std::map<std::string, casPV*> pvs;
};

myServer :: ~myServer()
{
}

class myPV;

class myPV : public casPV
{
    public:
        myPV ();
        virtual ~myPV();

        virtual caStatus interestRegister() { monitored = true; return S_casApp_success; }
        virtual void interestDelete() { monitored = false; }
        virtual caStatus read(const casCtx &ctx, gdd &prototype) { return myPV::ft.read(*this, prototype); }
        /* application function table */
        static void initFT() {
            if (!myPV::initialized)
            {
                myPV::ft.installReadFunc ("class", &myPV::getClass);
                myPV::ft.installReadFunc ("value", &myPV::getValue);
                myPV::ft.installReadFunc ("precision", &myPV::getPrecision);
                myPV::ft.installReadFunc ("graphicHigh", &myPV::getHighLimit);
                myPV::ft.installReadFunc ("graphicLow", &myPV::getLowLimit);
                myPV::ft.installReadFunc ("controlHigh", &myPV::getHighLimit);
                myPV::ft.installReadFunc ("controlLow", &myPV::getLowLimit);
                myPV::ft.installReadFunc ("alarmHigh", &myPV::getHighAlarmLimit);
                myPV::ft.installReadFunc ("alarmLow", &myPV::getLowAlarmLimit);
                myPV::ft.installReadFunc ("alarmHighWarning", &myPV::getHighWarnLimit);
                myPV::ft.installReadFunc ("alarmLowWarning", &myPV::getLowWarnLimit);
                myPV::ft.installReadFunc ("units", &myPV::getUnits);
                myPV::ft.installReadFunc ("enums", &myPV::getEnums);
                myPV::initialized = 1;
            }
        }
        virtual caStatus getClass(gdd &klass) { klass.putConvert(""); return S_casApp_success; };
        virtual caStatus getValue(gdd &value) { value.putConvert(fvalue); return S_casApp_success; };
        virtual caStatus getPrecision(gdd &prec) { prec.putConvert(3); return S_casApp_success;};
        virtual caStatus getHighLimit(gdd &hilim) { hilim.putConvert(10); return S_casApp_success;};
        virtual caStatus getLowLimit(gdd &lolim) { lolim.putConvert(-10); return S_casApp_success;};
        virtual caStatus getHighAlarmLimit(gdd &hilim) {hilim.putConvert(10); return S_casApp_success;};
        virtual caStatus getLowAlarmLimit(gdd &lolim) {lolim.putConvert(-10); return S_casApp_success;};
        virtual caStatus getHighWarnLimit(gdd &hilim) {hilim.putConvert(10); return S_casApp_success;};
        virtual caStatus getLowWarnLimit(gdd &lolim) {lolim.putConvert(-10); return S_casApp_success;};
        virtual caStatus getUnits(gdd &units) {units.putConvert("nm"); return S_casApp_success;};
        virtual caStatus getEnums(gdd &enums) {return S_casApp_success;};

        virtual const char *getName() const { return "rdi"; }
        virtual aitEnum bestExternalType() const { return aitEnumFloat64; }
        virtual unsigned maxDimension() const { return 0; }
        virtual aitIndex maxBound(unsigned dimension) { return dimension == 0 ? 1 : 0; }
        virtual void destroy() {}

        void setValue(double value) {
            fvalue = value;
            if (monitored) {
                gdd *pDD = gddApplicationTypeTable::AppTable().getDD(gddAppType_dbr_ctrl_double);
                pDD[gddAppTypeIndex_dbr_ctrl_double_units].putConvert("nm");
                pDD[gddAppTypeIndex_dbr_ctrl_double_alarmLowWarning].putConvert(-10);
                pDD[gddAppTypeIndex_dbr_ctrl_double_alarmHighWarning].putConvert(10);
                pDD[gddAppTypeIndex_dbr_ctrl_double_alarmLow].putConvert(-10);
                pDD[gddAppTypeIndex_dbr_ctrl_double_alarmHigh].putConvert(10);
                pDD[gddAppTypeIndex_dbr_ctrl_double_controlLow].putConvert(-10);
                pDD[gddAppTypeIndex_dbr_ctrl_double_controlHigh].putConvert(10);
                pDD[gddAppTypeIndex_dbr_ctrl_double_graphicLow].putConvert(-10);
                pDD[gddAppTypeIndex_dbr_ctrl_double_graphicHigh].putConvert(10);
                pDD[gddAppTypeIndex_dbr_ctrl_double_precision].putConvert(3);
                pDD[gddAppTypeIndex_dbr_ctrl_double_value].putConvert(fvalue);
                postEvent(getCAS()->valueEventMask(), *pDD);
                pDD->unreference();
            }
        }

    private:
        static gddAppFuncTable<myPV> ft;
        static bool initialized;
        double fvalue;
        bool monitored;
};

gddAppFuncTable<myPV> myPV::ft;
bool myPV :: initialized = false;

myPV :: myPV()
    : fvalue(0),monitored(false)
{
    if (!initialized)
        initFT();
}

myPV :: ~myPV()
{
}

void taskUpdate(void *arg)
{
    myPV * pPV = (myPV *) arg;
    while (true) {
        pPV->setValue((double)rand()/RAND_MAX*10);
        //epicsThreadSleep(0.001);
    }
}

int main()
{
    myServer server;
    myPV pv;
    server.addPV("rdi", &pv);
    
    epicsThreadCreate("taskUpdate",
            epicsThreadPriorityMedium,
            epicsThreadGetStackSize(epicsThreadStackMedium),
            taskUpdate,
            &pv);

    while (true)
        server.process(0.2);
    return 0;
}
