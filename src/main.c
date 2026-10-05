#include <gb/gb.h>
#include <gb/cgb.h>
#include <stdint.h>
#include <string.h>
#include "art.h"
#include "game.h"
#include "music.h"
uint8_t scenery_map[576],scenery_attr[576],map_tiles[576],map_attrs[576];
static uint8_t window_scratch[80];
static uint16_t active_world_palette[32];
static const uint16_t transition_palette[32]={0};
void begin_room_transition(void) NONBANKED {HIDE_SPRITES;HIDE_WIN;set_bkg_palette(0,8,transition_palette);}
void end_room_transition(void) NONBANKED {set_bkg_palette(0,8,active_world_palette);}
void tile_at(uint8_t x,uint8_t y,uint8_t t,uint8_t a) NONBANKED {
 VBK_REG=0;set_bkg_tile_xy(x,y,t);VBK_REG=1;set_bkg_tile_xy(x,y,a);VBK_REG=0;
}
void text_at(uint8_t x,uint8_t y,const char*s) NONBANKED {
 while(*s&&x<20){uint8_t c=*s++;if(c>='a'&&c<='z')c-=32;tile_at(x++,y,c>=32&&c<96?c:'?',7);}
}
void window_reset(uint8_t y,uint8_t rows) NONBANKED {
 uint8_t i,n;rows=(144-y+7)>>3;VBK_REG=0;memset(window_scratch,32,80);
 for(i=0;i<rows;i+=4){n=rows-i>4?4:rows-i;set_win_tiles(0,i,20,n,window_scratch);}
 VBK_REG=1;memset(window_scratch,7,80);for(i=0;i<rows;i+=4){n=rows-i>4?4:rows-i;set_win_tiles(0,i,20,n,window_scratch);}
 VBK_REG=0;move_win(7,y);SHOW_WIN;
}
void window_text(uint8_t x,uint8_t y,const char*s) NONBANKED {while(*s&&x<20){uint8_t c=*s++;if(c>='a'&&c<='z')c-=32;set_win_tile_xy(x++,y,c>=32&&c<96?c:'?');}}
void window_number(uint8_t x,uint8_t y,uint16_t n,uint8_t digits) NONBANKED {while(digits){set_win_tile_xy(x+--digits,y,'0'+n%10);n/=10;}}
static void upload(const ArtDef *d,uint8_t title,uint8_t biome) NONBANKED {
 uint8_t saved=CURRENT_BANK,i;ArtDef a;
 DISPLAY_OFF;HIDE_WIN;for(i=0;i<40;i++)hide_sprite(i);
 SWITCH_ROM(1);memcpy(&a,d,sizeof(ArtDef));SWITCH_ROM(a.bank);
 VBK_REG=0;set_bkg_data(112,a.n0,a.tiles0);VBK_REG=1;if(a.n1)set_bkg_data(96,a.n1,a.tiles1);
 if(title){memcpy(map_tiles,a.map,360);memcpy(map_attrs,a.attr,360);}else{memcpy(scenery_map,a.map,576);memcpy(scenery_attr,a.attr,576);}
 set_bkg_palette(0,8,a.pal);if(!title)memcpy(active_world_palette,a.pal,sizeof(active_world_palette));
 SWITCH_ROM(1);VBK_REG=0;set_bkg_data(32,64,font_tiles);set_bkg_data(96,16,title?terrain_tiles:terrain_world_tiles+(uint16_t)biome*256);
 VBK_REG=1;set_sprite_data(0,96,sprite_tiles);set_sprite_palette(0,8,sprite_palettes);VBK_REG=0;
 if(title){set_bkg_tiles(0,0,20,18,map_tiles);VBK_REG=1;set_bkg_tiles(0,0,20,18,map_attrs);VBK_REG=0;}
 move_bkg(0,0);SPRITES_8x16;SHOW_BKG;HIDE_SPRITES;
 SWITCH_ROM(saved);
}
void load_world_art(uint8_t biome) NONBANKED {upload(&art_worlds[biome],0,biome);}
void load_title_art(void) NONBANKED {upload(&art_title,1,0);}
void load_boss_art(uint8_t boss) NONBANKED {
 uint8_t saved=CURRENT_BANK;if(!boss||boss>4)return;SWITCH_ROM(1);VBK_REG=1;set_sprite_data(64,16,boss_tiles[boss-1]);VBK_REG=0;SWITCH_ROM(saved);
}
void main(void){
 cpu_fast();game_init();
 while(1){vsync();input=joypad();pressed=input&~previous_input;previous_input=input;frame++;audio_tick(game_mode==PLAY?(dash_timer?2:combo?1:0):0);game_tick();}
}
