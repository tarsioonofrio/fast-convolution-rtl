#include "optim.h"

void matrix_mul_shift_noloop_c2(int *m_out, const int *m_in){
	m_out[0] =  + (m_in[0] << 1);
	m_out[1] =  - m_in[0] - (m_in[1] << 1) + (m_in[2] << 1) - m_in[3] + (m_in[4] << 1);
	m_out[2] =  - (m_in[0] << 1) - m_in[1] - m_in[2] - (m_in[2] << 1) - m_in[4];
	m_out[3] =  + m_in[0] + m_in[1] + m_in[2] + m_in[3] - (m_in[4] << 1);
	m_out[4] =  + m_in[4];
	m_out[5] =  + (m_in[5] << 1);
	m_out[6] =  - m_in[5] - (m_in[6] << 1) + (m_in[7] << 1) - m_in[8] + (m_in[9] << 1);
	m_out[7] =  - (m_in[5] << 1) - m_in[6] - m_in[7] - (m_in[7] << 1) - m_in[9];
	m_out[8] =  + m_in[5] + m_in[6] + m_in[7] + m_in[8] - (m_in[9] << 1);
	m_out[9] =  + m_in[9];
	m_out[10] =  + (m_in[10] << 1);
	m_out[11] =  - m_in[10] - (m_in[11] << 1) + (m_in[12] << 1) - m_in[13] + (m_in[14] << 1);
	m_out[12] =  - (m_in[10] << 1) - m_in[11] - m_in[12] - (m_in[12] << 1) - m_in[14];
	m_out[13] =  + m_in[10] + m_in[11] + m_in[12] + m_in[13] - (m_in[14] << 1);
	m_out[14] =  + m_in[14];
	m_out[15] =  + (m_in[15] << 1);
	m_out[16] =  - m_in[15] - (m_in[16] << 1) + (m_in[17] << 1) - m_in[18] + (m_in[19] << 1);
	m_out[17] =  - (m_in[15] << 1) - m_in[16] - m_in[17] - (m_in[17] << 1) - m_in[19];
	m_out[18] =  + m_in[15] + m_in[16] + m_in[17] + m_in[18] - (m_in[19] << 1);
	m_out[19] =  + m_in[19];
	m_out[20] =  + (m_in[20] << 1);
	m_out[21] =  - m_in[20] - (m_in[21] << 1) + (m_in[22] << 1) - m_in[23] + (m_in[24] << 1);
	m_out[22] =  - (m_in[20] << 1) - m_in[21] - m_in[22] - (m_in[22] << 1) - m_in[24];
	m_out[23] =  + m_in[20] + m_in[21] + m_in[22] + m_in[23] - (m_in[24] << 1);
	m_out[24] =  + m_in[24];
}

void matrix_mul_shift_noloop_c1t(int *m_out, const int *m_in){
	m_out[0] =  + (m_in[0] << 1) - m_in[1] - (m_in[2] << 1) + m_in[3];
	m_out[1] =  - (m_in[1] << 1) - m_in[2] + m_in[3];
	m_out[2] =  + (m_in[1] << 1) - m_in[2] - (m_in[2] << 1) + m_in[3];
	m_out[3] =  - m_in[1] + m_in[3];
	m_out[4] =  + (m_in[1] << 1) - m_in[2] - (m_in[3] << 1) + m_in[4];
	m_out[5] =  + (m_in[5] << 1) - m_in[6] - (m_in[7] << 1) + m_in[8];
	m_out[6] =  - (m_in[6] << 1) - m_in[7] + m_in[8];
	m_out[7] =  + (m_in[6] << 1) - m_in[7] - (m_in[7] << 1) + m_in[8];
	m_out[8] =  - m_in[6] + m_in[8];
	m_out[9] =  + (m_in[6] << 1) - m_in[7] - (m_in[8] << 1) + m_in[9];
	m_out[10] =  + (m_in[10] << 1) - m_in[11] - (m_in[12] << 1) + m_in[13];
	m_out[11] =  - (m_in[11] << 1) - m_in[12] + m_in[13];
	m_out[12] =  + (m_in[11] << 1) - m_in[12] - (m_in[12] << 1) + m_in[13];
	m_out[13] =  - m_in[11] + m_in[13];
	m_out[14] =  + (m_in[11] << 1) - m_in[12] - (m_in[13] << 1) + m_in[14];
	m_out[15] =  + (m_in[15] << 1) - m_in[16] - (m_in[17] << 1) + m_in[18];
	m_out[16] =  - (m_in[16] << 1) - m_in[17] + m_in[18];
	m_out[17] =  + (m_in[16] << 1) - m_in[17] - (m_in[17] << 1) + m_in[18];
	m_out[18] =  - m_in[16] + m_in[18];
	m_out[19] =  + (m_in[16] << 1) - m_in[17] - (m_in[18] << 1) + m_in[19];
	m_out[20] =  + (m_in[20] << 1) - m_in[21] - (m_in[22] << 1) + m_in[23];
	m_out[21] =  - (m_in[21] << 1) - m_in[22] + m_in[23];
	m_out[22] =  + (m_in[21] << 1) - m_in[22] - (m_in[22] << 1) + m_in[23];
	m_out[23] =  - m_in[21] + m_in[23];
	m_out[24] =  + (m_in[21] << 1) - m_in[22] - (m_in[23] << 1) + m_in[24];
}

void matrix_mul_shift_noloop_a2(int *m_out, const int *m_in){
	m_out[0] =  + m_in[0];
	m_out[1] =  + m_in[0] + m_in[1] + m_in[2];
	m_out[2] =  + m_in[0] - m_in[1] + m_in[2];
	m_out[3] =  + m_in[0] + (m_in[1] << 1) + (m_in[2] << 2);
	m_out[4] =  + m_in[2];
	m_out[5] =  + m_in[5];
	m_out[6] =  + m_in[5] + m_in[6] + m_in[7];
	m_out[7] =  + m_in[5] - m_in[6] + m_in[7];
	m_out[8] =  + m_in[5] + (m_in[6] << 1) + (m_in[7] << 2);
	m_out[9] =  + m_in[7];
	m_out[10] =  + m_in[10];
	m_out[11] =  + m_in[10] + m_in[11] + m_in[12];
	m_out[12] =  + m_in[10] - m_in[11] + m_in[12];
	m_out[13] =  + m_in[10] + (m_in[11] << 1) + (m_in[12] << 2);
	m_out[14] =  + m_in[12];
}

void matrix_mul_shift_noloop_a1t(int *m_out, const int *m_in){
	m_out[0] =  + m_in[0] + m_in[1] + m_in[2];
	m_out[1] =  + m_in[1] - m_in[2];
	m_out[2] =  + m_in[1] + m_in[2];
	m_out[3] =  + m_in[3] + m_in[4] + m_in[5];
	m_out[4] =  + m_in[4] - m_in[5];
	m_out[5] =  + m_in[4] + m_in[5];
	m_out[6] =  + m_in[6] + m_in[7] + m_in[8];
	m_out[7] =  + m_in[7] - m_in[8];
	m_out[8] =  + m_in[7] + m_in[8];
}

void hadamart_product_noloop_iter(int *out, const int *in1, const int *in2){
	out[0] = in1[0] * in2[0];
}

