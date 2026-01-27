#ifndef C_BUILD_FLOAT_H
#define C_BUILD_FLOAT_H

const float mct[8*6] = {
	1f, 0f, 0f, 0f, -1f, 0f,
	0f, -1f, 1f, -1f, 1f, 0f,
	0f, 1f, 0f, 1f, 0f, 0f,
	0f, -1f, 1f, -1f, 1f, 0f,
	0f, -1f, -1f, 1f, 1f, 0f,
	0f, 1f, 0f, -1f, 0f, 0f,
	0f, -1f, 1f, 1f, -1f, 0f,
	0f, -1f, 0f, 0f, 0f, 1f
};
const float mb[8*3] = {
	1f, 0f, 0f,
	1f, 0f, 1f,
	1f, 1f, 1f,
	0f, 1f, 0f,
	1f, 0f, -1f,
	1f, 1f, -1f,
	0f, 1f, 0f,
	0f, 0f, 1f
};
const float mat[4*8] = {
	1f, 1f, 1f, 0f, 1f, 1f, 0f, 0f,
	0f, 0f, 1f, 1f, 0f, 1f, 1f, 0f,
	0f, 1f, 1f, 0f, -1f, -1f, 0f, 0f,
	0f, 0f, 1f, 1f, 0f, -1f, -1f, 1f
};
const float mq[8*2] = {
	1f, 1f,
	1f, 2f,
	1f, 2f,
	1f, 2f,
	1f, 2f,
	1f, 2f,
	1f, 2f,
	1f, 1f
};

#endif //C_BUILD_FLOAT_H
