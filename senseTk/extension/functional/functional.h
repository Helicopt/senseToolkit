#ifndef FUNCTIONAL_H

// TODO:

float intersect(float x1, float y1, float w1, float h1, float x2, float y2, float w2, float h2) {
	float mx1 = std::max(x1, x2);
	float my1 = std::max(y1, y2);
	float mx2 = std::min(x1+w1, x2+w2);
	float my2 = std::min(y1+h1, y2+h2);
	float ix, iy;
	ix = (mx2 > mx1)?(mx2 - mx1):0.;
	iy = (my2 > my1)?(my2 - my1):0.;
	return ix*iy;
}

#endif