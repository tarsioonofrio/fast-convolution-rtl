#ifndef C_BUILD_FLOAT_H
#define C_BUILD_FLOAT_H

const float mct[6*6] = {
	4f, 0f, -5f, 0f, 1f, 0f,
	0f, -4f, -4f, 1f, 1f, 0f,
	0f, 4f, -4f, -1f, 1f, 0f,
	0f, -2f, -1f, 2f, 1f, 0f,
	0f, 2f, -1f, -2f, 1f, 0f,
	0f, 4f, 0f, -5f, 0f, 1f
};
const float mb[6*3] = {
	1f, 0f, 0f,
	1f, 1f, 1f,
	1f, -1f, 1f,
	1f, 2f, 4f,
	1f, -2f, 4f,
	0f, 0f, 1f
};
const float mat[4*6] = {
	1f, 1f, 1f, 1f, 1f, 0f,
	0f, 1f, -1f, 2f, -2f, 0f,
	0f, 1f, 1f, 4f, 4f, 0f,
	0f, 1f, -1f, 8f, -8f, 1f
};
const float mq[6*2] = {
	1f, 4f,
	-1f, 6f,
	-1f, 6f,
	1f, 24f,
	1f, 24f,
	1f, 1f
};

#endif //C_BUILD_FLOAT_H
