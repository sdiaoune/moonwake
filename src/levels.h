#ifndef MOONWAKE_LEVELS_H
#define MOONWAKE_LEVELS_H

#include <gb/gb.h>
#include <stdint.h>

#define LEVEL_COUNT 12u
#define MAX_PLATFORMS 48u
#define MAX_PICKUPS 64u
#define MAX_ENEMIES 12u
#define LEVEL_MAX_PLATFORMS MAX_PLATFORMS
#define LEVEL_MAX_PICKUPS MAX_PICKUPS
#define LEVEL_MAX_ENEMIES MAX_ENEMIES

#define PLATFORM_SOLID 0u
#define PLATFORM_ONE_WAY 1u
#define PLATFORM_SPRING 2u
#define PLATFORM_CRUMBLE 3u
#define PICKUP_STAR 0u
#define PICKUP_LANTERN 1u
#define PICKUP_SEAL 2u
#define ENEMY_BEETLE 0u
#define ENEMY_OWL 1u
#define ENEMY_THORN 2u

typedef struct LevelDef {
    char name[19];
    uint16_t length, spawn_x, goal_x, checkpoint_x;
    uint8_t biome, spawn_y, goal_y, checkpoint_y, boss;
    uint8_t platform_count, pickup_count, enemy_count;
} LevelDef;

typedef struct PlatformDef {
    uint16_t x;
    uint8_t y, w, kind;
} PlatformDef;

typedef struct PickupDef {
    uint16_t x;
    uint8_t y, kind;
} PickupDef;

typedef struct EnemyDef {
    uint16_t x;
    uint8_t y, range, kind;
} EnemyDef;

void level_load(uint8_t id, LevelDef *out, PlatformDef *plats,
                PickupDef *picks, EnemyDef *enemies) BANKED;
/* Three NUL-terminated lines, each at most 20 printable characters.
 * Caller supplies three buffers of at least 21 bytes. */
void level_info(uint8_t id, LevelDef *out) BANKED;
void level_intro(uint8_t id, char *line1, char *line2, char *line3) BANKED;
void level_outro(char *line1, char *line2, char *line3) BANKED;
uint16_t level_par(uint8_t id) BANKED;

#endif
