/* LN original deterministic interleaving demonstration. Host C11, no threads/ISR.
 * The call labeled ISR makes the hypothetical preemption order explicit, so no
 * data race or assumed compiler-specific interrupt behavior is used in this test.
 */
#include <assert.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
struct Sample { uint32_t number; int32_t current_ma; };
static struct Sample latest;
static void simulated_isr(void) { latest.number=101; latest.current_ma=3000; }
int main(void) {
    latest=(struct Sample){100,2000};
    struct Sample mixed;
    mixed.number=latest.number;
    simulated_isr();
    mixed.current_ma=latest.current_ma;
    assert(mixed.number==100 && mixed.current_ma==3000);
    latest=(struct Sample){100,2000};
    const struct Sample coherent=latest; /* preemption is deferred until after copy */
    simulated_isr();
    assert(coherent.number==100 && coherent.current_ma==2000);
    const uint16_t raw=1000, zero=3000;
    const uint16_t wrapped=(uint16_t)(raw-zero);
    const int32_t correct=(int32_t)raw-(int32_t)zero;
    assert(wrapped==63536 && correct==-2000);
    printf("mixed=%" PRIu32 ",%" PRId32 " coherent=%" PRIu32 ",%" PRId32
           " wrapped=%" PRIu16 " correct=%" PRId32 "\n",
           mixed.number,mixed.current_ma,coherent.number,coherent.current_ma,wrapped,correct);
    return 0;
}
