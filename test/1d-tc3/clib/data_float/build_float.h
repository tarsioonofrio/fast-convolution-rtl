#ifndef C_BUILD_FLOAT_H
#define C_BUILD_FLOAT_H

const float mct[5*5] = {
	2f, -1f, -2f, 1f, 0f,
	0f, -2f, -1f, 1f, 0f,
	0f, 2f, -3f, 1f, 0f,
	0f, -1f, 0f, 1f, 0f,
	0f, 2f, -1f, -2f, 1f
};
const float mb[5*3] = {
	1f, 0f, 0f,
	1f, 1f, 1f,
	1f, -1f, 1f,
	1f, 2f, 4f,
	0f, 0f, 1f
};
const float mat[3*5] = {
	1f, 1f, 1f, 1f, 0f,
	0f, 1f, -1f, 2f, 0f,
	0f, 1f, 1f, 4f, 1f
};
const float mq[5*2] = {
	1f, 2f,
	-1f, 2f,
	-1f, 6f,
	1f, 6f,
	1f, 1f
};

#endif //C_BUILD_FLOAT_H
