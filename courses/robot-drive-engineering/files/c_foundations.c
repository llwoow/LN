#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <math.h>
bool adc_to_amp(uint16_t raw, double *amp) {
    if (amp == NULL || raw > 4095u) return false;
    int32_t centred = (int32_t)raw - 2048;
    *amp = (double)centred * (3.3 / 4096.0) / 0.1;
    return true;
}
bool mean_code(const uint16_t *raw, size_t n, double *out) {
    if (raw == NULL || out == NULL || n == 0 || n > 1000) return false;
    uint32_t total = 0;
    for (size_t k=0; k<n; ++k) {
        if (raw[k] > 4095u) return false;
        total += raw[k];
    }
    *out = (double)total / (double)n;
    return true;
}
int main(void) {
    double a=99;
    assert(adc_to_amp(1924,&a) && fabs(a+0.9990234375)<1e-12);
    assert(adc_to_amp(2048,&a) && a==0);
    assert(!adc_to_amp(5000,&a) && a==0);
    assert(!adc_to_amp(2048,NULL));
    uint16_t full[1000]; for(size_t k=0;k<1000;++k)full[k]=4095u;
    assert(mean_code(full,1000,&a)&&a==4095.0);
    assert(!mean_code(full,0,&a));
    assert(1/2==0 && 1.0/2.0==0.5);
    puts("Host-only C conversion, pointer, range and accumulator checks passed.");
}
