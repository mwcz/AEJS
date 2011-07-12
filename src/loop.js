// This is the basic structure of an interprative emulator

while( !stop_execution ) {

    switch( memory[ PC++ ] ) {

        case OPCODE1:
            opcode1();
            break;

        case OPCODE1:
            opcode1();
            break;

        // ...

        case OPCODEn:
            opcoden();
            break;
    }

}
