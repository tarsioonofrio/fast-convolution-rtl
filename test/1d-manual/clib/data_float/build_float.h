#ifndef C_BUILD_FLOAT_H
#define C_BUILD_FLOAT_H


const float mct[6*5] = {
	1.0f, -1.0f, -1.0f, 0.0f, 0.0f,
	0.0f, -1.0f, 1.0f, -1.0f, 0.0f,
	0.0f, 0.0f, -1.0f, -1.0f, 1.0f,
	0.0f, 1.0f, 0.0f, 0.0f, 0.0f,
	0.0f, 0.0f, 1.0f, 0.0f, 0.0f,
	0.0f, 0.0f, 0.0f, 1.0f, 0.0f
};
const float mb[6*3] = {
	1.0f, 0.0f, 0.0f,
	0.0f, 1.0f, 0.0f,
	0.0f, 0.0f, 1.0f,
	1.0f, 1.0f, 0.0f,
	1.0f, 0.0f, 1.0f,
	0.0f, 1.0f, 1.0f
};
const float mat[3*6] = {
	1.0f, 0.0f, 0.0f, 1.0f, 1.0f, 0.0f,
	0.0f, 1.0f, 0.0f, 1.0f, 0.0f, 1.0f,
	0.0f, 0.0f, 1.0f, 0.0f, 1.0f, 1.0f
};
const float mq[6*2] = {
	1.0f, 1.0f,
	1.0f, 1.0f,
	1.0f, 1.0f,
	1.0f, 1.0f,
	1.0f, 1.0f,
	1.0f, 1.0f
};

#endif //C_BUILD_FLOAT_H
