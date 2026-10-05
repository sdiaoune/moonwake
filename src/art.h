#ifndef MOONWAKE_ART_H
#define MOONWAKE_ART_H
#include <stdint.h>
typedef struct {uint8_t bank,n0,n1;const uint8_t *tiles0,*tiles1,*map,*attr;const uint16_t *pal;} ArtDef;
extern const ArtDef art_worlds[8];
extern const ArtDef art_title;
extern const uint8_t font_tiles[1024],terrain_tiles[256],sprite_tiles[1536];
extern const uint8_t terrain_world_tiles[2048];
extern const unsigned char boss_tiles[4][256];
extern const uint16_t sprite_palettes[32];
#define ART_BANK_FIRST 8
#endif
