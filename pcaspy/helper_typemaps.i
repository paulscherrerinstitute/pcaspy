/*
  swig typemap to facilitate argument pass and return

*/

/* const char* input */
%typemap(directorin) const char * pPVAliasName {
    %#if PY_VERSION_HEX >= 0x03000000
        $input = PyUnicode_FromString(pPVAliasName);
        if ($input == NULL) {
            PyErr_Print();
            $input = PyUnicode_DecodeLatin1(pPVAliasName, strlen(pPVAliasName), pPVAliasName);
        }
    %#else
        $input = PyString_FromString(pPVAliasName);
    %#endif
}

/* pvExistReturn */
%typemap(directorout) pvExistReturn {
    if (PyInt_Check($1)) {
        unsigned int val;
        int res = SWIG_AsVal_unsigned_SS_int($1, &val);
        if (SWIG_IsOK(res)) {
            pvExistReturnEnum status = static_cast< pvExistReturnEnum >(val);
            $result = pvExistReturn(status);
        }
    }
}

/* pvAttachReturn */
%typemap(directorout) pvAttachReturn {
    if (PyLong_Check($1)) {
        unsigned int val;
        int res = SWIG_AsVal_unsigned_SS_int($1, &val);
        if (SWIG_IsOK(res)) {
            caStatus status = static_cast< caStatus >(val);
            $result = pvAttachReturn(status);
        }
    }
    else {
        void *argp;
        int res = SWIG_ConvertPtr($1, &argp,SWIGTYPE_p_casPV, 0 |  0 );
        if (SWIG_IsOK(res)) {
            casPV *pv = reinterpret_cast< casPV * >(argp);
            $result = pvAttachReturn(*pv);
        }
    }
}

/* gddDestructor of aitFixedString array */
%{
class aitFixedStringDestructor: public gddDestructor {
    void run (void *);
};
void aitFixedStringDestructor::run ( void * pUntyped )
{
    aitFixedString *ps = (aitFixedString *) pUntyped;
    delete [] ps;
}

/* gddDestructor of aitFloat64 array */
class aitFloat64Destructor: public gddDestructor {
    void run (void *);
};
void aitFloat64Destructor::run ( void * pUntyped )
{
    aitFloat64 *ps = (aitFloat64 *) pUntyped;
    delete [] ps;
}

/* gddDestructor of aitUint8 array */
class aitUint8Destructor: public gddDestructor {
    void run (void *);
};
void aitUint8Destructor::run ( void * pUntyped )
{
    aitUint8 *ps = (aitUint8 *) pUntyped;
    delete [] ps;
}


/* gddDestructor of aitString array */
class aitStringDestructor: public gddDestructor {
    void run (void *);
};
void aitStringDestructor::run ( void * pUntyped )
{
    aitString *ps = (aitString *) pUntyped;
    delete [] ps;
}

/* gddDestructor of void pointer */
class pointerDestructor: public gddDestructor {
    void run (void *);
};
void pointerDestructor::run ( void * pUntyped )
{
    free (pUntyped);
}
%}

/* const aitFloat64 array pointer input  */
%typemap (in) aitFloat64 *dput {
    if (PySequence_Check($input)) {
        int size = PySequence_Size($input);
        int i = 0;
        $1 = new aitFloat64[size];
        for (i=0; i<size; i++)
        {
            PyObject *o = PySequence_GetItem($input, i);
            $1[i] = PyFloat_AsDouble(o);
            Py_XDECREF(o);
        }
    }
}
%typemap(freearg) aitFloat64 *dput {
    delete [] $1;
}

/* aitFloat64 array pointer and destructor input */
%typemap (in) (aitFloat64 *dput,gddDestructor *dest ) {
    if (PySequence_Check($input)) {
        int size = PySequence_Size($input);
        int i = 0;
        $1 = new aitFloat64[size];
        for (i=0; i<size; i++)
        {
            PyObject *o = PySequence_GetItem($input, i);
            $1[i] = PyFloat_AsDouble(o);
            Py_XDECREF(o);
        }
        $2 = new aitFloat64Destructor();
    }
}

/* aitFloat64 array pointer output */
%typemap (in) (aitFloat64 *dget, aitUint32 size) {
    if (!PyInt_Check($input)) {
       PyErr_SetString(PyExc_ValueError, "Expecting an integer");
       return NULL;
    }
    $2 = PyInt_AsLong($input);
    if ($2 < 0) {
        PyErr_SetString(PyExc_ValueError, "Positive integer expected");
        return NULL;
    }
    $1 = new aitFloat64[$2];
}

%typemap (argout) (aitFloat64 *dget, aitUint32 size) {
    Py_XDECREF($result);
    $result = PyList_New($2);
    for (aitUint32 i=0; i<$2; i++) {
        PyObject *o = PyFloat_FromDouble($1[i]);
        PyList_SetItem($result, i, o);
    }
    delete [] $1;
}

/* const aitFixedString array pointer input */
%typemap (in) aitFixedString *dput {
    if (PySequence_Check($input)) {
        int size = PySequence_Size($input);
        int i = 0;
        $1 = new aitFixedString[size];
        for (i=0; i<size; i++)
        {
            PyObject *o = PySequence_GetItem($input, i);
            strncpy ($1[i].fixed_string, PyString_AsString(o), AIT_FIXED_STRING_SIZE);
            Py_XDECREF(o);
        }
    }
}
%typemap(freearg) aitFixedString *dput{
    delete [] $1;
}
/* aitFixedString array pointer and destructor input */
%typemap (in) (aitFixedString *dput, gddDestructor *dest) {
    if (PySequence_Check($input)) {
        int size = PySequence_Size($input);
        int i = 0;
        $1 = new aitFixedString[size];
        for (i=0; i<size; i++)
        {
            PyObject *o = PySequence_GetItem($input, i);
            strncpy ($1[i].fixed_string, PyString_AsString(o), AIT_FIXED_STRING_SIZE);
            Py_XDECREF(o);
        }
        $2 = new aitFixedStringDestructor();
    }
}

/* const aitString array pointer input */
%typemap (in) aitString *dput {
    if (PySequence_Check($input)) {
        int size = PySequence_Size($input);
        int i = 0;
        $1 = new aitString[size];
        for (i=0; i<size; i++)
        {
            PyObject *o = PySequence_GetItem($input, i);
            $1[i] = PyString_AsString(o);
            Py_XDECREF(o);
        }
    }
}
%typemap(freearg) aitString *dput{
    delete [] $1;
}

/* aitString array pointer and destructor input */
%typemap (in) (aitString *dput, gddDestructor *dest) {
    if (PySequence_Check($input)) {
        int size = PySequence_Size($input);
        int i = 0;
        $1 = new aitString[size];
        for (i=0; i<size; i++)
        {
            PyObject *o = PySequence_GetItem($input, i);
            $1[i] = PyString_AsString(o);
            Py_XDECREF(o);
        }
        $2 = new aitStringDestructor();
    }
}

/* aitString array pointer output */
%typemap (in) (aitString *dget, aitUint32 size) {
    if (!PyInt_Check($input)) {
       PyErr_SetString(PyExc_ValueError, "Expecting an integer");
       return NULL;
    }
    $2 = PyInt_AsLong($input);
    if ($2 < 0) {
        PyErr_SetString(PyExc_ValueError, "Positive integer expected");
        return NULL;
    }
    $1 = new aitString[$2];
}
%typemap (argout) (aitString *dget, aitUint32 size) {
    Py_XDECREF($result);
    $result = PyList_New($2);
    for (aitUint32 i=0; i<$2; i++) {
        PyObject *o = PyString_FromString($1[i].string());
        PyList_SetItem($result, i, o);
    }
    delete [] $1;
}



/* const aitUint8 array pointer input  */
%typemap (in) aitUint8 *dput {
    if (PySequence_Check($input)) {
        int size = PySequence_Size($input);
        int i = 0;
        $1 = new aitUint8[size];
        for (i=0; i<size; i++)
        {
            PyObject *o = PySequence_GetItem($input, i);
            $1[i] = (aitUint8) PyInt_AsLong(o);
            Py_XDECREF(o);
        }
    }
}
%typemap(freearg) aitUint8 *dput {
    delete [] $1;
}

/* aitUint8 array pointer and destructor input */
%typemap (in) (aitUint8 *dput,gddDestructor *dest ) {
    if (PySequence_Check($input)) {
        int size = PySequence_Size($input);
        int i = 0;
        $1 = new aitUint8[size];
        for (i=0; i<size; i++)
        {
            PyObject *o = PySequence_GetItem($input, i);
            $1[i] = (aitUint8) PyInt_AsLong(o);
            Py_XDECREF(o);
        }
        $2 = new aitUint8Destructor();
    }
}

/* aitUint8 array pointer output */
%typemap (in) (aitUint8 *dget, aitUint32 size) {
    if (!PyInt_Check($input)) {
       PyErr_SetString(PyExc_ValueError, "Expecting an integer");
       return NULL;
    }
    $2 = PyInt_AsLong($input);
    if ($2 < 0) {
        PyErr_SetString(PyExc_ValueError, "Positive integer expected");
        return NULL;
    }
    $1 = new aitUint8[$2];
}
%typemap (argout) (aitUint8 *dget, aitUint32 size) {
    Py_XDECREF($result);
    $result = PyList_New($2);
    for (aitUint32 i=0; i<$2; i++) {
        PyObject *o = PyInt_FromLong($1[i]);
        PyList_SetItem($result, i, o);
    }
    delete [] $1;
}


/* void pointer input */
%typemap (in) (void *dput) {
%#if PY_VERSION_HEX<0x03000000
    if (PyBuffer_Check($input)) {
        PyObject *buff = PyBuffer_FromObject($input, 0, Py_END_OF_BUFFER);
        if (buff != NULL) {
            const void *data = NULL;
            Py_ssize_t size = 0;
            int error = PyObject_AsReadBuffer(buff, &data, &size);
            if (error == 0) {
                $1 = calloc(size, sizeof(char));
                memcpy($1, data, size);
            } else {
                printf("error in read PyBufferObject\n");
            }
        } else {
            printf("error in get PyBufferObject\n");
        }
        Py_XDECREF(buff);
    } else
%#endif
    if (PyObject_CheckBuffer($input)) {
        Py_buffer buff;
        int error = PyObject_GetBuffer($input, &buff, PyBUF_SIMPLE);
        if (error == 0) {
            $1 = calloc(buff.len, sizeof(char));
            memcpy($1, buff.buf, buff.len);
            PyBuffer_Release(&buff);
        } else {
            printf("error in get Py_buffer\n");
        }
    }
}
