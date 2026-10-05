/* Generated from docs/routes.json by tools/build_campaign.py. */
/* Jade Monsoon: three stages, nine continuous rooms. */
#pragma bank 17
#include "levels.h"
#include <string.h>

/* Stage 4, room 1: Lotus After Rain. */
static const PlatformDef platforms_0[] = {
    {0u, 128u, 224u, 0u},
    {248u, 128u, 144u, 0u},
    {416u, 112u, 128u, 0u},
    {568u, 128u, 168u, 0u},
    {760u, 128u, 176u, 0u},
    {960u, 112u, 136u, 0u},
    {1120u, 128u, 160u, 0u},
    {1304u, 112u, 112u, 0u},
    {1440u, 128u, 160u, 0u},
    {272u, 104u, 32u, 2u},
    {320u, 72u, 72u, 1u},
    {408u, 48u, 72u, 1u},
    {792u, 96u, 72u, 1u},
    {888u, 72u, 80u, 1u},
    {1160u, 104u, 32u, 2u},
    {1208u, 72u, 72u, 1u},
    {1304u, 48u, 80u, 1u},
};

static const PickupDef pickups_0[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {272u, 104u, 0u},
    {312u, 104u, 0u},
    {440u, 88u, 0u},
    {480u, 88u, 0u},
    {592u, 104u, 0u},
    {632u, 104u, 0u},
    {784u, 104u, 0u},
    {824u, 104u, 0u},
    {984u, 88u, 0u},
    {1024u, 88u, 0u},
    {1144u, 104u, 0u},
    {1184u, 104u, 0u},
    {1328u, 88u, 0u},
    {1368u, 88u, 0u},
    {1464u, 104u, 0u},
    {1504u, 104u, 0u},
    {336u, 48u, 0u},
    {424u, 24u, 0u},
    {440u, 24u, 2u},
    {808u, 72u, 0u},
    {904u, 48u, 0u},
    {928u, 48u, 2u},
    {1224u, 48u, 0u},
    {1320u, 24u, 0u},
    {1344u, 24u, 2u},
};

static const EnemyDef enemies_0[] = {
    {328u, 112u, 16u, 0u},
    {648u, 112u, 24u, 0u},
    {1032u, 96u, 24u, 0u},
    {1384u, 96u, 8u, 0u},
    {904u, 40u, 16u, 1u},
};

/* Stage 4, room 2: Lotus Library. */
static const PlatformDef platforms_1[] = {
    {0u, 128u, 192u, 0u},
    {216u, 112u, 144u, 0u},
    {384u, 96u, 112u, 0u},
    {520u, 80u, 128u, 0u},
    {680u, 96u, 112u, 1u},
    {816u, 128u, 160u, 0u},
    {1000u, 112u, 104u, 1u},
    {1136u, 96u, 128u, 0u},
    {1288u, 112u, 136u, 0u},
    {1448u, 128u, 144u, 0u},
    {1592u, 128u, 192u, 0u},
    {240u, 96u, 32u, 2u},
    {320u, 72u, 80u, 1u},
    {432u, 64u, 88u, 1u},
    {528u, 72u, 88u, 1u},
    {704u, 128u, 72u, 0u},
    {800u, 128u, 72u, 0u},
    {896u, 128u, 80u, 0u},
    {992u, 104u, 72u, 1u},
    {1160u, 72u, 72u, 1u},
    {1256u, 48u, 80u, 1u},
    {1352u, 48u, 88u, 1u},
    {1448u, 72u, 80u, 1u},
    {1320u, 40u, 64u, 1u},
};

static const PickupDef pickups_1[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {240u, 88u, 0u},
    {280u, 88u, 0u},
    {408u, 72u, 0u},
    {448u, 72u, 0u},
    {544u, 56u, 0u},
    {584u, 56u, 0u},
    {704u, 72u, 0u},
    {744u, 72u, 0u},
    {840u, 104u, 0u},
    {880u, 104u, 0u},
    {1024u, 88u, 0u},
    {1064u, 88u, 0u},
    {1160u, 72u, 0u},
    {1200u, 72u, 0u},
    {1312u, 88u, 0u},
    {1352u, 88u, 0u},
    {1472u, 104u, 0u},
    {1512u, 104u, 0u},
    {1616u, 104u, 0u},
    {1656u, 104u, 0u},
    {256u, 72u, 0u},
    {336u, 48u, 0u},
    {448u, 40u, 0u},
    {544u, 48u, 0u},
    {568u, 48u, 2u},
    {720u, 104u, 0u},
    {816u, 104u, 0u},
    {912u, 104u, 0u},
    {1008u, 80u, 0u},
    {936u, 104u, 2u},
    {1176u, 48u, 0u},
    {1272u, 24u, 0u},
    {1368u, 24u, 0u},
    {1464u, 48u, 0u},
    {1336u, 16u, 0u},
    {1360u, 16u, 2u},
};

static const EnemyDef enemies_1[] = {
    {440u, 80u, 24u, 0u},
    {736u, 80u, 24u, 0u},
    {1052u, 96u, 24u, 0u},
    {1356u, 96u, 24u, 0u},
    {832u, 96u, 16u, 1u},
};

/* Stage 4, room 3: Rainglass Grotto. */
static const PlatformDef platforms_2[] = {
    {0u, 128u, 224u, 0u},
    {256u, 112u, 112u, 1u},
    {392u, 96u, 128u, 1u},
    {560u, 96u, 96u, 1u},
    {688u, 112u, 128u, 0u},
    {848u, 128u, 176u, 0u},
    {1048u, 96u, 104u, 0u},
    {1184u, 80u, 120u, 0u},
    {1328u, 104u, 128u, 0u},
    {1480u, 128u, 144u, 0u},
    {1624u, 128u, 192u, 0u},
    {280u, 128u, 72u, 0u},
    {376u, 128u, 72u, 0u},
    {472u, 128u, 80u, 0u},
    {568u, 104u, 72u, 1u},
    {712u, 88u, 80u, 1u},
    {808u, 64u, 80u, 1u},
    {904u, 72u, 88u, 1u},
    {1000u, 88u, 88u, 1u},
    {1208u, 64u, 32u, 2u},
    {1288u, 48u, 80u, 1u},
    {1400u, 40u, 88u, 1u},
    {1496u, 56u, 88u, 1u},
};

static const PickupDef pickups_2[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {280u, 88u, 0u},
    {320u, 88u, 0u},
    {416u, 72u, 0u},
    {456u, 72u, 0u},
    {584u, 72u, 0u},
    {624u, 72u, 0u},
    {712u, 88u, 0u},
    {752u, 88u, 0u},
    {872u, 104u, 0u},
    {912u, 104u, 0u},
    {1072u, 72u, 0u},
    {1112u, 72u, 0u},
    {1208u, 56u, 0u},
    {1248u, 56u, 0u},
    {1352u, 80u, 0u},
    {1392u, 80u, 0u},
    {1504u, 104u, 0u},
    {1544u, 104u, 0u},
    {1648u, 104u, 0u},
    {1688u, 104u, 0u},
    {296u, 104u, 0u},
    {392u, 104u, 0u},
    {488u, 104u, 0u},
    {584u, 80u, 0u},
    {512u, 104u, 2u},
    {728u, 64u, 0u},
    {824u, 40u, 0u},
    {920u, 48u, 0u},
    {1016u, 64u, 0u},
    {1040u, 64u, 2u},
    {1224u, 40u, 0u},
    {1304u, 24u, 0u},
    {1416u, 16u, 0u},
    {1512u, 32u, 0u},
    {1536u, 32u, 2u},
};

static const EnemyDef enemies_2[] = {
    {456u, 80u, 24u, 0u},
    {752u, 96u, 24u, 0u},
    {1100u, 80u, 24u, 0u},
    {1392u, 88u, 24u, 0u},
    {840u, 32u, 16u, 1u},
};

/* Stage 5, room 1: Rainbell Canopy. */
static const PlatformDef platforms_3[] = {
    {0u, 128u, 192u, 0u},
    {216u, 112u, 120u, 0u},
    {360u, 96u, 112u, 0u},
    {496u, 112u, 144u, 0u},
    {664u, 128u, 192u, 0u},
    {880u, 112u, 128u, 0u},
    {1032u, 96u, 120u, 0u},
    {1176u, 112u, 136u, 0u},
    {1336u, 128u, 144u, 0u},
    {1504u, 128u, 160u, 0u},
    {240u, 80u, 64u, 1u},
    {328u, 56u, 88u, 3u},
    {696u, 96u, 64u, 1u},
    {784u, 72u, 72u, 3u},
    {880u, 48u, 80u, 1u},
    {1200u, 80u, 64u, 3u},
    {1288u, 56u, 96u, 1u},
};

static const PickupDef pickups_3[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {240u, 88u, 0u},
    {280u, 88u, 0u},
    {384u, 72u, 0u},
    {424u, 72u, 0u},
    {520u, 88u, 0u},
    {560u, 88u, 0u},
    {688u, 104u, 0u},
    {728u, 104u, 0u},
    {904u, 88u, 0u},
    {944u, 88u, 0u},
    {1056u, 72u, 0u},
    {1096u, 72u, 0u},
    {1200u, 88u, 0u},
    {1240u, 88u, 0u},
    {1360u, 104u, 0u},
    {1400u, 104u, 0u},
    {1528u, 104u, 0u},
    {1568u, 104u, 0u},
    {256u, 56u, 0u},
    {344u, 32u, 0u},
    {368u, 32u, 2u},
    {712u, 72u, 0u},
    {800u, 48u, 0u},
    {896u, 24u, 0u},
    {856u, 48u, 1u},
    {920u, 24u, 2u},
    {1216u, 56u, 0u},
    {1304u, 32u, 0u},
    {1336u, 32u, 2u},
};

static const EnemyDef enemies_3[] = {
    {280u, 96u, 16u, 0u},
    {568u, 96u, 24u, 0u},
    {952u, 96u, 16u, 0u},
    {1416u, 112u, 24u, 0u},
    {832u, 40u, 16u, 1u},
    {1104u, 56u, 16u, 1u},
};

/* Stage 5, room 2: Bellflower Loops. */
static const PlatformDef platforms_4[] = {
    {0u, 128u, 192u, 0u},
    {216u, 112u, 128u, 0u},
    {376u, 96u, 104u, 0u},
    {504u, 112u, 136u, 0u},
    {664u, 128u, 112u, 0u},
    {808u, 112u, 160u, 0u},
    {1000u, 96u, 112u, 0u},
    {1144u, 80u, 104u, 1u},
    {1272u, 104u, 144u, 1u},
    {1440u, 128u, 144u, 0u},
    {1584u, 128u, 192u, 0u},
    {240u, 88u, 72u, 1u},
    {336u, 64u, 80u, 1u},
    {432u, 64u, 88u, 1u},
    {528u, 88u, 80u, 1u},
    {400u, 56u, 64u, 1u},
    {688u, 104u, 80u, 1u},
    {784u, 88u, 64u, 3u},
    {880u, 80u, 88u, 1u},
    {976u, 88u, 88u, 1u},
    {1168u, 128u, 72u, 0u},
    {1264u, 128u, 72u, 0u},
    {1360u, 128u, 80u, 0u},
    {1456u, 104u, 72u, 1u},
};

static const PickupDef pickups_4[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {240u, 88u, 0u},
    {280u, 88u, 0u},
    {400u, 72u, 0u},
    {440u, 72u, 0u},
    {528u, 88u, 0u},
    {568u, 88u, 0u},
    {688u, 104u, 0u},
    {728u, 104u, 0u},
    {832u, 88u, 0u},
    {872u, 88u, 0u},
    {1024u, 72u, 0u},
    {1064u, 72u, 0u},
    {1168u, 56u, 0u},
    {1208u, 56u, 0u},
    {1296u, 80u, 0u},
    {1336u, 80u, 0u},
    {1464u, 104u, 0u},
    {1504u, 104u, 0u},
    {1608u, 104u, 0u},
    {1648u, 104u, 0u},
    {256u, 64u, 0u},
    {352u, 40u, 0u},
    {448u, 40u, 0u},
    {544u, 64u, 0u},
    {416u, 32u, 0u},
    {440u, 32u, 2u},
    {704u, 80u, 0u},
    {800u, 64u, 0u},
    {896u, 56u, 0u},
    {992u, 64u, 0u},
    {776u, 72u, 1u},
    {872u, 64u, 1u},
    {1016u, 64u, 2u},
    {1184u, 104u, 0u},
    {1280u, 104u, 0u},
    {1376u, 104u, 0u},
    {1472u, 80u, 0u},
    {1400u, 104u, 2u},
};

static const EnemyDef enemies_4[] = {
    {428u, 80u, 24u, 0u},
    {720u, 112u, 24u, 0u},
    {1056u, 80u, 24u, 0u},
    {1344u, 88u, 24u, 0u},
    {816u, 56u, 16u, 1u},
};

/* Stage 5, room 3: Mothwing Boughs. */
static const PlatformDef platforms_5[] = {
    {0u, 128u, 224u, 0u},
    {248u, 112u, 104u, 0u},
    {384u, 96u, 128u, 0u},
    {544u, 80u, 112u, 0u},
    {680u, 96u, 128u, 0u},
    {840u, 112u, 144u, 0u},
    {1024u, 128u, 104u, 0u},
    {1160u, 104u, 120u, 0u},
    {1304u, 96u, 136u, 0u},
    {1464u, 128u, 144u, 0u},
    {1608u, 128u, 192u, 0u},
    {272u, 88u, 80u, 1u},
    {368u, 64u, 80u, 1u},
    {464u, 72u, 88u, 1u},
    {560u, 72u, 88u, 1u},
    {704u, 72u, 72u, 1u},
    {800u, 48u, 80u, 1u},
    {896u, 48u, 88u, 1u},
    {992u, 72u, 80u, 1u},
    {864u, 40u, 64u, 1u},
    {1184u, 80u, 80u, 1u},
    {1280u, 64u, 64u, 3u},
    {1376u, 56u, 88u, 1u},
    {1472u, 80u, 88u, 1u},
};

static const PickupDef pickups_5[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {272u, 88u, 0u},
    {312u, 88u, 0u},
    {408u, 72u, 0u},
    {448u, 72u, 0u},
    {568u, 56u, 0u},
    {608u, 56u, 0u},
    {704u, 72u, 0u},
    {744u, 72u, 0u},
    {864u, 88u, 0u},
    {904u, 88u, 0u},
    {1048u, 104u, 0u},
    {1088u, 104u, 0u},
    {1184u, 80u, 0u},
    {1224u, 80u, 0u},
    {1328u, 72u, 0u},
    {1368u, 72u, 0u},
    {1488u, 104u, 0u},
    {1528u, 104u, 0u},
    {1632u, 104u, 0u},
    {1672u, 104u, 0u},
    {288u, 64u, 0u},
    {384u, 40u, 0u},
    {480u, 48u, 0u},
    {576u, 48u, 0u},
    {600u, 48u, 2u},
    {720u, 48u, 0u},
    {816u, 24u, 0u},
    {912u, 24u, 0u},
    {1008u, 48u, 0u},
    {880u, 16u, 0u},
    {904u, 16u, 2u},
    {1200u, 56u, 0u},
    {1296u, 40u, 0u},
    {1392u, 32u, 0u},
    {1488u, 56u, 0u},
    {1272u, 48u, 1u},
    {1368u, 40u, 1u},
    {1512u, 56u, 2u},
};

static const EnemyDef enemies_5[] = {
    {448u, 80u, 24u, 0u},
    {744u, 80u, 24u, 0u},
    {1076u, 112u, 24u, 0u},
    {1372u, 80u, 24u, 0u},
    {832u, 24u, 16u, 1u},
};

/* Stage 6, room 1: Glasswater Run. */
static const PlatformDef platforms_6[] = {
    {0u, 128u, 224u, 0u},
    {256u, 112u, 128u, 0u},
    {424u, 128u, 192u, 0u},
    {656u, 128u, 176u, 0u},
    {880u, 112u, 128u, 0u},
    {1048u, 96u, 112u, 2u},
    {1200u, 112u, 144u, 0u},
    {1384u, 128u, 160u, 0u},
    {1568u, 128u, 160u, 0u},
    {272u, 80u, 64u, 1u},
    {368u, 56u, 96u, 1u},
    {680u, 96u, 64u, 1u},
    {776u, 72u, 64u, 1u},
    {872u, 48u, 72u, 1u},
    {1216u, 80u, 72u, 1u},
    {1320u, 56u, 80u, 1u},
    {1440u, 56u, 64u, 1u},
};

static const PickupDef pickups_6[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {280u, 88u, 0u},
    {320u, 88u, 0u},
    {448u, 104u, 0u},
    {488u, 104u, 0u},
    {680u, 104u, 0u},
    {720u, 104u, 0u},
    {904u, 88u, 0u},
    {944u, 88u, 0u},
    {1072u, 72u, 0u},
    {1112u, 72u, 0u},
    {1224u, 88u, 0u},
    {1264u, 88u, 0u},
    {1408u, 104u, 0u},
    {1448u, 104u, 0u},
    {1592u, 104u, 0u},
    {1632u, 104u, 0u},
    {288u, 56u, 0u},
    {384u, 32u, 0u},
    {416u, 32u, 2u},
    {696u, 72u, 0u},
    {792u, 48u, 0u},
    {888u, 24u, 0u},
    {752u, 64u, 1u},
    {848u, 40u, 1u},
    {904u, 24u, 2u},
    {1232u, 56u, 0u},
    {1336u, 32u, 0u},
    {1456u, 32u, 0u},
    {1304u, 56u, 1u},
    {1416u, 40u, 1u},
    {1464u, 32u, 2u},
    {864u, 88u, 1u},
    {1360u, 88u, 1u},
};

static const EnemyDef enemies_6[] = {
    {336u, 96u, 16u, 0u},
    {520u, 112u, 32u, 0u},
    {752u, 112u, 24u, 0u},
    {1120u, 80u, 8u, 0u},
    {1480u, 112u, 24u, 0u},
    {1304u, 40u, 24u, 1u},
};

/* Stage 6, room 2: Moss Lantern Road. */
static const PlatformDef platforms_7[] = {
    {0u, 128u, 192u, 0u},
    {224u, 128u, 144u, 0u},
    {408u, 112u, 112u, 0u},
    {552u, 96u, 128u, 0u},
    {704u, 112u, 112u, 1u},
    {856u, 128u, 160u, 0u},
    {1056u, 112u, 104u, 1u},
    {1200u, 96u, 120u, 0u},
    {1352u, 112u, 128u, 0u},
    {1504u, 128u, 144u, 0u},
    {1648u, 128u, 192u, 0u},
    {248u, 104u, 80u, 1u},
    {344u, 80u, 80u, 1u},
    {440u, 88u, 88u, 1u},
    {536u, 88u, 88u, 1u},
    {728u, 128u, 72u, 0u},
    {824u, 128u, 72u, 0u},
    {920u, 128u, 80u, 0u},
    {1016u, 104u, 72u, 1u},
    {1224u, 72u, 72u, 1u},
    {1320u, 48u, 80u, 1u},
    {1416u, 48u, 88u, 1u},
    {1512u, 72u, 80u, 1u},
    {1384u, 40u, 64u, 1u},
};

static const PickupDef pickups_7[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {248u, 104u, 0u},
    {288u, 104u, 0u},
    {432u, 88u, 0u},
    {472u, 88u, 0u},
    {576u, 72u, 0u},
    {616u, 72u, 0u},
    {728u, 88u, 0u},
    {768u, 88u, 0u},
    {880u, 104u, 0u},
    {920u, 104u, 0u},
    {1080u, 88u, 0u},
    {1120u, 88u, 0u},
    {1224u, 72u, 0u},
    {1264u, 72u, 0u},
    {1376u, 88u, 0u},
    {1416u, 88u, 0u},
    {1528u, 104u, 0u},
    {1568u, 104u, 0u},
    {1672u, 104u, 0u},
    {1712u, 104u, 0u},
    {264u, 80u, 0u},
    {360u, 56u, 0u},
    {456u, 64u, 0u},
    {552u, 64u, 0u},
    {336u, 64u, 1u},
    {432u, 72u, 1u},
    {576u, 64u, 2u},
    {744u, 104u, 0u},
    {840u, 104u, 0u},
    {936u, 104u, 0u},
    {1032u, 80u, 0u},
    {960u, 104u, 2u},
    {1240u, 48u, 0u},
    {1336u, 24u, 0u},
    {1432u, 24u, 0u},
    {1528u, 48u, 0u},
    {1400u, 16u, 0u},
    {1424u, 16u, 2u},
};

static const EnemyDef enemies_7[] = {
    {464u, 96u, 24u, 0u},
    {760u, 96u, 24u, 0u},
    {1108u, 96u, 24u, 0u},
    {1416u, 96u, 24u, 0u},
    {856u, 96u, 16u, 1u},
};

/* Stage 6, room 3: Rainbell Crown. */
static const PlatformDef platforms_8[] = {
    {0u, 128u, 224u, 0u},
    {248u, 112u, 112u, 0u},
    {392u, 96u, 128u, 0u},
    {544u, 80u, 104u, 0u},
    {680u, 96u, 112u, 0u},
    {824u, 112u, 144u, 0u},
    {1000u, 128u, 104u, 0u},
    {1144u, 112u, 120u, 0u},
    {1296u, 128u, 128u, 0u},
    {1424u, 128u, 144u, 0u},
    {1568u, 128u, 224u, 0u},
    {272u, 96u, 32u, 2u},
    {352u, 72u, 80u, 1u},
    {464u, 64u, 88u, 1u},
    {560u, 72u, 88u, 1u},
    {704u, 72u, 80u, 1u},
    {800u, 48u, 80u, 1u},
    {896u, 56u, 88u, 1u},
    {992u, 72u, 88u, 1u},
    {1168u, 88u, 64u, 1u},
    {1264u, 64u, 80u, 1u},
    {1216u, 56u, 64u, 1u},
};

static const PickupDef pickups_8[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {272u, 88u, 0u},
    {312u, 88u, 0u},
    {416u, 72u, 0u},
    {456u, 72u, 0u},
    {568u, 56u, 0u},
    {608u, 56u, 0u},
    {704u, 72u, 0u},
    {744u, 72u, 0u},
    {848u, 88u, 0u},
    {888u, 88u, 0u},
    {1024u, 104u, 0u},
    {1064u, 104u, 0u},
    {1168u, 88u, 0u},
    {1208u, 88u, 0u},
    {1320u, 104u, 0u},
    {1360u, 104u, 0u},
    {1448u, 104u, 0u},
    {1488u, 104u, 0u},
    {288u, 72u, 0u},
    {368u, 48u, 0u},
    {480u, 40u, 0u},
    {576u, 48u, 0u},
    {600u, 48u, 2u},
    {720u, 48u, 0u},
    {816u, 24u, 0u},
    {912u, 32u, 0u},
    {1008u, 48u, 0u},
    {1032u, 48u, 2u},
    {1184u, 64u, 0u},
    {1280u, 40u, 0u},
    {1232u, 32u, 0u},
    {1256u, 32u, 2u},
};

static const EnemyDef enemies_8[] = {
    {456u, 80u, 24u, 0u},
    {736u, 80u, 24u, 0u},
    {1052u, 112u, 24u, 0u},
    {832u, 24u, 16u, 1u},
};

static const LevelDef definitions[9] = {
    {"Lotus After Rain", 1600u, 24u, 1552u, 840u, 1u, 112u, 128u, 128u, 0u, 17u, 27u, 5u, 0u},
    {"Lotus Library", 1784u, 24u, 1736u, 896u, 1u, 112u, 128u, 128u, 0u, 24u, 38u, 5u, 0u},
    {"Rainglass Grotto", 1816u, 24u, 1768u, 936u, 1u, 112u, 128u, 128u, 0u, 23u, 37u, 5u, 0u},
    {"Rainbell Canopy", 1664u, 24u, 1616u, 760u, 1u, 112u, 128u, 128u, 0u, 17u, 31u, 6u, 0u},
    {"Bellflower Loops", 1776u, 24u, 1728u, 888u, 1u, 112u, 128u, 112u, 0u, 24u, 40u, 5u, 0u},
    {"Mothwing Boughs", 1800u, 24u, 1752u, 912u, 1u, 112u, 128u, 112u, 0u, 24u, 40u, 5u, 0u},
    {"Glasswater Run", 1728u, 24u, 1680u, 800u, 1u, 112u, 128u, 128u, 0u, 17u, 35u, 6u, 0u},
    {"Moss Lantern Road", 1840u, 24u, 1792u, 936u, 1u, 112u, 128u, 128u, 0u, 24u, 40u, 5u, 0u},
    {"Rainbell Crown", 1792u, 24u, 1744u, 1496u, 1u, 112u, 128u, 128u, 1u, 22u, 34u, 4u, 0u},
};

static const PlatformDef * const platforms_sets[9] = {
    platforms_0, platforms_1, platforms_2, platforms_3, platforms_4, platforms_5, platforms_6, platforms_7, platforms_8
};

static const PickupDef * const pickups_sets[9] = {
    pickups_0, pickups_1, pickups_2, pickups_3, pickups_4, pickups_5, pickups_6, pickups_7, pickups_8
};

static const EnemyDef * const enemies_sets[9] = {
    enemies_0, enemies_1, enemies_2, enemies_3, enemies_4, enemies_5, enemies_6, enemies_7, enemies_8
};

static const char intros[9][3][21] = {
    {"RAIN WAKES LOTUS.", "SMALL SPRINGS SING.", "BOUNCE TOWARD LIGHT."},
    {"LOTUS LIBRARY", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
    {"RAINGLASS GROTTO", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
    {"RAINBELLS KEEP TIME.", "BRITTLE LEAVES FALL.", "KEEP YOUR FEET LIGHT"},
    {"BELLFLOWER LOOPS", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
    {"MOTHWING BOUGHS", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
    {"THE RIVER IS GLASS.", "LIGHT SKIPS ON RAIN.", "RUN WITH THE CURRENT"},
    {"MOSS LANTERN ROAD", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
    {"RAINBELL CROWN", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
};

static const uint16_t pars[3] = {
    100u, 100u, 110u
};

static uint8_t room_index(uint8_t local_stage, uint8_t room) {
    if (local_stage >= 3u) local_stage = 0u;
    if (room >= ROOMS_PER_STAGE) room = 0u;
    return local_stage * ROOMS_PER_STAGE + room;
}

void campaign_1_load(uint8_t local_stage, uint8_t room, LevelDef *out,
                       PlatformDef *plats, PickupDef *picks, EnemyDef *enemies) BANKED {
    uint8_t index = room_index(local_stage, room);
    memcpy(out, &definitions[index], sizeof(LevelDef));
    memcpy(plats, platforms_sets[index], (uint16_t)out->platform_count * sizeof(PlatformDef));
    memcpy(picks, pickups_sets[index], (uint16_t)out->pickup_count * sizeof(PickupDef));
    memcpy(enemies, enemies_sets[index], (uint16_t)out->enemy_count * sizeof(EnemyDef));
}

void campaign_1_info(uint8_t local_stage, LevelDef *out) BANKED {
    memcpy(out, &definitions[room_index(local_stage, 0u)], sizeof(LevelDef));
}

void campaign_1_intro(uint8_t local_stage, uint8_t room, char *line1,
                        char *line2, char *line3) BANKED {
    uint8_t index = room_index(local_stage, room);
    strcpy(line1, intros[index][0]);
    strcpy(line2, intros[index][1]);
    strcpy(line3, intros[index][2]);
}

uint16_t campaign_1_par(uint8_t local_stage) BANKED {
    if (local_stage >= 3u) local_stage = 0u;
    return pars[local_stage];
}
