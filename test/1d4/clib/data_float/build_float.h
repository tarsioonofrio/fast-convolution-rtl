#ifndef C_BUILD_FLOAT_H
#define C_BUILD_FLOAT_H


const float mct[6*6] = {
	4.0f, 0.0f, -5.0f, 0.0f, 1.0f, 0.0f,
	0.0f, -4.0f, -4.0f, 1.0f, 1.0f, 0.0f,
	0.0f, 4.0f, -4.0f, -1.0f, 1.0f, 0.0f,
	0.0f, -2.0f, -1.0f, 2.0f, 1.0f, 0.0f,
	0.0f, 2.0f, -1.0f, -2.0f, 1.0f, 0.0f,
	0.0f, 4.0f, 0.0f, -5.0f, 0.0f, 1.0f
};
const float mb[6*3] = {
	1.0f, 0.0f, 0.0f,
	1.0f, 1.0f, 1.0f,
	1.0f, -1.0f, 1.0f,
	1.0f, 2.0f, 4.0f,
	1.0f, -2.0f, 4.0f,
	0.0f, 0.0f, 1.0f
};
const float mat[4*6] = {
	1.0f, 1.0f, 1.0f, 1.0f, 1.0f, 0.0f,
	0.0f, 1.0f, -1.0f, 2.0f, -2.0f, 0.0f,
	0.0f, 1.0f, 1.0f, 4.0f, 4.0f, 0.0f,
	0.0f, 1.0f, -1.0f, 8.0f, -8.0f, 1.0f
};
const float mq[6*2] = {
	1.0f, 4.0f,
	-1.0f, 6.0f,
	-1.0f, 6.0f,
	1.0f, 24.0f,
	1.0f, 24.0f,
	1.0f, 1.0f
};

#endif //C_BUILD_FLOAT_H
