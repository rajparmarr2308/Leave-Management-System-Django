// Compatibility with Visual Studio 2013 and older which don't support
// the inline keyword in C (only in C++): use __inline instead.
#if (defined(_MSC_VER) && _MSC_VER < 1900 \
     && !defined(__cplusplus) && !defined(inline))
#  define PYCAPI_COMPAT_STATIC_INLINE(TYPE) static __inline TYPE
#else
#  define PYCAPI_COMPAT_STATIC_INLINE(TYPE) static inline TYPE
#endif

// C++ compatibility
#ifdef __cplusplus
#  define PYCAPI_COMPAT_CAST(TYPE, EXPR) reinterpret_cast<TYPE>(EXPR)
#  define PYCAPI_COMPAT_NULL nullptr
#else
#  define PYCAPI_COMPAT_CAST(TYPE, EXPR) ((TYPE)(EXPR))
#  define PYCAPI_COMPAT_NULL NULL
#endif

// Cast argument to PyObject* type.
#ifndef _PyObject_CAST
#  define _PyObject_CAST(op) PYCAPI_COMPAT_CAST(PyObject*, op)
#endif
#ifndef _PyObject_CAST_CONST
#  define _PyObject_CAST_CONST(op) PYCAPI_COMPAT_CAST(const PyObject*, op)
#endif

// bpo-39573 added Py_SET_TYPE() to Python 3.9.0a4
#if PY_VERSION_HEX < 0x030900A4 && !defined(Py_SET_TYPE)
PYCAPI_COMPAT_STATIC_INLINE(void)
_Py_SET_TYPE(PyObject *ob, PyTypeObject *type)
{
    ob->ob_type = type;
}
#define Py_SET_TYPE(ob, type) _Py_SET_TYPE(_PyObject_CAST(ob), type)
#endif
