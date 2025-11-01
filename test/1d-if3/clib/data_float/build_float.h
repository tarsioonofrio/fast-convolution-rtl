#ifndef C_BUILD_FLOAT_H
#define C_BUILD_FLOAT_H

const float mct[6*5] = {
	1f, -1f, -1f, 0f, 0f,
	0f, -1f, 1f, -1f, 0f,
	0f, 0f, -1f, -1f, 1f,
	0f, 1f, 0f, 0f, 0f,
	0f, 0f, 1f, 0f, 0f,
	0f, 0f, 0f, 1f, 0f
};
const float mb[6*3] = {
	1f, 0f, 0f,
	0f, 1f, 0f,
	0f, 0f, 1f,
	1f, 1f, 0f,
	1f, 0f, 1f,
	0f, 1f, 1f
};
const float mat[3*6] = {
	1f, 0f, 0f, 1f, 1f, 0f,
	0f, 1f, 0f, 1f, 0f, 1f,
	0f, 0f, 1f, 0f, 1f, 1f
};
const float mq[6*2] = {
	1f, 1f,
	1f, 1f,
	1f, 1f,
	1f, 1f,
	1f, 1f,
	1f, 1f
};

#endif //C_BUILD_FLOAT_H
