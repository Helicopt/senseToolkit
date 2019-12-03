#include<boost/python.hpp>
#include <cstdlib>
#include <cstdio>
#include <cmath>
#include <algorithm>

#include "functional.h"
#include "time.h"

using namespace boost::python;
using namespace std;

namespace boost_functional {

    class cDet {
    public:
        cDet(){type = eval("float");}
        cDet(float x, float y, float w, float h): x(x), y(y), w(w), h(h)
        {
            type = eval("float");
        }
        float _intersection(const cDet & o) const {
            return intersect(x, y, w, h, o.x, o.y, o.w, o.h);
        }
        float _area() const {
            return max(w, 0.f) * max(h, 0.f);
        }
        float _union(const cDet & o) const {
            float i = intersect(x, y, w, h, o.x, o.y, o.w, o.h);
            float a1 = _area();
            float a2 = o._area();
            return a1 + a2 - i;
        }
        float _iou(const cDet & o) const {
            float i = intersect(x, y, w, h, o.x, o.y, o.w, o.h);
            float a1 = _area();
            float a2 = o._area();
            return i / (a1 + a2 - i);
        }
        void _trim(const int w_, const int h_) {
            float x1 = x;
            float y1 = y;
            x = max(x, 0.f);
            y = max(y, 0.f);
            float x2 = min((float)w_, x1 + w);
            float y2 = min((float)h_, y1 + h);
            w = max(x2 - x, 0.f);
            h = max(y2 - y, 0.f);
        }
        object get_x1 () const {
            return  type(x);
        }
        object get_y1 () const {
            return  type(y);
        }
        object get_x2 () const {
            return  type(x+w);
        }
        object get_y2 () const {
            return  type(y+h);
        }
        object get_w  () const {
            return  type(w);
        }
        object get_h  () const {
            return  type(h);
        }
        object get_cx () const {
            return  type(x+w/2);
        }
        object get_cy () const {
            return  type(y+h/2);
        }
        void set_x1 (object v) {
            x = extract<float>(v);
        }
        void set_y1 (object v) {
            y = extract<float>(v);
        }
        void set_x2 (object v) {
            w = extract<float>(v) - x;
        }
        void set_y2 (object v) {
            h = extract<float>(v) - y;
        }
        void set_w  (object v) {
            w = extract<float>(v);
        }
        void set_h  (object v) {
            h = extract<float>(v);
        }
        void set_cx (object v) {
            x = extract<float>(v) - w/2;
        }
        void set_cy (object v) {
            y = extract<float>(v) - h/2;
        }
        object get_type() const {
            return type;
        }
        void set_type(object v) {
            type = v;
        }
    private:
        float x, y, w, h;
        object type;
    };


    struct cDet_picle_suite : pickle_suite {
        static tuple getinitargs(const cDet& v) {
            return make_tuple(v.get_x1(), v.get_y1(), v.get_w(), v.get_h());
        }
        static tuple getstate(object v) {
            cDet const &v_ = extract<cDet const&>(v);
            return make_tuple(v.attr("__dict__"), v_.get_type());
        }
        static void setstate(object v, tuple state) {
            cDet& v_ = extract<cDet&>(v);
            if (len(state)!=2) {
                PyErr_SetObject(PyExc_ValueError, ("expected 2-item tuple, got %s"%state).ptr());
                throw_error_already_set();
            }
            dict d = extract<dict>(v.attr("__dict__"));
            d.update(state[0]);

            object dtype = state[1];
            v_.set_type(dtype);
        }
        static bool getstate_manages_dict() {return true;}
    };


    str version() {
        return "senseTookit boost c extension (2019.12.02.0)";
    };

    object iou_batch(object adets, object bdets) {
        object& al = adets;
        object& bl = bdets;
        list ret; 
        ssize_t cnt = extract<ssize_t>(al.attr("__len__")());
        if (extract<ssize_t>(al.attr("__len__")())!=cnt) {
            return ret;
        }
        for (ssize_t i = 0; i < cnt; ++i) {
            cDet& a = extract<cDet&>(al[i]);
            cDet& b = extract<cDet&>(bl[i]);
            ret.append(a._iou(b));
        }
        return ret;
    };

    object test(int x) {
        list ret;
        for (int i=0;i<x;++i)
            ret.append(i+1);
        return ret;
    }

    object c_sum(object x) {
        object ret(0);
        ssize_t cnt = extract<ssize_t>(x.attr("__len__")());
        for (int i=0;i<cnt;++i)
            ret+=x[i];
        return ret;
    }

    object expr(object x, object y) {
        return y(x);
    }
}



BOOST_PYTHON_MODULE(boost_functional)
{
    using namespace boost_functional;
    class_<cDet>("cDet", init<>())
        .add_property("x1", &cDet::get_x1, &cDet::set_x1)
        .add_property("y1", &cDet::get_y1, &cDet::set_y1)
        .add_property("x2", &cDet::get_x2, &cDet::set_x2)
        .add_property("y2", &cDet::get_y2, &cDet::set_y2)
        .add_property( "w", &cDet::get_w , &cDet::set_w )
        .add_property( "h", &cDet::get_h , &cDet::set_h )
        .add_property("cx", &cDet::get_cx, &cDet::set_cx)
        .add_property("cy", &cDet::get_cy, &cDet::set_cy)
        .add_property("dtype", &cDet::get_type)
        .def(init<float, float, float, float>())
        .def("intersection", &cDet::_intersection)
        .def("area", &cDet::_area)
        .def("iou", &cDet::_iou)
        .def("union", &cDet::_union)
        .def("_trim", &cDet::_trim)
        .def("_astype", &cDet::set_type)

        .def_pickle(cDet_picle_suite())
    ;
    def("c_version", version);
    def("c_test", test);
    def("c_sum", c_sum);
    def("c_iou_batch", iou_batch);
    def("c_expr", expr);
}