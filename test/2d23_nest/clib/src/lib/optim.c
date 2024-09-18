#include "optim.h"

void matrix_mul_shift_noloop_a(int *m_out, const int *m_in){
	m_out[0] =  + m_in[0] + m_in[1] + m_in[2] + m_in[3] + m_in[5] + m_in[6] + m_in[7] + m_in[8] + m_in[10] + m_in[11] + m_in[12] + m_in[13];
	m_out[1] =  + m_in[1] - m_in[2] + (m_in[3] << 1) + m_in[6] - m_in[7] + (m_in[8] << 1) + m_in[11] - m_in[12] + (m_in[13] << 1);
	m_out[2] =  + m_in[1] + m_in[2] + (m_in[3] << 2) + m_in[4] + m_in[6] + m_in[7] + (m_in[8] << 2) + m_in[9] + m_in[11] + m_in[12] + (m_in[13] << 2) + m_in[14];
	m_out[3] =  + m_in[5] + m_in[6] + m_in[7] + m_in[8] - m_in[10] - m_in[11] - m_in[12] - m_in[13] + m_in[15] + m_in[16] + m_in[17] + m_in[18];
	m_out[4] =  + m_in[6] - m_in[7] + (m_in[8] << 1) - m_in[11] + m_in[12] - (m_in[13] << 1) + m_in[16] - m_in[17] + (m_in[18] << 1);
	m_out[5] =  + m_in[6] + m_in[7] + (m_in[8] << 2) + m_in[9] - m_in[11] - m_in[12] - (m_in[13] << 2) - m_in[14] + m_in[16] + m_in[17] + (m_in[18] << 2) + m_in[19];
}

void matrix_mul_shift_noloop_c(int *m_out, const int *m_in){
	m_out[0] =  - (m_in[0] << 1) + m_in[1] + (m_in[2] << 1) - m_in[3] + (m_in[10] << 1) - m_in[11] - (m_in[12] << 1) + m_in[13];
	m_out[1] =  + (m_in[1] << 1) + m_in[2] - m_in[3] - (m_in[11] << 1) - m_in[12] + m_in[13];
	m_out[2] =  - (m_in[1] << 1) + m_in[2] + (m_in[2] << 1) - m_in[3] + (m_in[11] << 1) - m_in[12] - (m_in[12] << 1) + m_in[13];
	m_out[3] =  + m_in[1] - m_in[3] - m_in[11] + m_in[13];
	m_out[4] =  - (m_in[1] << 1) + m_in[2] + (m_in[3] << 1) - m_in[4] + (m_in[11] << 1) - m_in[12] - (m_in[13] << 1) + m_in[14];
	m_out[5] =  + (m_in[5] << 1) - m_in[6] - (m_in[7] << 1) + m_in[8] + (m_in[10] << 1) - m_in[11] - (m_in[12] << 1) + m_in[13];
	m_out[6] =  - (m_in[6] << 1) - m_in[7] + m_in[8] - (m_in[11] << 1) - m_in[12] + m_in[13];
	m_out[7] =  + (m_in[6] << 1) - m_in[7] - (m_in[7] << 1) + m_in[8] + (m_in[11] << 1) - m_in[12] - (m_in[12] << 1) + m_in[13];
	m_out[8] =  - m_in[6] + m_in[8] - m_in[11] + m_in[13];
	m_out[9] =  + (m_in[6] << 1) - m_in[7] - (m_in[8] << 1) + m_in[9] + (m_in[11] << 1) - m_in[12] - (m_in[13] << 1) + m_in[14];
	m_out[10] =  - (m_in[5] << 1) + m_in[6] + (m_in[7] << 1) - m_in[8] + (m_in[10] << 1) - m_in[11] - (m_in[12] << 1) + m_in[13];
	m_out[11] =  + (m_in[6] << 1) + m_in[7] - m_in[8] - (m_in[11] << 1) - m_in[12] + m_in[13];
	m_out[12] =  - (m_in[6] << 1) + m_in[7] + (m_in[7] << 1) - m_in[8] + (m_in[11] << 1) - m_in[12] - (m_in[12] << 1) + m_in[13];
	m_out[13] =  + m_in[6] - m_in[8] - m_in[11] + m_in[13];
	m_out[14] =  - (m_in[6] << 1) + m_in[7] + (m_in[8] << 1) - m_in[9] + (m_in[11] << 1) - m_in[12] - (m_in[13] << 1) + m_in[14];
	m_out[15] =  - (m_in[5] << 1) + m_in[6] + (m_in[7] << 1) - m_in[8] + (m_in[15] << 1) - m_in[16] - (m_in[17] << 1) + m_in[18];
	m_out[16] =  + (m_in[6] << 1) + m_in[7] - m_in[8] - (m_in[16] << 1) - m_in[17] + m_in[18];
	m_out[17] =  - (m_in[6] << 1) + m_in[7] + (m_in[7] << 1) - m_in[8] + (m_in[16] << 1) - m_in[17] - (m_in[17] << 1) + m_in[18];
	m_out[18] =  + m_in[6] - m_in[8] - m_in[16] + m_in[18];
	m_out[19] =  - (m_in[6] << 1) + m_in[7] + (m_in[8] << 1) - m_in[9] + (m_in[16] << 1) - m_in[17] - (m_in[18] << 1) + m_in[19];
}

void hadamart_product_noloop(int *out, const int *in1, const int *in2){
	out[0] = in1[0] * in2[0];
	out[1] = in1[1] * in2[1];
	out[2] = in1[2] * in2[2];
	out[3] = in1[3] * in2[3];
	out[4] = in1[4] * in2[4];
	out[5] = in1[5] * in2[5];
	out[6] = in1[6] * in2[6];
	out[7] = in1[7] * in2[7];
	out[8] = in1[8] * in2[8];
	out[9] = in1[9] * in2[9];
	out[10] = in1[10] * in2[10];
	out[11] = in1[11] * in2[11];
	out[12] = in1[12] * in2[12];
	out[13] = in1[13] * in2[13];
	out[14] = in1[14] * in2[14];
	out[15] = in1[15] * in2[15];
	out[16] = in1[16] * in2[16];
	out[17] = in1[17] * in2[17];
	out[18] = in1[18] * in2[18];
	out[19] = in1[19] * in2[19];
}

