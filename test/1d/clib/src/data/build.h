#ifndef C_BUILD_H
#define C_BUILD_H


const int mct[5*5] = {
	2, -1, -2, 1, 0,
	0, -2, -1, 1, 0,
	0, 2, -3, 1, 0,
	0, -1, 0, 1, 0,
	0, 2, -1, -2, 1
};
const int mb[5*3] = {
	1, 0, 0,
	1, 1, 1,
	1, -1, 1,
	1, 2, 4,
	0, 0, 1
};
const int mat[3*5] = {
	1, 1, 1, 1, 0,
	0, 1, -1, 2, 0,
	0, 1, 1, 4, 1
};
const int mq[5*2] = {
	1, 2,
	-1, 2,
	-1, 6,
	1, 6,
	1, 1
};

#endif //C_BUILD_H
