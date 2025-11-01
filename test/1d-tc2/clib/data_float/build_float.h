#ifndef C_BUILD_FLOAT_H
#define C_BUILD_FLOAT_H

const float mct[4*4] = {
	-1f, 0f, 1f, 0f,
	0f, 1f, 1f, 0f,
	0f, -1f, 1f, 0f,
	0f, -1f, 0f, 1f
};
const float mb[4*3] = {
	1f, 0f, 0f,
	1f, 1f, 1f,
	1f, -1f, 1f,
	0f, 0f, 1f
};
const float mat[2*4] = {
	1f, 1f, 1f, 0f,
	0f, 1f, -1f, 1f
};
const float mq[4*2] = {
	-1f, 1f,
	1f, 2f,
	1f, 2f,
	1f, 1f
};

#endif //C_BUILD_FLOAT_H
