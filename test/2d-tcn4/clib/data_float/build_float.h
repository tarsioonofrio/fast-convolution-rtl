#ifndef C_BUILD_FLOAT_H
#define C_BUILD_FLOAT_H

const float mc1t[4*4] = {
	-1f, 0f, 1f, 0f,
	0f, 1f, 1f, 0f,
	0f, -1f, 1f, 0f,
	0f, -1f, 0f, 1f
};
const float mb1[4*3] = {
	1f, 0f, 0f,
	1f, 1f, 1f,
	1f, -1f, 1f,
	0f, 0f, 1f
};
const float ma1t[2*4] = {
	1f, 1f, 1f, 0f,
	0f, 1f, -1f, 1f
};
const float mq1[4*2] = {
	-1f, 1f,
	1f, 2f,
	1f, 2f,
	1f, 1f
};
const float mc2t[4*4] = {
	-1f, 0f, 1f, 0f,
	0f, 1f, 1f, 0f,
	0f, -1f, 1f, 0f,
	0f, -1f, 0f, 1f
};
const float mb2[4*3] = {
	1f, 0f, 0f,
	1f, 1f, 1f,
	1f, -1f, 1f,
	0f, 0f, 1f
};
const float ma2t[2*4] = {
	1f, 1f, 1f, 0f,
	0f, 1f, -1f, 1f
};
const float mc2[4*4] = {
	-1f, 0f, 0f, 0f,
	0f, 1f, -1f, -1f,
	1f, 1f, 1f, 0f,
	0f, 0f, 0f, 1f
};
const float ma2[4*2] = {
	1f, 0f,
	1f, 1f,
	1f, -1f,
	0f, 1f
};
const float mq2[4*2] = {
	-1f, 1f,
	1f, 2f,
	1f, 2f,
	1f, 1f
};

#endif //C_BUILD_FLOAT_H
