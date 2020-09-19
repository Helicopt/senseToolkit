#include <cstdlib>
#include <cstdio>
#include <cmath>
#include <algorithm>
#include "Python.h"
#include "functional.h"
#include "time.h"

using namespace std;

static PyObject *
_version(PyObject *self, PyObject *args)
{
	PyObject *ret = (PyObject *)Py_BuildValue("s", "senseTookit fast c extension (2018.08.22.0)");
	return ret;
}

static PyObject *
_test(PyObject *self, PyObject *args)
{
	int num;
	int res = PyArg_ParseTuple(args, "i", &num);
	if (!res)
		return NULL;
	PyObject *ret = PyList_New(num);
	for (int i = 0; i < num; ++i)
	{
		PyList_SetItem(ret, i, (PyObject *)Py_BuildValue("i", i + 1));
	}
	return ret;
}

static PyObject *
_sum(PyObject *self, PyObject *args)
{
	PyObject *list = NULL;
	int res = PyArg_ParseTuple(args, "O", &list);
	if (!res)
		return NULL;
	if (!PyList_CheckExact(list))
		return NULL;
	int num = 0;
	int cnt = PyList_Size(list);
	for (int i = 0; i < cnt; ++i)
	{
		int tmp;
		int res = PyArg_Parse(PyList_GetItem(list, i), "i", &tmp);
		if (!res)
			return NULL;
		num += tmp;
	}
	return (PyObject *)Py_BuildValue("i", num);
}

static PyObject *
_fmax(PyObject *self, PyObject *args)
{
	float x, y;
	int res = PyArg_ParseTuple(args, "ff", &x, &y);
	if (!res)
		return NULL;
	return (PyObject *)Py_BuildValue("f", std::max(x, y));
}

static PyObject *
_fmin(PyObject *self, PyObject *args)
{
	float x, y;
	int res = PyArg_ParseTuple(args, "ff", &x, &y);
	if (!res)
		return NULL;
	return (PyObject *)Py_BuildValue("f", std::min(x, y));
}

static PyObject *
_intersect(PyObject *self, PyObject *args)
{
	float x1, y1, w1, h1, x2, y2, w2, h2;
	int res = PyArg_ParseTuple(args, "ffffffff", &x1, &y1, &w1, &h1, &x2, &y2, &w2, &h2);
	if (!res)
		return NULL;
	float ret = intersect(x1, y1, w1, h1, x2, y2, w2, h2);
	return (PyObject *)Py_BuildValue("f", ret);
}

static PyObject *
_area(PyObject *self, PyObject *args)
{
	float x, y;
	int res = PyArg_ParseTuple(args, "ff", &x, &y);
	if (!res)
		return NULL;
	x = std::max(x, 0.f);
	y = std::max(y, 0.f);
	return (PyObject *)Py_BuildValue("f", x * y);
}

static PyObject *
_union(PyObject *self, PyObject *args)
{
	float x1, y1, w1, h1, x2, y2, w2, h2;
	int res = PyArg_ParseTuple(args, "ffffffff", &x1, &y1, &w1, &h1, &x2, &y2, &w2, &h2);
	if (!res)
		return NULL;
	float ret = intersect(x1, y1, w1, h1, x2, y2, w2, h2);
	w1 = std::max(w1, 0.f);
	h1 = std::max(h1, 0.f);
	w2 = std::max(w2, 0.f);
	h2 = std::max(h2, 0.f);
	return (PyObject *)Py_BuildValue("f", (w1 * h1 + w2 * h2 - ret));
}

static PyObject *
_iou(PyObject *self, PyObject *args)
{
	float x1, y1, w1, h1, x2, y2, w2, h2;
	int res = PyArg_ParseTuple(args, "ffffffff", &x1, &y1, &w1, &h1, &x2, &y2, &w2, &h2);
	if (!res)
		return NULL;
	float ret = intersect(x1, y1, w1, h1, x2, y2, w2, h2);
	w1 = std::max(w1, 0.f);
	h1 = std::max(h1, 0.f);
	w2 = std::max(w2, 0.f);
	h2 = std::max(h2, 0.f);
	return (PyObject *)Py_BuildValue("f", ret / (w1 * h1 + w2 * h2 - ret));
}

static PyObject *
_iou_batch(PyObject *self, PyObject *args)
{
	PyObject *dets1, *dets2;
	int res = PyArg_ParseTuple(args, "OO", &dets1, &dets2);
	if (!res)
		return NULL;
	if (!PyList_CheckExact(dets1))
		return NULL;
	if (!PyList_CheckExact(dets2))
		return NULL;
	int cnt = PyList_Size(dets1);
	if (PyList_Size(dets2) != cnt)
		return NULL;
	PyObject *ret_list = PyList_New(cnt);
	if (cnt == 0)
		return ret_list;
	char *x1s = (char *)"_x1";
	char *y1s = (char *)"_y1";
	char *ws = (char *)"_w";
	char *hs = (char *)"_h";
	// long long be = time(0);
	for (int i = 0; i < cnt; ++i)
	{
		PyObject *d1 = PyList_GetItem(dets1, i);
		PyObject *d2 = PyList_GetItem(dets2, i);
		int res;
		float x1_;
		PyObject *k = PyObject_GetAttrString(d1, x1s);
		res = PyArg_Parse(k, "f", &x1_);
		if (!res)
			return NULL;
		float x2_;
		PyObject *q = PyObject_GetAttrString(d2, x1s);
		res = PyArg_Parse(q, "f", &x2_);
		if (!res)
			return NULL;
		float y1_;
		PyObject *k_ = PyObject_GetAttrString(d1, y1s);
		res = PyArg_Parse(k_, "f", &y1_);
		if (!res)
			return NULL;
		float y2_;
		PyObject *q_ = PyObject_GetAttrString(d2, y1s);
		res = PyArg_Parse(q_, "f", &y2_);
		if (!res)
			return NULL;
		// printf("%lld\n", k_ - k);
		// printf("%lld\n", q_ - q);
		float w1_;
		res = PyArg_Parse(PyObject_GetAttrString(d1, ws), "f", &w1_);
		if (!res)
			return NULL;
		float w2_;
		res = PyArg_Parse(PyObject_GetAttrString(d2, ws), "f", &w2_);
		if (!res)
			return NULL;
		float h1_;
		res = PyArg_Parse(PyObject_GetAttrString(d1, hs), "f", &h1_);
		if (!res)
			return NULL;
		float h2_;
		res = PyArg_Parse(PyObject_GetAttrString(d2, hs), "f", &h2_);
		if (!res)
			return NULL;
		float ret = intersect(x1_, y1_, w1_, h1_, x2_, y2_, w2_, h2_);
		ret = ret / (w1_ * h1_ + w2_ * h2_ - ret);
		PyList_SetItem(ret_list, i, (PyObject *)Py_BuildValue("f", ret));
	}
	// long long en = time(0);
	// printf("%lld\n", en - be);
	return ret_list;
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
		{"c_iou_batch", _iou_batch, METH_VARARGS},
		{NULL, NULL}};

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
	NULL};

#endif

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC
PyInit_functional(void)
{
	PyObject *module = PyModule_Create(&moduledef);
	return module;
#else
PyMODINIT_FUNC initfunctional()
{
	Py_InitModule("functional", extMethods);
#endif
}
