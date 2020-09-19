#include <cstdlib>
#include <cstdio>
#include "Python.h"
#include "flow.h"

static PyObject *
_version(PyObject *self, PyObject *args)
{
	PyObject *ret = (PyObject *)Py_BuildValue("s", "tracking association module version: 0.5(initial) 1.0(2018-01-09), code by toka");
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
_createFlow(PyObject *self, PyObject *args)
{
	int id;
	int res = PyArg_ParseTuple(args, "i", &id);
	if (!res)
		return NULL;
	return (PyObject *)Py_BuildValue("i", createFlow(id));
}

static PyObject *
_release(PyObject *self, PyObject *args)
{
	int id;
	int res = PyArg_ParseTuple(args, "i", &id);
	if (!res)
		return NULL;
	release(id);
	return (PyObject *)Py_BuildValue("");
}

static PyObject *
_printParam(PyObject *self, PyObject *args)
{
	int id;
	int res = PyArg_ParseTuple(args, "i", &id);
	if (!res)
		return NULL;
	printParam(id);
	return (PyObject *)Py_BuildValue("");
}

static PyObject *
_clear(PyObject *self, PyObject *args)
{
	int id;
	int res = PyArg_ParseTuple(args, "i", &id);
	if (!res)
		return NULL;
	clear(id);
	return (PyObject *)Py_BuildValue("");
}

static PyObject *
_setNodes(PyObject *self, PyObject *args)
{
	int id, num1, num2, num3 = -1;
	int res = PyArg_ParseTuple(args, "iii|i", &id, &num1, &num2, &num3);
	if (!res)
		return NULL;
	if (num3 == -1)
		setNodes(id, num1, num2);
	else
		setNodes(id, num1, num2, num3);
	return (PyObject *)Py_BuildValue("");
}

static PyObject *
_setThr(PyObject *self, PyObject *args)
{
	int id, num;
	int res = PyArg_ParseTuple(args, "ii", &id, &num);
	if (!res)
		return NULL;
	setThr(id, num);
	return (PyObject *)Py_BuildValue("");
}

static PyObject *
_addEdge(PyObject *self, PyObject *args)
{
	int id, a, b, c, f = 1;
	int res = PyArg_ParseTuple(args, "iiii|i", &id, &a, &b, &c, &f);
	if (!res)
		return NULL;
	return (PyObject *)Py_BuildValue("i", addEdge(id, a, b, c, f));
}

static PyObject *
_flow(PyObject *self, PyObject *args)
{
	int id;
	int res = PyArg_ParseTuple(args, "i", &id);
	if (!res)
		return NULL;
	const std::vector<int> &mat = flow(id);
	size_t num = mat.size();
	PyObject *ret = PyList_New(num);
	for (size_t i = 0; i < num; ++i)
	{
		PyList_SetItem(ret, i, (PyObject *)Py_BuildValue("i", mat[i]));
	}
	return ret;
}

static PyMethodDef
	extMethods[] = {
		{"version", _version, METH_VARARGS},
		{"test", _test, METH_VARARGS},
		{"sum", _sum, METH_VARARGS},
		{"createFlow", _createFlow, METH_VARARGS},
		{"release", _release, METH_VARARGS},
		{"setNodes", _setNodes, METH_VARARGS},
		{"addEdge", _addEdge, METH_VARARGS},
		{"setThr", _setThr, METH_VARARGS},
		{"clear", _clear, METH_VARARGS},
		{"flow", _flow, METH_VARARGS},
		{"printParam", _printParam, METH_VARARGS},
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
PyInit_flow(void)
{
	PyObject *module = PyModule_Create(&moduledef);
	return module;
#else
PyMODINIT_FUNC initflow()
{
	Py_InitModule("flow", extMethods);
#endif
}
