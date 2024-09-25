#ifndef C_OPTIM_H
#define C_OPTIM_H

void matrix_mul_shift_noloop_a(int *m_out, const int *m_in);

void matrix_mul_shift_noloop_c(int *m_out, const int *m_in);

void hadamart_product_noloop(int *out, const int *in1, const int *in2);

#endif //C_OPTIM_H