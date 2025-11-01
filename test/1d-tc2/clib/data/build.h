#ifndef C_BUILD_H
#define C_BUILD_H

const int mct[4*4] = {
	-1, 0, 1, 0,
	0, 1, 1, 0,
	0, -1, 1, 0,
	0, -1, 0, 1
};
const int mb[4*3] = {
	1, 0, 0,
	1, 1, 1,
	1, -1, 1,
	0, 0, 1
};
const int mat[2*4] = {
	1, 1, 1, 0,
	0, 1, -1, 1
};
const int mq[4*2] = {
	-1, 1,
	1, 2,
	1, 2,
	1, 1
};

#endif //C_BUILD_H
