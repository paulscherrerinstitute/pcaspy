#include "pv.h"

int PV :: initialized = 0;
gddAppFuncTable<PV> PV :: ft;

PV :: PV () {
    PV::initFT();
}

PV ::~PV () {
}

caStatus PV :: read ( const casCtx & ctx, gdd & protoIn)
{
    return PV::ft.read ( *this, protoIn );
}

caStatus PV :: postEvent(gdd &value)
{

    //
    // post a value change event
    //
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

void PV :: destroy()
{
}
