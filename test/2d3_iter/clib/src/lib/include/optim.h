#ifndef C_OPTIM_ITER_H
#define C_OPTIM_ITER_H

void matrix_mul_shift_noloop_c2(int *m_out, const int *m_in);

void matrix_mul_shift_noloop_c1t(int *m_out, const int *m_in);

void matrix_mul_shift_noloop_a2(int *m_out, const int *m_in);

void matrix_mul_shift_noloop_a1t(int *m_out, const int *m_in);

void hadamart_product_noloop_iter(int *out, const int *in1, const int *in2);

#endif //C_OPTIM_ITER_H