prefix = ''
pvdb = {
'RAND' : {
    },

'WAVE' : { 
    'count': 20, 
    'prec' :  3, 
    },

'SHUFFLE' : { 
    'type' : 'enum',
    'enums': ['None', 'Shuffle'],
    'scan' : 0,
    },

'CMD'     : {
    'type' : 'str',
    'scan' : 0,
    },

'START'   : {
    'type' : 'enum',
    'enums': ['STOP', 'START'],
    'asyn' : True,
    },
}
