#define F_CPU 1000000UL

#include <avr/io.h>
#include <util/delay.h>

int main() {

    DDRB |= (1 << PB0);
    int a=10;
    while(a>0) {
        a--;
        PORTB ^= (1 << PB0);

        _delay_ms(500);
    }
}
