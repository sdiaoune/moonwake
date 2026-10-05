/* Double-slot CRC save. Distinct Moonwake signature preserves Signal Bloom data. */
#pragma bank 6
#include <gb/gb.h>
#include <stdint.h>
#include <string.h>
#include "game.h"
#define SAVE_SIZE 64
static uint16_t sequence;
static uint16_t crc(const uint8_t*b){uint8_t i,j;uint16_t c=0xffff;for(i=1;i<62;i++){c^=(uint16_t)b[i]<<8;for(j=0;j<8;j++)c=(c&0x8000)?(c<<1)^0x1021:c<<1;}return c;}
static uint8_t valid(const uint8_t*b){return b[0]=='M'&&b[1]=='W'&&b[2]==1&&b[5]<LEVEL_COUNT&&b[6]<2&&crc(b)==((uint16_t)b[62]|((uint16_t)b[63]<<8));}
void save_read(void) BANKED {
 uint8_t a[SAVE_SIZE],b[SAVE_SIZE],*p,i,va,vb;uint16_t sa,sb;volatile uint8_t*r=(volatile uint8_t*)0xA100;
 ENABLE_RAM;SWITCH_RAM(0);for(i=0;i<SAVE_SIZE;i++){a[i]=r[i];b[i]=r[0x80+i];}DISABLE_RAM;
 va=valid(a);vb=valid(b);sa=(uint16_t)a[3]|((uint16_t)a[4]<<8);sb=(uint16_t)b[3]|((uint16_t)b[4]<<8);
 if(!va&&!vb)return;save_slot=vb&&(!va||(int16_t)(sb-sa)>0);p=save_slot?b:a;sequence=save_slot?sb:sa;
 unlocked=p[5];completed=p[6];sound_on=p[7]?1:0;for(i=0;i<LEVEL_COUNT;i++){medal[i]=p[8+i]<4?p[8+i]:0;seal_bits[i]=p[20+i]&7;best_frames[i]=(uint16_t)p[32+i*2]|((uint16_t)p[33+i*2]<<8);}
 deaths=(uint16_t)p[56]|((uint16_t)p[57]<<8);stage_id=p[58]<=unlocked?p[58]:unlocked;save_valid=1;
}
void save_write(void) BANKED {
 uint8_t b[SAVE_SIZE],i;uint16_t c;volatile uint8_t*r;
 memset(b,0,SAVE_SIZE);sequence++;b[0]='M';b[1]='W';b[2]=1;b[3]=sequence;b[4]=sequence>>8;b[5]=unlocked;b[6]=completed;b[7]=sound_on;
 for(i=0;i<LEVEL_COUNT;i++){b[8+i]=medal[i];b[20+i]=seal_bits[i];b[32+i*2]=best_frames[i];b[33+i*2]=best_frames[i]>>8;}
 b[56]=deaths;b[57]=deaths>>8;b[58]=stage_id;c=crc(b);b[62]=c;b[63]=c>>8;save_slot^=1;
 ENABLE_RAM;SWITCH_RAM(0);r=(volatile uint8_t*)(save_slot?0xA180:0xA100);r[0]=0;for(i=1;i<SAVE_SIZE;i++)r[i]=b[i];r[0]=b[0];DISABLE_RAM;save_valid=1;
}
void save_reset(void) BANKED {unlocked=completed=stage_id=deaths=0;memset(medal,0,LEVEL_COUNT);memset(seal_bits,0,LEVEL_COUNT);memset(best_frames,0,LEVEL_COUNT*2);save_write();}
