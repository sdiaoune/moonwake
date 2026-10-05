#ifndef MOONWAKE_MUSIC_H
#define MOONWAKE_MUSIC_H
#include <gb/gb.h>
#include <stdint.h>
/* Native CGB APU; call audio_tick once per video frame.
 * Scenes: 0 title, 1 harbor, 2 monsoon, 3 engines, 4 moonwhale,
 * 5 boss, 6 clear, 7 ending.
 * SFX: 0 jump, 1 star, 2 hurt, 3 lantern, 4 dash, 5 clear,
 * 6 spring, 7 boss hit. Mute preserves score position. */
void audio_init(void) BANKED;
void audio_scene(uint8_t scene) BANKED;
void audio_tick(uint8_t energy) BANKED;
void audio_sfx(uint8_t effect) BANKED;
void audio_enable(uint8_t enabled) BANKED;
#endif
