/* Generated campaign dispatcher. Content stays in its active bank. */
#pragma bank 3
#include "levels.h"
#include <string.h>

void level_load(uint8_t id, LevelDef *out, PlatformDef *plats,
                PickupDef *picks, EnemyDef *enemies) BANKED {
    level_load_room(id, 0u, out, plats, picks, enemies);
}

void level_load_room(uint8_t id, uint8_t room, LevelDef *out,
                     PlatformDef *plats, PickupDef *picks, EnemyDef *enemies) BANKED {
    if (room >= ROOMS_PER_STAGE) room = 0u;
    if (id >= LEVEL_COUNT) id = 0u;
    switch (id / 3u) {
        case 0u: campaign_0_load(id % 3u, room, out, plats, picks, enemies); break;
        case 1u: campaign_1_load(id % 3u, room, out, plats, picks, enemies); break;
        case 2u: campaign_2_load(id % 3u, room, out, plats, picks, enemies); break;
        case 3u: campaign_3_load(id % 3u, room, out, plats, picks, enemies); break;
        case 4u: campaign_4_load(id % 3u, room, out, plats, picks, enemies); break;
        case 5u: campaign_5_load(id % 3u, room, out, plats, picks, enemies); break;
        case 6u: campaign_6_load(id % 3u, room, out, plats, picks, enemies); break;
        case 7u: campaign_7_load(id % 3u, room, out, plats, picks, enemies); break;
    }
}

void level_info(uint8_t id, LevelDef *out) BANKED {
    if (id >= LEVEL_COUNT) id = 0u;
    switch (id / 3u) {
        case 0u: campaign_0_info(id % 3u, out); break;
        case 1u: campaign_1_info(id % 3u, out); break;
        case 2u: campaign_2_info(id % 3u, out); break;
        case 3u: campaign_3_info(id % 3u, out); break;
        case 4u: campaign_4_info(id % 3u, out); break;
        case 5u: campaign_5_info(id % 3u, out); break;
        case 6u: campaign_6_info(id % 3u, out); break;
        case 7u: campaign_7_info(id % 3u, out); break;
    }
}

void level_intro(uint8_t id, char *line1, char *line2, char *line3) BANKED {
    level_intro_room(id, 0u, line1, line2, line3);
}

void level_intro_room(uint8_t id, uint8_t room, char *line1,
                      char *line2, char *line3) BANKED {
    if (room >= ROOMS_PER_STAGE) room = 0u;
    if (id >= LEVEL_COUNT) id = 0u;
    switch (id / 3u) {
        case 0u: campaign_0_intro(id % 3u, room, line1, line2, line3); break;
        case 1u: campaign_1_intro(id % 3u, room, line1, line2, line3); break;
        case 2u: campaign_2_intro(id % 3u, room, line1, line2, line3); break;
        case 3u: campaign_3_intro(id % 3u, room, line1, line2, line3); break;
        case 4u: campaign_4_intro(id % 3u, room, line1, line2, line3); break;
        case 5u: campaign_5_intro(id % 3u, room, line1, line2, line3); break;
        case 6u: campaign_6_intro(id % 3u, room, line1, line2, line3); break;
        case 7u: campaign_7_intro(id % 3u, room, line1, line2, line3); break;
    }
}

uint16_t level_par(uint8_t id) BANKED {
    if (id >= LEVEL_COUNT) id = 0u;
    switch (id / 3u) {
        case 0u: return campaign_0_par(id % 3u);
        case 1u: return campaign_1_par(id % 3u);
        case 2u: return campaign_2_par(id % 3u);
        case 3u: return campaign_3_par(id % 3u);
        case 4u: return campaign_4_par(id % 3u);
        case 5u: return campaign_5_par(id % 3u);
        case 6u: return campaign_6_par(id % 3u);
        case 7u: return campaign_7_par(id % 3u);
    }
    return 0u;
}

void level_outro(char *line1, char *line2, char *line3) BANKED {
    strcpy(line1, "THE LONG DAWN RISES.");
    strcpy(line2, "THE SKY SEA SINGS.");
    strcpy(line3, "KIP BRINGS IT HOME.");
}
