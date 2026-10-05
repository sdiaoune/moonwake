/* Moonwake: native scrolling gameplay, 12.4 fixed point, 60 Hz controller loop. */
#pragma bank 4
#include <gb/gb.h>
#include <gb/cgb.h>
#include <stdint.h>
#include <string.h>
#include "game.h"
#include "music.h"
uint8_t game_mode,stage_id,input,pressed,previous_input,frame;
uint8_t health,grounded,dash_charge,dash_timer,seal_count,stars,combo;
uint8_t unlocked,completed,save_valid,sound_on=1,map_selection,story_next;
uint8_t medal[LEVEL_COUNT],seal_bits[LEVEL_COUNT];
uint16_t best_frames[LEVEL_COUNT],deaths,stage_frames,camera_x,checkpoint_x;
int16_t player_x,player_y,velocity_x,velocity_y;
uint8_t title_selection,checkpoint_on,save_slot,current_rank;
LevelDef current_level;
PlatformDef platforms[48];PickupDef pickups[64];EnemyDef enemies[12];
uint8_t pickup_taken[64],enemy_alive[12],crumble[48];
static int8_t enemy_offset[12],enemy_direction[12];
static uint8_t pickup_buckets[32][8],pickup_bucket_counts[32],pickup_seal_id[64],lantern_active[8],lantern_active_count;
static uint8_t lantern_cooldown[64],coyote,jump_buffer,facing,hurt_timer,combo_timer;
static uint8_t spring_timer;
uint8_t boss_hp;
static uint8_t boss_cooldown,boss_y,boss_shot_timer,boss_shot_index,particle_timer,checkpoint_notice;
static int16_t projectile_x[2];static uint8_t projectile_y[2],projectile_on[2];
static uint8_t column_tiles[18],column_attrs[18],column_cache_valid;
static uint16_t old_camera_column;static uint8_t old_health,old_stars,old_charge,old_seals,old_combo,hud_banner,combo_notice,old_boss_hp,boss_hud;
static int16_t previous_y;
static uint8_t bits3(uint8_t b){return (b&1)+((b>>1)&1)+((b>>2)&1);}
static uint8_t overlap(int16_t ax,int16_t ay,uint8_t aw,uint8_t ah,int16_t bx,int16_t by,uint8_t bw,uint8_t bh){return ax<bx+bw&&ax+aw>bx&&ay<by+bh&&ay+ah>by;}
static uint8_t platform_live(uint8_t i){return platforms[i].kind!=3||crumble[i]<40;}
void column(uint16_t c){
 uint8_t y,i,k,tx=c&31,sx=(c+(stage_id%3)*7)&31;uint16_t wx=c<<3,o;
 for(y=0;y<18;y++){o=(uint16_t)y*32+sx;column_tiles[y]=scenery_map[o];column_attrs[y]=scenery_attr[o];}
 for(i=0;i<current_level.platform_count;i++){
  PlatformDef*p=&platforms[i];if(wx<p->x||wx>=p->x+p->w||!platform_live(i))continue;
  y=p->y>>3;k=p->kind;if(y>=18)continue;
  column_tiles[y]=k==1?101:k==2?102:k==3?103:wx==p->x?96:wx+8>=p->x+p->w?98:97;column_attrs[y]=6;
  if(k==0&&y<17){column_tiles[y+1]=99;column_attrs[y+1]=6;}
 }
 if(!column_cache_valid){VBK_REG=0;set_bkg_tiles(tx,0,1,18,column_tiles);VBK_REG=1;set_bkg_tiles(tx,0,1,18,column_attrs);VBK_REG=0;}
 for(y=0;y<18;y++){o=(uint16_t)y*32+tx;if(column_cache_valid&&(map_tiles[o]!=column_tiles[y]||map_attrs[o]!=column_attrs[y]))tile_at(tx,y,column_tiles[y],column_attrs[y]);map_tiles[o]=column_tiles[y];map_attrs[o]=column_attrs[y];}
}
void redraw_world(void) BANKED {uint8_t i;uint16_t c=camera_x>>3;column_cache_valid=0;for(i=0;i<32;i++)column(c+i);column_cache_valid=1;old_camera_column=c;move_bkg((uint8_t)camera_x,0);}
static void redraw_platform(uint8_t i){uint16_t c;PlatformDef*p=&platforms[i];for(c=p->x>>3;c<(p->x+p->w)>>3;c++)if(c>=camera_x/8&&c<=camera_x/8+21)column(c);}
void camera_update(void){
 int16_t target=(player_x>>4)-(facing?96:56);uint16_t c;int16_t delta;uint8_t i;
 if(target<0)target=0;if(target>(int16_t)(current_level.length-160))target=current_level.length-160;
 delta=target-camera_x;if(delta>6)delta=6;if(delta< -6)delta= -6;camera_x+=delta;c=camera_x>>3;
 if(c>old_camera_column){for(i=0;i<c-old_camera_column;i++)column(old_camera_column+21+i);}
 else if(c<old_camera_column){for(i=0;i<old_camera_column-c;i++)column(c+i);}
 old_camera_column=c;move_bkg((uint8_t)camera_x,0);
}
void hud_update(void) BANKED {
 uint8_t i,force=!(LCDC_REG&0x20)||hud_banner;
 if(checkpoint_notice||combo_notice){if(!hud_banner||!(LCDC_REG&0x20)){window_reset(136,1);window_text(0,0,checkpoint_notice?"CHECKPOINT - SAVED":"WAKE CHAIN! +HEART");hud_banner=1;}return;}
 hud_banner=0;if(force){window_reset(136,1);window_text(0,0,"H");window_text(5,0,"S");window_text(10,0,"$");window_text(14,0,"X");boss_hud=0;window_text(18,0,"B");}
 if(force||health!=old_health)for(i=0;i<3;i++)set_win_tile_xy(1+i,0,i<health?'*':'.');
 if(force||seal_count!=old_seals)for(i=0;i<3;i++)set_win_tile_xy(6+i,0,i<seal_count?'*':'.');
 if(force||stars!=old_stars)window_number(11,0,stars,2);
 if(current_level.boss&&camera_x>current_level.goal_x-200){window_text(14,0,"HP");window_number(16,0,boss_hp,1);boss_hud=1;}else window_number(15,0,combo,1);if(force||dash_charge!=old_charge)set_win_tile_xy(19,0,dash_charge?'+':'-');
 old_health=health;old_stars=stars;old_charge=dash_charge;old_seals=seal_count;old_combo=combo;old_boss_hp=boss_hp;
}
static void sprite8(uint8_t id,int16_t x,int16_t y,uint8_t t,uint8_t pal,uint8_t flip){
 if(x<=-8||x>=160||y<=-16||y>=144){hide_sprite(id);return;}
 set_sprite_tile(id,t);set_sprite_prop(id,S_BANK|pal|(flip?S_FLIPX:0));move_sprite(id,x+8,y+16);
}
static void sprite16(uint8_t id,int16_t x,int16_t y,uint8_t t,uint8_t pal,uint8_t flip){
 sprite8(id,x,y,t+(flip?2:0),pal,flip);sprite8(id+1,x+8,y,t+(flip?0:2),pal,flip);
}
static int16_t enemy_x(uint8_t i){return enemies[i].x+enemy_offset[i];}
static uint8_t enemy_y(uint8_t i){uint8_t n;if(enemies[i].kind!=1)return enemies[i].y;n=(frame+i*13)&63;n=n<32?n:63-n;return enemies[i].y+n/4-4;}
void draw_objects(void) BANKED {
 uint8_t i,id=2,pose,n,b,k,last_bucket;int16_t x,y,px=(player_x>>4)-camera_x,py=player_y>>4;
 pose=dash_timer?5:!grounded?4:velocity_x?1+((frame>>3)%3):0;
 if(hurt_timer&&(frame&4)){hide_sprite(0);hide_sprite(1);}else sprite16(0,px,py,pose*4,0,facing);
 /* Gameplay sprites get priority over effects. At most two enemies on a scanline. */
 for(i=0;i<current_level.enemy_count&&id<10;i++)if(enemy_alive[i]){
  x=enemy_x(i)-camera_x;y=enemy_y(i);if(x> -16&&x<160){if(enemies[i].kind==2)sprite8(id++,x+4,y,50,1,0);else if(enemies[i].kind==1)sprite8(id++,x+4,y,28+((frame>>3)&1)*2,2,enemy_direction[i]<0);else{sprite16(id,x,y,24,1,enemy_direction[i]<0);id+=2;}}
 }
 /* The same spatial buckets used by collision also bound sprite work.
    Include the partially visible pickup at the left edge. */
 last_bucket=(camera_x+159)>>6;
 for(b=(camera_x>8?camera_x-8:0)>>6;b<=last_bucket&&b<32;b++)for(k=0;k<pickup_bucket_counts[b]&&id<24;k++){
  i=pickup_buckets[b][k];
  if(pickup_taken[i]&&pickups[i].kind!=1)continue;
  x=pickups[i].x-camera_x;if(x<=-8||x>=160)continue;y=pickups[i].y;
  if(pickups[i].kind==1&&lantern_cooldown[i])continue;
  sprite8(id++,x,y+((frame>>4)&1),pickups[i].kind==1?32:pickups[i].kind==2?34:44,pickups[i].kind==1?3:4,0);
 }
 x=current_level.checkpoint_x-camera_x;if(x> -8&&x<160)sprite8(id++,x,current_level.checkpoint_y-16,36,checkpoint_on?3:5,0);
 x=current_level.goal_x-camera_x;if(x>-16&&x<160&&(!current_level.boss||!boss_hp)){sprite16(id,x,current_level.goal_y-16,38,5,0);id+=2;}
 if(current_level.boss&&boss_hp){
  x=(int16_t)current_level.goal_x-48-camera_x;y=boss_y;
  for(i=0;i<4;i++)for(n=0;n<2;n++)sprite8(id++,x+i*8,y+n*16,64+i*4+n*2,boss_cooldown&&(frame&4)?4:boss_shot_timer<=12?3:7,0);
  for(i=0;i<2;i++)if(projectile_on[i])sprite8(id++,projectile_x[i]-camera_x,projectile_y[i],80,6,0);
 }
 if(dash_timer&&id<38){sprite8(id++,px+(facing?16:-8),py,42,6,facing);sprite8(id++,px+(facing?24:-16),py,42,6,facing);}
 if(particle_timer&&id<39)sprite8(id++,px+4,py-8,44,4,0);
 while(id<40)hide_sprite(id++);
}
static void reset_objects(void){uint8_t i,n=0,b;lantern_active_count=0;memset(pickup_bucket_counts,0,32);for(i=0;i<current_level.pickup_count;i++){pickup_taken[i]=0;lantern_cooldown[i]=0;if(pickups[i].kind==2){pickup_taken[i]=0;pickup_seal_id[i]=n;n++;}b=pickups[i].x>>6;if(b<32&&pickup_bucket_counts[b]<8)pickup_buckets[b][pickup_bucket_counts[b]++]=i;}
 for(i=0;i<current_level.enemy_count;i++){enemy_alive[i]=1;enemy_offset[i]=0;enemy_direction[i]=1;}memset(crumble,0,48);
 for(i=0;i<2;i++)projectile_on[i]=0;boss_hp=current_level.boss?6:0;boss_cooldown=boss_shot_index=0;boss_shot_timer=90;boss_y=72;
}
static void spawn(uint16_t x,uint8_t y){player_x=x<<4;player_y=(int16_t)y<<4;velocity_x=velocity_y=0;grounded=coyote=jump_buffer=0;dash_timer=0;spring_timer=0;dash_charge=1;hurt_timer=75;combo=combo_timer=0;health=3;facing=0;}
void begin_stage(uint8_t id,uint8_t intro) BANKED {
 stage_id=id;level_load(id,&current_level,platforms,pickups,enemies);stage_frames=0;stars=0;seal_count=0;checkpoint_notice=combo_notice=hud_banner=0;checkpoint_on=0;checkpoint_x=current_level.spawn_x;
 reset_objects();spawn(current_level.spawn_x,current_level.spawn_y);hurt_timer=0;camera_x=0;load_world_art(current_level.biome);redraw_world();hud_update();draw_objects();SHOW_SPRITES;DISPLAY_ON;
 audio_scene(current_level.boss?5:1+current_level.biome);game_mode=PLAY;save_write();
 if(intro){story_next=0;ui_story(id);}
}
void restart_checkpoint(void) BANKED {
 uint16_t x=checkpoint_on?current_level.checkpoint_x:current_level.spawn_x;uint8_t y=checkpoint_on?current_level.checkpoint_y-16:current_level.spawn_y;
 /* Preserve collected stars/seals; refresh hazards and temporary platforms. */
 uint8_t i;for(i=0;i<current_level.enemy_count;i++){enemy_alive[i]=1;enemy_offset[i]=0;enemy_direction[i]=1;}memset(crumble,0,48);
 for(i=0;i<2;i++)projectile_on[i]=0;boss_hp=current_level.boss?6:0;boss_cooldown=boss_shot_index=0;boss_shot_timer=90;
 spawn(x,y);camera_x=x>56?x-56:0;if(camera_x>current_level.length-160)camera_x=current_level.length-160;
 game_mode=PLAY;DISPLAY_OFF;HIDE_WIN;hud_banner=0;redraw_world();hud_update();draw_objects();SHOW_SPRITES;DISPLAY_ON;
 audio_scene(current_level.boss?5:1+current_level.biome);
}
static void hurt(int16_t source){
 if(hurt_timer||dash_timer)return;health--;hurt_timer=75;dash_timer=0;velocity_y=-55;velocity_x=(player_x>>4)<source?-42:42;audio_sfx(2);combo=0;
 if(!health){deaths++;restart_checkpoint();}
}
static void add_combo(void){if(combo<9)combo++;combo_timer=100;particle_timer=12;if(combo==3&&health<3){health++;combo_notice=45;}}
void physics(void){
 uint8_t i,landed=255;int16_t oldfeet,newfeet,px;PlatformDef*p;
 previous_y=player_y;if(spring_timer)spring_timer--;
 if(grounded)coyote=6;else if(coyote)coyote--;
 if(pressed&J_A)jump_buffer=6;else if(jump_buffer)jump_buffer--;
 if(!dash_timer){if(input&J_RIGHT)facing=0;else if(input&J_LEFT)facing=1;}
 if(pressed&J_B&&dash_charge){dash_charge=0;dash_timer=10;velocity_y=0;velocity_x=facing?-92:92;audio_sfx(4);particle_timer=8;}
 if(jump_buffer&&coyote&&!dash_timer){velocity_y=-100;grounded=coyote=jump_buffer=0;audio_sfx(0);}
 if(dash_timer){velocity_x=facing?-92:92;velocity_y=0;dash_timer--;}
 else{
  if(input&J_RIGHT){velocity_x+=5;if(velocity_x>42)velocity_x=42;facing=0;}
  else if(input&J_LEFT){velocity_x-=5;if(velocity_x< -42)velocity_x=-42;facing=1;}
  else if(velocity_x>0){velocity_x-=6;if(velocity_x<0)velocity_x=0;}
  else if(velocity_x<0){velocity_x+=6;if(velocity_x>0)velocity_x=0;}
  if(!spring_timer&&!(input&J_A)&&velocity_y< -48)velocity_y=-48;
  velocity_y+=5;if(velocity_y>96)velocity_y=96;
 }
 player_x+=velocity_x;if(player_x<0){player_x=0;velocity_x=0;}
 if(player_x>(int16_t)((current_level.length-16)<<4))player_x=(current_level.length-16)<<4;
 oldfeet=(previous_y>>4)+16;player_y+=velocity_y;newfeet=(player_y>>4)+16;px=player_x>>4;grounded=0;
 if(velocity_y>=0){
  for(i=0;i<current_level.platform_count;i++){
   p=&platforms[i];if(!platform_live(i)||px+12<=p->x||px+3>=p->x+p->w)continue;
   if(oldfeet<=p->y+2&&newfeet>=p->y){player_y=(int16_t)(p->y-16)<<4;velocity_y=0;grounded=1;dash_charge=1;landed=i;break;}
  }
 }
 if(landed!=255){p=&platforms[landed];if(p->kind==2){spring_timer=26;velocity_y=-126;grounded=0;audio_sfx(6);particle_timer=10;}if(p->kind==3&&crumble[landed]==0)crumble[landed]=1;}
 if(player_y<128)player_y=128;
 if(player_y>148*16){deaths++;audio_sfx(2);restart_checkpoint();}
}
void world_tick(void){
 uint8_t i,b,bj,lo,hi;int16_t px=player_x>>4,py=player_y>>4,ex,ey;
 for(i=0;i<current_level.platform_count;i++)if(crumble[i]&&crumble[i]<40){crumble[i]++;if(crumble[i]==40)redraw_platform(i);}
 for(i=0;i<lantern_active_count;){uint8_t li=lantern_active[i];if(lantern_cooldown[li])lantern_cooldown[li]--;if(!lantern_cooldown[li])lantern_active[i]=lantern_active[--lantern_active_count];else i++;}
 lo=px>16?(px-16)>>6:0;hi=(px+16)>>6;if(hi>31)hi=31;
 for(b=lo;b<=hi;b++)for(bj=0;bj<pickup_bucket_counts[b];bj++){
  PickupDef*p;i=pickup_buckets[b][bj];p=&pickups[i];
  if(p->kind!=1&&pickup_taken[i])continue;
  if(p->kind==1&&lantern_cooldown[i])continue;
  if((uint16_t)(p->x-px+16)>32)continue;
  if(overlap(px+2,py+2,12,14,p->x-3,p->y-2,14,18)){
   if(p->kind==1){dash_charge=1;lantern_cooldown[i]=30;if(lantern_active_count<8)lantern_active[lantern_active_count++]=i;if(velocity_y>0)velocity_y=-32;add_combo();audio_sfx(3);}
   else if(p->kind==2){pickup_taken[i]=1;seal_bits[stage_id]|=1<<pickup_seal_id[i];seal_count++;add_combo();audio_sfx(1);save_write();}
   else{pickup_taken[i]=1;if(stars<99)stars++;if(stars%20==0&&health<3)health++;particle_timer=6;audio_sfx(1);}
  }
 }
 for(i=0;i<current_level.enemy_count;i++)if(enemy_alive[i]){
  EnemyDef*e=&enemies[i];if(e->kind!=2&&(frame&1)==0){enemy_offset[i]+=enemy_direction[i];if(enemy_offset[i]>=e->range)enemy_direction[i]=-1;if(enemy_offset[i]<=-e->range)enemy_direction[i]=1;}
  ex=enemy_x(i);ey=enemy_y(i);
  if(overlap(px+3,py+2,10,14,ex+2,ey+3,12,13)){
   if(e->kind!=2&&(dash_timer||(velocity_y>0&&(previous_y>>4)+16<=ey+8))){enemy_alive[i]=0;velocity_y=dash_timer?0:-78;dash_charge=1;add_combo();stars++;audio_sfx(7);}
   else if(e->kind==2&&dash_timer){dash_timer=0;hurt_timer=0;hurt(ex);}else hurt(ex);
  }
 }
 if(!checkpoint_on&&px>=current_level.checkpoint_x-8){checkpoint_on=1;checkpoint_x=current_level.checkpoint_x;health=3;checkpoint_notice=90;particle_timer=15;audio_sfx(3);save_write();}
 if(current_level.boss&&boss_hp){
  ex=current_level.goal_x-48;boss_y=(boss_hp<=3?56:64)+((frame&63)<32?(frame&31)/2:(63-(frame&63))/2);
  if(boss_cooldown)boss_cooldown--;
  /* Arm near the arena. A twelve-tick warm glow tells the next shot. */
  if(px>ex-150){if(boss_shot_timer)boss_shot_timer--;if(!boss_shot_timer){i=projectile_on[0]?1:0;projectile_on[i]=1;projectile_x[i]=ex;projectile_y[i]=boss_hp<=3&&(boss_shot_index&1)?88:108;boss_shot_index++;boss_shot_timer=boss_hp<=3?60:90;}}
  else boss_shot_timer=boss_hp<=3?60:90;
  for(i=0;i<2;i++)if(projectile_on[i]){
   projectile_x[i]-=2;if(projectile_x[i]<(int16_t)camera_x-16)projectile_on[i]=0;
   else if(overlap(px+3,py+2,10,14,projectile_x[i],projectile_y[i],8,12)){if(dash_timer){projectile_on[i]=0;add_combo();}else hurt(projectile_x[i]);}
  }
  if(overlap(px+3,py+2,10,14,ex,boss_y,32,32)){
   if(!boss_cooldown&&(dash_timer||(velocity_y>0&&(previous_y>>4)+16<=boss_y+10))){boss_hp--;boss_cooldown=55;dash_charge=1;dash_timer=0;velocity_y=-94;velocity_x=-36;hurt_timer=25;audio_sfx(7);add_combo();if(!boss_hp){health=3;particle_timer=45;for(i=0;i<2;i++)projectile_on[i]=0;}}
   else if(!boss_cooldown)hurt(ex);
  }
 }
 if((!current_level.boss||!boss_hp)&&px+12>=current_level.goal_x&&py+16>=current_level.goal_y-24&&py+16<=current_level.goal_y+8){
  uint16_t par=level_par(stage_id)*60;uint8_t rank=seal_count==3?(stage_frames<=par?3:2):1;
  current_rank=rank;if(rank>medal[stage_id])medal[stage_id]=rank;if(!best_frames[stage_id]||stage_frames<best_frames[stage_id])best_frames[stage_id]=stage_frames;
  if(stage_id+1>unlocked&&stage_id+1<LEVEL_COUNT)unlocked=stage_id+1;if(stage_id==LEVEL_COUNT-1)completed=1;
  save_write();game_mode=STAGE_CLEAR;audio_scene(6);ui_clear();
 }
}
void game_init(void) BANKED {save_read();audio_init();audio_enable(sound_on);ui_title();}
void game_tick(void) BANKED {
 if(game_mode!=PLAY){ui_tick();return;}
 if(pressed&J_START){ui_pause();return;}
 if(pressed&J_SELECT){deaths++;restart_checkpoint();return;}
 if(stage_frames<65535)stage_frames++;if(hurt_timer)hurt_timer--;if(particle_timer)particle_timer--;if(checkpoint_notice)checkpoint_notice--;if(combo_notice)combo_notice--;
 if(combo_timer)combo_timer--;else combo=0;
 physics();world_tick();if(game_mode!=PLAY)return;
 camera_update();draw_objects();if(health!=old_health||stars!=old_stars||dash_charge!=old_charge||seal_count!=old_seals||combo!=old_combo||(current_level.boss&&camera_x>current_level.goal_x-200&&(!boss_hud||old_boss_hp!=boss_hp))||((checkpoint_notice||combo_notice)&&!hud_banner)||(hud_banner&&!checkpoint_notice&&!combo_notice))hud_update();
}
