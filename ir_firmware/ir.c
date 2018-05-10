/* Define which IOs on the expansion deck is used */
#define SENSOR_OUT	DECK_GPIO_TX2

#include "deck.h"

#include "log.h"

#include "FreeRTOS.h"
#include "timers.h"

static xTimerHandle timer;
static float range;

// This function will be called by the FreeRTOS timer every 100ms
void SensorValue(xTimerHandle timer)
{
   range=analogReadVoltage(SENSOR_OUT); // Reading the value of the sensor 1
   //range=analogRead(DECK_GPIO_TX1); // Reading the value of the sensor 2
   //range=analogRead(DECK_GPIO_SCK); // Reading the value of the sensor 3
}

void irInit(DeckInfo *info)
{
  pinMode(SENSOR_OUT,INPUT); // Set my sensor 1 as an input
  //pinMode(DECK_GPIO_TX1,INPUT); // Set my sensor 2 as an input
  //pinMode(DECK_GPIO_SCK,INPUT); // Set my sensor 3 as an input

  // Create and start the update timer with a period of 100ms
  timer = xTimerCreate("irsensorTmr", M2T(100), pdTRUE, NULL, SensorValue);
  xTimerStart(timer, 100);
}

static const DeckDriver ir_deck = {
  .vid = 0x00,
  .pid = 0x00,
  .name = "bcIR",

  .usedGpio = DECK_USING_TX2,

  .init = irInit,
};

DECK_DRIVER(ir_deck);

LOG_GROUP_START(forwardRange)
LOG_ADD(LOG_FLOAT, forwardRange, &range)
LOG_GROUP_STOP(forwardRange)