#ifndef C_EXAMPLE_H
#define C_EXAMPLE_H


const int md[5*1] = {
	0,
	1,
	2,
	3,
	4
};
const int mg[3*1] = {
	0,
	1,
	2
};
const int mgg[5*5] = {
	0, 0, 0, 0, 0,
	0, -1, 0, 0, 0,
	0, 0, 0, 0, 0,
	0, 0, 0, 1, 0,
	0, 0, 0, 0, 2
};
const float mggf[5*5] = {
	0.0f, 0.0f, 0.0f, 0.0f, 0.0f,
	0.0f, -1.5f, 0.0f, 0.0f, 0.0f,
	0.0f, 0.0f, -0.16666666666666666f, 0.0f, 0.0f,
	0.0f, 0.0f, 0.0f, 1.6666666666666667f, 0.0f,
	0.0f, 0.0f, 0.0f, 0.0f, 2.0f
};
const int ms_gold[3*1] = {
	5,
	8,
	11
};

#endif //C_EXAMPLE_H
