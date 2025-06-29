/*
 * Copyright (c) 2015-2020, Texas Instruments Incorporated
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * *  Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * *  Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * *  Neither the name of Texas Instruments Incorporated nor the names of
 *    its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/*
 *  ======== gpiointerrupt.c ========
 */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

/* Driver Header files */
#include <ti/drivers/GPIO.h>
#include <ti/drivers/Timer.h>

/* Driver configuration */
#include "ti_drivers_config.h"

#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

/* Driver Header files */
#include <ti/drivers/GPIO.h>
#include <ti/drivers/Timer.h>

/* Driver configuration */
#include "ti_drivers_config.h"

/* Configuration Constants */
#define MAX_MSG_LEN 100                 // Maximum user input message length
#define UNIT_MS_DEFAULT 500            // Default Morse blip timing (ms)
#define SIM_MODE 1                     // Set to 1 for console simulation mode, 0 for embedded LED mode

/* Enumeration for LED states */
enum STATES { RED, GREEN, OFF } STATE;

/* Morse Code Engine Variables */
unsigned int msgIndex = 0;             // Index into the current Morse message pattern
int msgLength = 0;                     // Length of the current Morse pattern
int unit_ms = UNIT_MS_DEFAULT;         // Current unit timing for Morse blips (in ms)

/* Storage for the translated Morse message pattern */
enum STATES currentMessage[MAX_MSG_LEN * 10];

/* Morse alphabet: A-Z (dots = RED, dashes = GREEN) */
const char* morseTable[26] = {
    ".-", "-...", "-.-.", "-..", ".", "..-.", "--.", "....", "..",  // A-I
    ".---", "-.-", ".-..", "--", "-.", "---", ".--.", "--.-", ".-.", // J-R
    "...", "-", "..-", "...-", ".--", "-..-", "-.--", "--.."         // S-Z
};

/*
 *  ======== appendSymbol ========
 *  Appends a Morse symbol to the message buffer.
 *  '.' becomes RED + OFF; '-' becomes GREEN + OFF.
 */
void appendSymbol(enum STATES* buffer, int* index, char symbol) {
    if (symbol == '.') {
        buffer[(*index)++] = RED;
        buffer[(*index)++] = OFF;
    } else if (symbol == '-') {
        buffer[(*index)++] = GREEN;
        buffer[(*index)++] = OFF;
    }
}

/*
 *  ======== generateMorse ========
 *  Converts a user-entered string into a sequence of LED states
 *  representing Morse code.
 */
void generateMorse(const char* text) {
    msgIndex = 0;
    msgLength = 0;

    for (int i = 0; text[i] != '\0'; i++) {
        if (isalpha(text[i])) {
            const char* code = morseTable[toupper(text[i]) - 'A'];
            for (int j = 0; code[j] != '\0'; j++) {
                appendSymbol(currentMessage, &msgLength, code[j]);
            }
            currentMessage[msgLength++] = OFF; // Gap between characters
        }
    }
}

/*
 *  ======== setLEDs ========
 *  Controls LED output depending on selected mode.
 *  In simulation mode, prints Morse symbols to console.
 *  In embedded mode, toggles hardware LEDs.
 */
void setLEDs() {
#if SIM_MODE
    switch (STATE) {
        case RED: printf("."); break;
        case GREEN: printf("-"); break;
        case OFF: printf(" "); break;
    }
    fflush(stdout); // Ensure output is printed immediately
#else
    switch (STATE) {
        case RED:
            GPIO_write(CONFIG_GPIO_LED_0, CONFIG_GPIO_LED_ON);
            GPIO_write(CONFIG_GPIO_LED_1, CONFIG_GPIO_LED_OFF);
            break;
        case GREEN:
            GPIO_write(CONFIG_GPIO_LED_0, GPIO_CFG_OUT_LOW);
            GPIO_write(CONFIG_GPIO_LED_1, GPIO_CFG_OUT_HIGH);
            break;
        case OFF:
            GPIO_write(CONFIG_GPIO_LED_0, GPIO_CFG_OUT_LOW);
            GPIO_write(CONFIG_GPIO_LED_1, GPIO_CFG_OUT_LOW);
            break;
    }
#endif
}

/*
 *  ======== timerCallback ========
 *  Invoked at regular intervals to advance Morse message playback.
 */
void timerCallback(Timer_Handle myHandle, int_fast16_t status) {
    if (msgIndex < msgLength) {
        STATE = currentMessage[msgIndex++];
        setLEDs();
    } else {
        msgIndex = 0; // Restart the message
#if SIM_MODE
        printf("\n"); // Newline after completing message
#endif
    }
}

/*
 *  ======== initTimer ========
 *  Initializes and starts the timer with a given period.
 */
void initTimer(int period_us) {
    Timer_Handle timer0;
    Timer_Params params;

    Timer_init();
    Timer_Params_init(&params);
    params.period = period_us;
    params.periodUnits = Timer_PERIOD_US;
    params.timerMode = Timer_CONTINUOUS_CALLBACK;
    params.timerCallback = timerCallback;

    timer0 = Timer_open(CONFIG_TIMER_0, &params);
    if (timer0 == NULL || Timer_start(timer0) == Timer_STATUS_ERROR) {
        while (1) {} // Trap execution on failure
    }
}

/*
 *  ======== mainThread ========
 *  Entry point of the application. Initializes GPIO or console,
 *  accepts user input, generates Morse pattern, and starts timer.
 */
void *mainThread(void *arg0) {
#if !SIM_MODE
    GPIO_init();
    initTimer(unit_ms * 1000);

    GPIO_setConfig(CONFIG_GPIO_LED_0, GPIO_CFG_OUT_STD | GPIO_CFG_OUT_LOW);
    GPIO_setConfig(CONFIG_GPIO_LED_1, GPIO_CFG_OUT_STD | GPIO_CFG_OUT_LOW);
    GPIO_write(CONFIG_GPIO_LED_0, GPIO_CFG_OUT_LOW);
    GPIO_write(CONFIG_GPIO_LED_1, GPIO_CFG_OUT_LOW);
#else
    char input[MAX_MSG_LEN];
    int speed;

    printf("Enter message to convert to Morse (letters only): ");
    fgets(input, sizeof(input), stdin);
    input[strcspn(input, "\n")] = '\0';

    printf("Enter speed in milliseconds per unit (100–1000): ");
    scanf("%d", &speed);
    unit_ms = (speed >= 100 && speed <= 1000) ? speed : UNIT_MS_DEFAULT;

    generateMorse(input);
    initTimer(unit_ms * 1000);
#endif

    return (NULL);
}
