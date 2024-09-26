#include "optim.h"

void matrix_mul_shift_noloop_a(int *m_out, const int *m_in){
	m_out[0] =  + m_in[0] + m_in[1] + m_in[2];
	m_out[1] =  + m_in[1] - m_in[2] + m_in[3];
}

void matrix_mul_shift_noloop_c(int *m_out, const int *m_in){
	m_out[0] =  - m_in[0] + m_in[2];
	m_out[1] =  + m_in[1] + m_in[2];
	m_out[2] =  - m_in[1] + m_in[2];
	m_out[3] =  - m_in[1] + m_in[3];
}

void hadamart_product_noloop(int *out, const int *in1, const int *in2){
	out[0] = in1[0] * in2[0];
	out[1] = in1[1] * in2[1];
	out[2] = in1[2] * in2[2];
	out[3] = in1[3] * in2[3];
}

