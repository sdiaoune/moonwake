/* MW v2 keeps both v1 slots and the earlier Signal Bloom save untouched. */
#pragma bank 6
#include <gb/gb.h>
#include <stdint.h>
#include <string.h>
#include "game.h"
#define SAVE_SIZE 192u
#define SLOT_A 0xA200u
#define SLOT_B 0xA300u
#define GENERATION_FENCE 0xA3F0u
#define MEDALS 24u
#define SEALS 48u
#define TIMES 96u
static uint16_t sequence;
static const uint16_t crc_nibbles[16]={0x0000,0x1021,0x2042,0x3063,0x4084,0x50a5,0x60c6,0x70e7,0x8108,0x9129,0xa14a,0xb16b,0xc18c,0xd1ad,0xe1ce,0xf1ef};
static uint16_t crc(const uint8_t *b,uint8_t end){
 uint8_t i;uint16_t c=0xffff;
 for(i=1;i<end;i++){c^=(uint16_t)b[i]<<8;c=(c<<4)^crc_nibbles[c>>12];c=(c<<4)^crc_nibbles[c>>12];}
 return c;
}
static uint16_t word(const uint8_t *b,uint8_t i){return (uint16_t)b[i]|((uint16_t)b[i+1]<<8);}
static void putword(uint8_t*b,uint8_t i,uint16_t n){b[i]=n;b[i+1]=n>>8;}
static uint8_t valid(const uint8_t*b){
 return b[0]=='M'&&b[1]=='W'&&b[2]==2&&b[5]<LEVEL_COUNT&&b[6]<2&&b[8]<=b[5]&&b[9]<ROOMS_PER_STAGE&&b[10]<2&&b[11]>0&&b[11]<=3&&b[13]<2&&(!b[13]||(b[9]==2&&(b[8]==LEVEL_COUNT-1?b[6]:b[8]+1<=b[5])))&&crc(b,190)==word(b,190);
}
static uint8_t legacy_valid(const uint8_t*b){return b[0]=='M'&&b[1]=='W'&&b[2]==1&&b[5]<12&&b[6]<2&&crc(b,62)==word(b,62);}
static void migrate(void){
 uint8_t a[64],b[64],*p,i,va,vb;uint16_t sa,sb;volatile uint8_t*r=(volatile uint8_t*)0xA100;
 ENABLE_RAM;SWITCH_RAM(0);for(i=0;i<64;i++){a[i]=r[i];b[i]=r[0x80+i];}DISABLE_RAM;
 va=legacy_valid(a);vb=legacy_valid(b);if(!va&&!vb)return;
 sa=word(a,3);sb=word(b,3);p=vb&&(!va||(int16_t)(sb-sa)>0)?b:a;
 unlocked=p[6]?12:p[5];completed=0;sound_on=p[7]?1:0;
 for(i=0;i<12;i++)seal_bits[i]=p[20+i]&7;
 /* Longer courses have new ranks/pars. Preserve first-room discoveries,
    and offer the whole expanded journey with the old atlas unlocked. */
 memset(medal,0,sizeof(medal));memset(best_frames,0,sizeof(best_frames));
 deaths=word(p,56);stage_id=room_id=checkpoint_on=stars=seal_count=stage_clear_pending=0;run_seal_bits=stage_frames=0;health=3;journey_frames=0;
 memset(room_taken_bits,0,8);migrated_save=1;save_write();
}
void save_read(void) BANKED {
 uint8_t a[SAVE_SIZE],b[SAVE_SIZE],*p,i,va,vb,fenced;uint16_t sa,sb;volatile uint8_t*r;
 ENABLE_RAM;SWITCH_RAM(0);r=(volatile uint8_t*)SLOT_A;for(i=0;i<SAVE_SIZE;i++)a[i]=r[i];r=(volatile uint8_t*)SLOT_B;for(i=0;i<SAVE_SIZE;i++)b[i]=r[i];r=(volatile uint8_t*)GENERATION_FENCE;fenced=r[0]=='M'&&r[1]=='W'&&r[2]=='2'&&r[3]=='!';DISABLE_RAM;
 va=valid(a);vb=valid(b);
 if(!va&&!vb){
  /* Invalid newer saves must not silently resurrect an old playthrough. */
  if(!fenced&&!((a[0]=='M'&&a[1]=='W'&&a[2]==2)||(b[0]=='M'&&b[1]=='W'&&b[2]==2)))migrate();
  return;
 }
 sa=word(a,3);sb=word(b,3);save_slot=vb&&(!va||(int16_t)(sb-sa)>0);p=save_slot?b:a;sequence=save_slot?sb:sa;
 unlocked=p[5];completed=p[6];sound_on=p[7]?1:0;stage_id=p[8];room_id=p[9];checkpoint_on=p[10];health=p[11];stars=p[12];stage_clear_pending=p[13];deaths=word(p,14);stage_frames=word(p,16);run_seal_bits=word(p,18)&0x1ff;
 seal_count=0;for(i=0;i<9;i++)if(run_seal_bits&((uint16_t)1<<i))seal_count++;
 for(i=0;i<LEVEL_COUNT;i++){medal[i]=p[MEDALS+i]<4?p[MEDALS+i]:0;seal_bits[i]=word(p,SEALS+i*2)&0x1ff;best_frames[i]=word(p,TIMES+i*2);}
 journey_frames=(uint32_t)p[144]|((uint32_t)p[145]<<8)|((uint32_t)p[146]<<16)|((uint32_t)p[147]<<24);
 memcpy(room_taken_bits,p+152,8);save_valid=1;
}
void save_write(void) BANKED {
 uint8_t b[SAVE_SIZE],i;uint16_t c;volatile uint8_t*r;
 memset(b,0,SAVE_SIZE);sequence++;b[0]='M';b[1]='W';b[2]=2;putword(b,3,sequence);b[5]=unlocked;b[6]=completed;b[7]=sound_on;b[8]=stage_id;b[9]=room_id;b[10]=checkpoint_on;b[11]=health?health:3;b[12]=stars;b[13]=stage_clear_pending;putword(b,14,deaths);putword(b,16,stage_frames);putword(b,18,run_seal_bits);
 for(i=0;i<LEVEL_COUNT;i++){b[MEDALS+i]=medal[i];putword(b,SEALS+i*2,seal_bits[i]);putword(b,TIMES+i*2,best_frames[i]);}
 b[144]=journey_frames;b[145]=journey_frames>>8;b[146]=journey_frames>>16;b[147]=journey_frames>>24;memcpy(b+152,room_taken_bits,8);
 c=crc(b,190);putword(b,190,c);save_slot^=1;
 ENABLE_RAM;SWITCH_RAM(0);r=(volatile uint8_t*)(save_slot?SLOT_B:SLOT_A);r[0]=0;for(i=1;i<SAVE_SIZE;i++)r[i]=b[i];r[0]=b[0];
 /* Commit the generation marker only after a valid transactional slot exists. */
 r=(volatile uint8_t*)GENERATION_FENCE;r[0]='M';r[1]='W';r[2]='2';r[3]='!';DISABLE_RAM;save_valid=1;
}
void save_reset(void) BANKED {
 unlocked=completed=stage_id=room_id=deaths=checkpoint_on=stars=seal_count=migrated_save=stage_clear_pending=0;run_seal_bits=stage_frames=0;journey_frames=0;health=3;
 memset(medal,0,sizeof(medal));memset(seal_bits,0,sizeof(seal_bits));memset(best_frames,0,sizeof(best_frames));memset(room_taken_bits,0,8);save_write();
}
