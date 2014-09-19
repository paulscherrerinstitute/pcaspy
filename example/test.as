# only writable when $(P)LEVEL is below 3
# 
ASG(fill) {
    INPA($(P)LEVEL)
    RULE(1, READ)
    RULE(1, WRITE){
        CALC("A<3")
    }
}
