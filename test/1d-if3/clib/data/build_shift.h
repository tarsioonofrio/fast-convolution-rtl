#ifndef C_BUILD_SHIFT_H
#define C_BUILD_SHIFT_H

#define AP_SIZE 0
#define AN_SIZE 0
#define CP_SIZE 0
#define CN_SIZE 0

const int map[3*6] = {
	1, 0, 0, 1, 1, 0,
	0, 1, 0, 1, 0, 1,
	0, 0, 1, 0, 1, 1
};
const int man[3*6] = {
	0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0
};
const int mcp[6*5] = {
	1, 0, 0, 0, 0,
	0, 0, 1, 0, 0,
	0, 0, 0, 0, 1,
	0, 1, 0, 0, 0,
	0, 0, 1, 0, 0,
	0, 0, 0, 1, 0
};
const int mcn[6*5] = {
	0, 1, 1, 0, 0,
	0, 1, 0, 1, 0,
	0, 0, 1, 1, 0,
	0, 0, 0, 0, 0,
	0, 0, 0, 0, 0,
	0, 0, 0, 0, 0
};

#endif //C_BUILD_SHIFT_H
