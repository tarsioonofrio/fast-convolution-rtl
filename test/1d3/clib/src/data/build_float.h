#ifndef C_BUILD_FLOAT_H
#define C_BUILD_FLOAT_H


const float mct[5*5] = {
	2.0f, -1.0f, -2.0f, 1.0f, 0.0f,
	0.0f, -2.0f, -1.0f, 1.0f, 0.0f,
	0.0f, 2.0f, -3.0f, 1.0f, 0.0f,
	0.0f, -1.0f, 0.0f, 1.0f, 0.0f,
	0.0f, 2.0f, -1.0f, -2.0f, 1.0f
};
const float mb[5*3] = {
	1.0f, 0.0f, 0.0f,
	1.0f, 1.0f, 1.0f,
	1.0f, -1.0f, 1.0f,
	1.0f, 2.0f, 4.0f,
	0.0f, 0.0f, 1.0f
};
const float mat[3*5] = {
	1.0f, 1.0f, 1.0f, 1.0f, 0.0f,
	0.0f, 1.0f, -1.0f, 2.0f, 0.0f,
	0.0f, 1.0f, 1.0f, 4.0f, 1.0f
};
const float mq[5*2] = {
	1.0f, 2.0f,
	-1.0f, 2.0f,
	-1.0f, 6.0f,
	1.0f, 6.0f,
	1.0f, 1.0f
};

#endif //C_BUILD_FLOAT_H
