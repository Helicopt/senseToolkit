#include <cstdlib>
#include <cstdio>
#include <cmath>
#include <algorithm>
#include "Python.h"
#include "functional.h"

using namespace std;


static PyObject *
_version(PyObject * self, PyObject * args) {
	PyObject * ret = (PyObject*)Py_BuildValue("s", "senseTookit fast c extension (2018.08.22.0)");
	return ret;	
}

static PyObject *
_test(PyObject * self, PyObject * args) {
	int num;
	int res = PyArg_ParseTuple(args, "i", &num);
	if (!res) return NULL;
	PyObject * ret = PyList_New(num);
	for (int i=0;i<num;++i) {
		PyList_SetItem(ret,i,(PyObject*)Py_BuildValue("i", i+1));
	}
	return ret;
}

static PyObject *
_sum(PyObject * self, PyObject * args) {
	PyObject * list = NULL;
	int res = PyArg_ParseTuple(args, "O", &list);
	if (!res) return NULL;
	if (!PyList_CheckExact(list)) return NULL;
	int num = 0;
	int cnt = PyList_Size(list);
	for (int i=0;i<cnt;++i) {
		int tmp;
		int res=PyArg_Parse(PyList_GetItem(list,i),"i",&tmp);
		if (!res) return NULL;
		num+=tmp;
	}
	return (PyObject*)Py_BuildValue("i", num);
}

static PyObject *
_fmax(PyObject * self, PyObject * args) {
	float x, y;
	int res = PyArg_ParseTuple(args, "ff", &x, &y);
	if (!res) return NULL;
	return (PyObject*)Py_BuildValue("f", std::max(x, y));
}

static PyObject *
_fmin(PyObject * self, PyObject * args) {
	float x, y;
	int res = PyArg_ParseTuple(args, "ff", &x, &y);
	if (!res) return NULL;
	return (PyObject*)Py_BuildValue("f", std::min(x, y));
}

static PyObject *
_intersect(PyObject * self, PyObject * args) {
	float x1, y1, w1, h1, x2, y2, w2, h2;
	int res = PyArg_ParseTuple(args, "ffffffff", &x1, &y1, &w1, &h1, &x2, &y2, &w2, &h2);
	if (!res) return NULL;
	float ret = intersect(x1, y1, w1, h1, x2, y2, w2, h2);
	return (PyObject*)Py_BuildValue("f", ret);
}

static PyObject *
_area(PyObject * self, PyObject * args) {
	float x, y;
	int res = PyArg_ParseTuple(args, "ff", &x, &y);
	if (!res) return NULL;
	x = std::max(x, 0.f);
	y = std::max(y, 0.f);
	return (PyObject*)Py_BuildValue("f", x*y);
}

static PyObject *
_union(PyObject * self, PyObject * args) {
	float x1, y1, w1, h1, x2, y2, w2, h2;
	int res = PyArg_ParseTuple(args, "ffffffff", &x1, &y1, &w1, &h1, &x2, &y2, &w2, &h2);
	if (!res) return NULL;
	float ret = intersect(x1, y1, w1, h1, x2, y2, w2, h2);
	w1 = std::max(w1, 0.f);
	h1 = std::max(h1, 0.f);
	w2 = std::max(w2, 0.f);
	h2 = std::max(h2, 0.f);
	return (PyObject*)Py_BuildValue("f", (w1*h1+w2*h2-ret));
}

static PyObject *
_iou(PyObject * self, PyObject * args) {
	float x1, y1, w1, h1, x2, y2, w2, h2;
	int res = PyArg_ParseTuple(args, "ffffffff", &x1, &y1, &w1, &h1, &x2, &y2, &w2, &h2);
	if (!res) return NULL;
	float ret = intersect(x1, y1, w1, h1, x2, y2, w2, h2);
	w1 = std::max(w1, 0.f);
	h1 = std::max(h1, 0.f);
	w2 = std::max(w2, 0.f);
	h2 = std::max(h2, 0.f);
	return (PyObject*)Py_BuildValue("f", ret / (w1*h1+w2*h2-ret));
}

static PyMethodDef
extMethods[] = {
	{"c_version", _version, METH_VARARGS},
	{"c_test", _test, METH_VARARGS},
	{"c_sum", _sum, METH_VARARGS},
	{"c_fmax", _fmax, METH_VARARGS},
	{"c_fmin", _fmin, METH_VARARGS},
	{"c_intersection", _intersect, METH_VARARGS},
	{"c_area", _area, METH_VARARGS},
	{"c_union", _union, METH_VARARGS},
	{"c_iou", _iou, METH_VARARGS},
	{NULL, NULL}
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "functional",
        NULL,
        -1,
        extMethods,
        NULL,
        NULL,
        NULL,
        NULL
};

#endif

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC
PyInit_functional(void) {
    PyObject *module = PyModule_Create(&moduledef);
	return module;
#else
PyMODINIT_FUNC initfunctional() {
	Py_InitModule("functional", extMethods);
#endif
}
