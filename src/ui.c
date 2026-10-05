#pragma bank 5
#include <gb/gb.h>
#include <gb/cgb.h>
#include <stdint.h>
#include "game.h"
#include "music.h"
static uint8_t selection,reset_confirm,ui_age,story_scene,map_return;
static void resume(void);
static char line1[21],line2[21],line3[21];
static void hide_objects(void){uint8_t i;for(i=0;i<40;i++)hide_sprite(i);HIDE_SPRITES;}
static void panel(uint8_t y,uint8_t rows){hide_objects();window_reset(y,rows);}
static void title_menu(void){
 window_reset(104,5);window_text(2,0,title_selection==0?"> START ADVENTURE":"  START ADVENTURE");
 if(save_valid)window_text(2,0,title_selection==0?"> CONTINUE":"  CONTINUE");
 window_text(2,1,title_selection==1?"> STAGE ATLAS":"  STAGE ATLAS");window_text(2,2,title_selection==2?"> HOW TO PLAY":"  HOW TO PLAY");
 window_text(2,3,reset_confirm?"B AGAIN: NEW GAME":"A / START TO PLAY");window_text(0,4,"AN ORIGINAL GBC GAME");
}
void ui_title(void) BANKED {load_title_art();title_selection=reset_confirm=0;game_mode=TITLE;title_menu();DISPLAY_ON;audio_scene(0);ui_age=0;}
void ui_help(void) BANKED {
 game_mode=HELP;panel(32,14);window_text(2,0,"CHASE THE MOON.");window_text(1,2,"D-PAD  RUN");window_text(1,3,"A      JUMP");window_text(1,4,"HOLD A FOR HEIGHT");window_text(1,5,"B      COMET DASH");window_text(0,7,"LAND / TOUCH LANTERN");window_text(1,8,"TO REFILL YOUR DASH");window_text(1,9,"STOMP OR DASH FOES");window_text(1,11,"START PAUSE / ATLAS");window_text(1,12,"SELECT CHECKPOINT");window_text(1,13,"A BEGIN   B BACK");ui_age=0;
}
void ui_story(uint8_t scene) BANKED {
 game_mode=STORY;story_scene=scene;panel(96,6);level_intro(scene,line1,line2,line3);window_text(1,0,current_level.name);window_text(0,2,line1);window_text(0,3,line2);window_text(0,4,line3);window_text(14,5,"A GO >");ui_age=0;
}
void ui_pause(void) BANKED {
 game_mode=PAUSE;selection=0;panel(48,10);window_text(5,0,"MOONWAKE");window_text(1,2,current_level.name);window_text(2,4,"> KEEP RUNNING");window_text(2,5,"  STAGE ATLAS");window_text(2,6,sound_on?"  SOUND ON        ":"  SOUND OFF       ");window_text(2,7,"  BACK TO TITLE");window_text(1,9,"A SELECT   B RESUME");ui_age=0;
}
static void map_draw(void){
 uint8_t i,row,first=(map_selection/6)*6;LevelDef d;
 panel(24,15);window_text(3,0,"THE SKY ATLAS");
 window_text(0,1,"BEST");if(best_frames[map_selection])window_number(5,1,best_frames[map_selection]/60,3);else window_text(5,1,"---");window_text(8,1,"S PAR");window_number(14,1,level_par(map_selection),3);window_text(17,1,"S");
 for(i=first;i<first+6&&i<LEVEL_COUNT;i++){
  row=2+(i-first)*2;level_info(i,&d);
  window_text(0,row,i==map_selection?">":" ");if(i<=unlocked)window_text(1,row,d.name);else window_text(1,row,"??? SLEEPING SEA");
  if(i<=unlocked){window_text(2,row+1,"SEALS");window_number(8,row+1,(seal_bits[i]&1)+((seal_bits[i]>>1)&1)+((seal_bits[i]>>2)&1),1);window_text(9,row+1,"/3");window_text(13,row+1,medal[i]==3?"S":medal[i]==2?"A":medal[i]==1?"B":"-");}
 }
 window_text(0,14,"A GO B BACK <> PAGE");
}
void ui_map(void) BANKED {map_return=game_mode;game_mode=MAP;map_selection=stage_id;map_draw();ui_age=0;}
void ui_clear(void) BANKED {
 game_mode=STAGE_CLEAR;panel(40,13);window_text(4,0,"MOON DELIVERED");window_text(1,2,current_level.name);window_text(2,4,"MOON SEALS");window_number(14,4,seal_count,1);window_text(15,4,"/3");
 window_text(2,5,"STARLIGHT");window_number(13,5,stars,2);window_text(2,6,"TIME");window_number(13,6,stage_frames/60,3);window_text(17,6,"S");
 window_text(2,8,"RANK");window_text(9,8,current_rank==3?"S STARDUST":current_rank==2?"A MOONLIT":"B ARRIVED");
 window_text(2,7,"PAR");window_number(13,7,level_par(stage_id),3);window_text(17,7,"S");window_text(2,9,"BEST");window_number(13,9,best_frames[stage_id]/60,3);window_text(17,9,"S");
 window_text(0,10,"3 SEALS + PAR = S");window_text(0,11,"ATLAS: REPLAY STAGES");window_text(3,12,"A NEXT   B ATLAS");ui_age=0;
}
void ui_ending(void) BANKED {
 game_mode=ENDING;load_title_art();panel(64,10);window_text(1,0,"THE SKY REMEMBERS.");window_text(0,2,"THE MOONWHALE WAKES.");window_text(0,3,"A SEA OF DREAMS");window_text(0,4,"FLOWS HOME AGAIN.");window_text(0,6,"THANK YOU, MOON HARE");window_text(0,8,"A ATLAS   B TITLE");DISPLAY_ON;audio_scene(7);ui_age=0;
}
static void resume(void){game_mode=PLAY;HIDE_WIN;hud_update();draw_objects();SHOW_SPRITES;DISPLAY_ON;}
void ui_tick(void) BANKED {
 uint8_t old=selection;if(ui_age<240)ui_age++;
 if(ui_age<10)return;
 if(game_mode==TITLE){
  if(pressed&J_DOWN){title_selection=(title_selection+1)%3;reset_confirm=0;title_menu();}if(pressed&J_UP){title_selection=(title_selection+2)%3;reset_confirm=0;title_menu();}
  if(pressed&J_B){if(reset_confirm){save_reset();begin_stage(0,1);}else{reset_confirm=1;title_menu();}}
  if(pressed&(J_A|J_START)){if(title_selection==1){ui_map();}else if(title_selection==2)ui_help();else begin_stage(save_valid?stage_id:0,1);}
 }else if(game_mode==HELP){if(pressed&(J_A|J_START))begin_stage(save_valid?stage_id:0,1);else if(pressed&J_B)ui_title();}
 else if(game_mode==STORY){if(pressed&(J_A|J_START|J_B))resume();}
 else if(game_mode==PAUSE){
  if(pressed&J_DOWN)selection=(selection+1)%4;if(pressed&J_UP)selection=(selection+3)%4;
  if(selection!=old){window_text(2,4," ");window_text(2,5," ");window_text(2,6," ");window_text(2,7," ");window_text(2,4+selection,">");}
  if(pressed&(J_B|J_START))resume();else if(pressed&J_A){if(selection==0)resume();else if(selection==1)ui_map();else if(selection==2){sound_on^=1;audio_enable(sound_on);save_write();window_text(2,6,sound_on?"> SOUND ON        ":"> SOUND OFF       ");}else ui_title();}
 }else if(game_mode==MAP){
  uint8_t m=map_selection;
  if(pressed&J_DOWN&&map_selection<unlocked)map_selection++;if(pressed&J_UP&&map_selection)map_selection--;
  if(pressed&J_RIGHT){map_selection=map_selection<6?6:map_selection;if(map_selection>unlocked)map_selection=unlocked;}
  if(pressed&J_LEFT&&map_selection>=6)map_selection-=6;
  if(m!=map_selection)map_draw();
  if(pressed&(J_A|J_START))begin_stage(map_selection,1);else if(pressed&J_B){if(map_return==PAUSE)resume();else if(map_return==STAGE_CLEAR)ui_clear();else if(map_return==ENDING)ui_ending();else ui_title();}
 }else if(game_mode==STAGE_CLEAR){if(pressed&J_B)ui_map();else if(pressed&(J_A|J_START)){if(stage_id==LEVEL_COUNT-1)ui_ending();else begin_stage(stage_id+1,1);}}
 else if(game_mode==ENDING){if(pressed&J_A)ui_map();else if(pressed&J_B)ui_title();}
}
