#ifndef MOONWAKE_GAME_H
#define MOONWAKE_GAME_H
#include <gb/gb.h>
#include <stdint.h>
#include "levels.h"
#define TITLE 0
#define PLAY 1
#define PAUSE 2
#define STAGE_CLEAR 3
#define MAP 4
#define STORY 5
#define ENDING 6
#define HELP 7
extern uint8_t game_mode,stage_id,input,pressed,previous_input,frame;
extern uint8_t health,grounded,dash_charge,dash_timer,seal_count,stars,combo;
extern uint8_t unlocked,completed,save_valid,sound_on,map_selection,story_next;
extern uint8_t medal[LEVEL_COUNT];
extern uint16_t seal_bits[LEVEL_COUNT],run_seal_bits;
extern uint8_t room_id,room_taken_bits[8],migrated_save;
extern uint8_t stage_clear_pending;
extern uint32_t journey_frames;
extern uint16_t best_frames[LEVEL_COUNT],deaths,stage_frames,camera_x,checkpoint_x;
extern int16_t player_x,player_y,velocity_x,velocity_y;
extern uint8_t title_selection,checkpoint_on,save_slot,current_rank,boss_hp;
extern LevelDef current_level;
extern PlatformDef platforms[48];
extern PickupDef pickups[64];
extern EnemyDef enemies[12];
extern uint8_t pickup_taken[64],enemy_alive[12],crumble[48];
extern uint8_t scenery_map[576],scenery_attr[576],map_tiles[576],map_attrs[576];
void game_init(void) BANKED;
void game_tick(void) BANKED;
void begin_stage(uint8_t id,uint8_t intro) BANKED;
void continue_adventure(void) BANKED;
void restart_checkpoint(void) BANKED;
void load_boss_art(uint8_t boss) NONBANKED;
void begin_room_transition(void) NONBANKED;
void end_room_transition(void) NONBANKED;
void save_read(void) BANKED;
void save_write(void) BANKED;
void save_reset(void) BANKED;
void ui_title(void) BANKED;
void ui_story(uint8_t scene) BANKED;
void ui_pause(void) BANKED;
void ui_map(void) BANKED;
void ui_help(void) BANKED;
void ui_clear(void) BANKED;
void ui_ending(void) BANKED;
void ui_tick(void) BANKED;
void load_world_art(uint8_t biome) NONBANKED;
void load_title_art(void) NONBANKED;
void redraw_world(void) BANKED;
void draw_objects(void) BANKED;
void text_at(uint8_t x,uint8_t y,const char *s) NONBANKED;
void tile_at(uint8_t x,uint8_t y,uint8_t t,uint8_t a) NONBANKED;
void window_reset(uint8_t y,uint8_t rows) NONBANKED;
void window_text(uint8_t x,uint8_t y,const char *s) NONBANKED;
void window_number(uint8_t x,uint8_t y,uint16_t n,uint8_t digits) NONBANKED;
void hud_update(void) BANKED;
#endif
