/* Generated from docs/routes.json by tools/build_campaign.py. */
/* Moonwhale: three stages, nine continuous rooms. */
#pragma bank 19
#include "levels.h"
#include <string.h>

/* Stage 10, room 1: Whale in the Sky. */
static const PlatformDef platforms_0[] = {
    {0u, 128u, 224u, 0u},
    {224u, 128u, 184u, 0u},
    {432u, 112u, 152u, 0u},
    {608u, 128u, 184u, 0u},
    {816u, 128u, 184u, 0u},
    {1024u, 112u, 144u, 0u},
    {1192u, 128u, 184u, 0u},
    {1400u, 128u, 200u, 0u},
    {248u, 96u, 72u, 1u},
    {344u, 72u, 88u, 1u},
    {840u, 96u, 72u, 1u},
    {936u, 72u, 88u, 1u},
    {1216u, 96u, 72u, 1u},
    {1312u, 72u, 88u, 1u},
};

static const PickupDef pickups_0[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {248u, 104u, 0u},
    {288u, 104u, 0u},
    {456u, 88u, 0u},
    {496u, 88u, 0u},
    {632u, 104u, 0u},
    {672u, 104u, 0u},
    {840u, 104u, 0u},
    {880u, 104u, 0u},
    {1048u, 88u, 0u},
    {1088u, 88u, 0u},
    {1216u, 104u, 0u},
    {1256u, 104u, 0u},
    {1424u, 104u, 0u},
    {1464u, 104u, 0u},
    {264u, 72u, 0u},
    {360u, 48u, 0u},
    {384u, 48u, 2u},
    {856u, 72u, 0u},
    {952u, 48u, 0u},
    {976u, 48u, 2u},
    {1232u, 72u, 0u},
    {1328u, 48u, 0u},
    {1360u, 48u, 2u},
};

static const EnemyDef enemies_0[] = {
    {520u, 96u, 24u, 0u},
    {712u, 112u, 24u, 0u},
    {1104u, 96u, 16u, 0u},
    {1496u, 112u, 24u, 0u},
    {992u, 40u, 16u, 1u},
};

/* Stage 10, room 2: Pearlspine Garden. */
static const PlatformDef platforms_1[] = {
    {0u, 128u, 224u, 0u},
    {248u, 128u, 144u, 0u},
    {416u, 112u, 112u, 0u},
    {560u, 96u, 128u, 0u},
    {712u, 112u, 104u, 1u},
    {840u, 128u, 160u, 0u},
    {1024u, 96u, 112u, 1u},
    {1168u, 80u, 120u, 0u},
    {1312u, 104u, 128u, 0u},
    {1464u, 128u, 144u, 0u},
    {1608u, 128u, 192u, 0u},
    {272u, 104u, 80u, 1u},
    {368u, 80u, 80u, 1u},
    {464u, 88u, 88u, 1u},
    {560u, 88u, 88u, 1u},
    {736u, 128u, 72u, 0u},
    {832u, 128u, 72u, 0u},
    {928u, 128u, 80u, 0u},
    {1024u, 104u, 72u, 1u},
    {1192u, 64u, 32u, 2u},
    {1272u, 48u, 80u, 1u},
    {1384u, 40u, 88u, 1u},
    {1480u, 56u, 88u, 1u},
};

static const PickupDef pickups_1[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {272u, 104u, 0u},
    {312u, 104u, 0u},
    {440u, 88u, 0u},
    {480u, 88u, 0u},
    {584u, 72u, 0u},
    {624u, 72u, 0u},
    {736u, 88u, 0u},
    {776u, 88u, 0u},
    {864u, 104u, 0u},
    {904u, 104u, 0u},
    {1048u, 72u, 0u},
    {1088u, 72u, 0u},
    {1192u, 56u, 0u},
    {1232u, 56u, 0u},
    {1336u, 80u, 0u},
    {1376u, 80u, 0u},
    {1488u, 104u, 0u},
    {1528u, 104u, 0u},
    {1632u, 104u, 0u},
    {1672u, 104u, 0u},
    {288u, 80u, 0u},
    {384u, 56u, 0u},
    {480u, 64u, 0u},
    {576u, 64u, 0u},
    {600u, 64u, 2u},
    {752u, 104u, 0u},
    {848u, 104u, 0u},
    {944u, 104u, 0u},
    {1040u, 80u, 0u},
    {968u, 104u, 2u},
    {1208u, 40u, 0u},
    {1288u, 24u, 0u},
    {1400u, 16u, 0u},
    {1496u, 32u, 0u},
    {1520u, 32u, 2u},
};

static const EnemyDef enemies_1[] = {
    {472u, 96u, 24u, 0u},
    {764u, 96u, 24u, 0u},
    {1080u, 80u, 24u, 0u},
    {1376u, 88u, 24u, 0u},
    {864u, 96u, 16u, 1u},
};

/* Stage 10, room 3: Moonfoam Hollows. */
static const PlatformDef platforms_2[] = {
    {0u, 128u, 192u, 0u},
    {216u, 112u, 128u, 1u},
    {368u, 96u, 112u, 1u},
    {512u, 80u, 144u, 1u},
    {680u, 96u, 104u, 0u},
    {816u, 128u, 160u, 0u},
    {1008u, 112u, 112u, 0u},
    {1152u, 96u, 128u, 0u},
    {1304u, 112u, 120u, 0u},
    {1448u, 128u, 144u, 0u},
    {1592u, 128u, 192u, 0u},
    {240u, 128u, 72u, 0u},
    {336u, 128u, 72u, 0u},
    {432u, 128u, 80u, 0u},
    {528u, 104u, 72u, 1u},
    {704u, 72u, 72u, 1u},
    {800u, 48u, 80u, 1u},
    {896u, 48u, 88u, 1u},
    {992u, 72u, 80u, 1u},
    {864u, 40u, 64u, 1u},
    {1176u, 72u, 80u, 1u},
    {1272u, 48u, 80u, 1u},
    {1368u, 56u, 88u, 1u},
    {1464u, 72u, 88u, 1u},
};

static const PickupDef pickups_2[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {240u, 88u, 0u},
    {280u, 88u, 0u},
    {392u, 72u, 0u},
    {432u, 72u, 0u},
    {536u, 56u, 0u},
    {576u, 56u, 0u},
    {704u, 72u, 0u},
    {744u, 72u, 0u},
    {840u, 104u, 0u},
    {880u, 104u, 0u},
    {1032u, 88u, 0u},
    {1072u, 88u, 0u},
    {1176u, 72u, 0u},
    {1216u, 72u, 0u},
    {1328u, 88u, 0u},
    {1368u, 88u, 0u},
    {1472u, 104u, 0u},
    {1512u, 104u, 0u},
    {1616u, 104u, 0u},
    {1656u, 104u, 0u},
    {256u, 104u, 0u},
    {352u, 104u, 0u},
    {448u, 104u, 0u},
    {544u, 80u, 0u},
    {472u, 104u, 2u},
    {720u, 48u, 0u},
    {816u, 24u, 0u},
    {912u, 24u, 0u},
    {1008u, 48u, 0u},
    {880u, 16u, 0u},
    {904u, 16u, 2u},
    {1192u, 48u, 0u},
    {1288u, 24u, 0u},
    {1384u, 32u, 0u},
    {1480u, 48u, 0u},
    {1264u, 32u, 1u},
    {1360u, 40u, 1u},
    {1504u, 48u, 2u},
};

static const EnemyDef enemies_2[] = {
    {424u, 80u, 24u, 0u},
    {732u, 80u, 24u, 0u},
    {1064u, 96u, 24u, 0u},
    {1364u, 96u, 24u, 0u},
    {832u, 24u, 16u, 1u},
};

/* Stage 11, room 1: Stardrift Current. */
static const PlatformDef platforms_3[] = {
    {0u, 128u, 224u, 0u},
    {256u, 112u, 128u, 0u},
    {424u, 96u, 112u, 0u},
    {576u, 112u, 128u, 0u},
    {744u, 128u, 192u, 0u},
    {976u, 112u, 128u, 0u},
    {1200u, 96u, 96u, 0u},
    {1296u, 112u, 128u, 0u},
    {1464u, 128u, 112u, 0u},
    {1600u, 128u, 160u, 0u},
    {280u, 80u, 64u, 1u},
    {376u, 56u, 80u, 1u},
    {776u, 96u, 64u, 1u},
    {872u, 72u, 64u, 1u},
    {976u, 48u, 88u, 1u},
    {1168u, 64u, 64u, 1u},
    {1264u, 48u, 64u, 1u},
    {1376u, 48u, 80u, 1u},
};

static const PickupDef pickups_3[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {280u, 88u, 0u},
    {320u, 88u, 0u},
    {448u, 72u, 0u},
    {488u, 72u, 0u},
    {600u, 88u, 0u},
    {640u, 88u, 0u},
    {768u, 104u, 0u},
    {808u, 104u, 0u},
    {1000u, 88u, 0u},
    {1040u, 88u, 0u},
    {1168u, 72u, 0u},
    {1208u, 72u, 0u},
    {1320u, 88u, 0u},
    {1360u, 88u, 0u},
    {1488u, 104u, 0u},
    {1528u, 104u, 0u},
    {1624u, 104u, 0u},
    {1664u, 104u, 0u},
    {296u, 56u, 0u},
    {392u, 32u, 0u},
    {416u, 32u, 2u},
    {792u, 72u, 0u},
    {888u, 48u, 0u},
    {992u, 24u, 0u},
    {848u, 64u, 1u},
    {952u, 40u, 1u},
    {1024u, 24u, 2u},
    {1184u, 40u, 0u},
    {1280u, 24u, 0u},
    {1392u, 24u, 0u},
    {1240u, 40u, 1u},
    {1344u, 32u, 1u},
    {1424u, 24u, 2u},
    {952u, 88u, 1u},
    {1440u, 88u, 1u},
    {1144u, 64u, 1u},
};

static const EnemyDef enemies_3[] = {
    {336u, 96u, 16u, 0u},
    {648u, 96u, 16u, 0u},
    {848u, 112u, 24u, 0u},
    {1056u, 96u, 16u, 0u},
    {1376u, 96u, 16u, 0u},
    {1688u, 112u, 24u, 0u},
    {920u, 40u, 24u, 1u},
    {1336u, 32u, 16u, 1u},
};

/* Stage 11, room 2: Manta Slipstream. */
static const PlatformDef platforms_4[] = {
    {0u, 128u, 224u, 0u},
    {256u, 112u, 112u, 0u},
    {408u, 96u, 120u, 0u},
    {560u, 112u, 112u, 0u},
    {712u, 128u, 128u, 0u},
    {880u, 112u, 160u, 0u},
    {1080u, 96u, 104u, 0u},
    {1216u, 80u, 128u, 0u},
    {1376u, 104u, 112u, 0u},
    {1512u, 128u, 144u, 0u},
    {1656u, 128u, 192u, 0u},
    {280u, 88u, 80u, 1u},
    {376u, 64u, 80u, 1u},
    {472u, 72u, 88u, 1u},
    {568u, 88u, 88u, 1u},
    {736u, 104u, 80u, 1u},
    {832u, 80u, 80u, 1u},
    {928u, 88u, 88u, 1u},
    {1024u, 88u, 88u, 1u},
    {1240u, 56u, 72u, 1u},
    {1336u, 40u, 80u, 1u},
    {1432u, 40u, 88u, 1u},
    {1528u, 56u, 80u, 1u},
    {1400u, 40u, 64u, 1u},
};

static const PickupDef pickups_4[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {280u, 88u, 0u},
    {320u, 88u, 0u},
    {432u, 72u, 0u},
    {472u, 72u, 0u},
    {584u, 88u, 0u},
    {624u, 88u, 0u},
    {736u, 104u, 0u},
    {776u, 104u, 0u},
    {904u, 88u, 0u},
    {944u, 88u, 0u},
    {1104u, 72u, 0u},
    {1144u, 72u, 0u},
    {1240u, 56u, 0u},
    {1280u, 56u, 0u},
    {1400u, 80u, 0u},
    {1440u, 80u, 0u},
    {1536u, 104u, 0u},
    {1576u, 104u, 0u},
    {1680u, 104u, 0u},
    {1720u, 104u, 0u},
    {296u, 64u, 0u},
    {392u, 40u, 0u},
    {488u, 48u, 0u},
    {584u, 64u, 0u},
    {368u, 48u, 1u},
    {464u, 56u, 1u},
    {608u, 64u, 2u},
    {752u, 80u, 0u},
    {848u, 56u, 0u},
    {944u, 64u, 0u},
    {1040u, 64u, 0u},
    {1064u, 64u, 2u},
    {1256u, 32u, 0u},
    {1352u, 16u, 0u},
    {1448u, 16u, 0u},
    {1544u, 32u, 0u},
    {1416u, 16u, 0u},
    {1440u, 16u, 2u},
};

static const EnemyDef enemies_4[] = {
    {468u, 80u, 24u, 0u},
    {776u, 112u, 24u, 0u},
    {1132u, 80u, 24u, 0u},
    {1432u, 88u, 24u, 0u},
    {864u, 48u, 16u, 1u},
};

/* Stage 11, room 3: Starwake Lagoon. */
static const PlatformDef platforms_5[] = {
    {0u, 128u, 192u, 0u},
    {224u, 128u, 144u, 0u},
    {408u, 112u, 112u, 1u},
    {552u, 96u, 128u, 1u},
    {720u, 96u, 104u, 0u},
    {856u, 112u, 160u, 0u},
    {1056u, 128u, 112u, 0u},
    {1200u, 104u, 120u, 0u},
    {1352u, 96u, 128u, 0u},
    {1504u, 128u, 144u, 0u},
    {1648u, 128u, 192u, 0u},
    {248u, 128u, 72u, 0u},
    {344u, 128u, 72u, 0u},
    {440u, 128u, 80u, 0u},
    {536u, 104u, 72u, 1u},
    {744u, 72u, 80u, 1u},
    {840u, 48u, 80u, 1u},
    {936u, 56u, 88u, 1u},
    {1032u, 72u, 88u, 1u},
    {1224u, 80u, 64u, 1u},
    {1320u, 56u, 80u, 1u},
    {1272u, 48u, 64u, 1u},
};

static const PickupDef pickups_5[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {248u, 104u, 0u},
    {288u, 104u, 0u},
    {432u, 88u, 0u},
    {472u, 88u, 0u},
    {576u, 72u, 0u},
    {616u, 72u, 0u},
    {744u, 72u, 0u},
    {784u, 72u, 0u},
    {880u, 88u, 0u},
    {920u, 88u, 0u},
    {1080u, 104u, 0u},
    {1120u, 104u, 0u},
    {1224u, 80u, 0u},
    {1264u, 80u, 0u},
    {1376u, 72u, 0u},
    {1416u, 72u, 0u},
    {1528u, 104u, 0u},
    {1568u, 104u, 0u},
    {1672u, 104u, 0u},
    {1712u, 104u, 0u},
    {264u, 104u, 0u},
    {360u, 104u, 0u},
    {456u, 104u, 0u},
    {552u, 80u, 0u},
    {480u, 104u, 2u},
    {760u, 48u, 0u},
    {856u, 24u, 0u},
    {952u, 32u, 0u},
    {1048u, 48u, 0u},
    {832u, 32u, 1u},
    {928u, 40u, 1u},
    {1072u, 48u, 2u},
    {1240u, 56u, 0u},
    {1336u, 32u, 0u},
    {1288u, 24u, 0u},
    {1312u, 24u, 2u},
};

static const EnemyDef enemies_5[] = {
    {464u, 96u, 24u, 0u},
    {772u, 80u, 24u, 0u},
    {1112u, 112u, 24u, 0u},
    {1416u, 80u, 24u, 0u},
    {872u, 24u, 16u, 1u},
};

/* Stage 12, room 1: Heart of Moonwake. */
static const PlatformDef platforms_6[] = {
    {0u, 128u, 224u, 0u},
    {248u, 112u, 120u, 0u},
    {392u, 128u, 160u, 0u},
    {576u, 112u, 128u, 0u},
    {728u, 128u, 192u, 0u},
    {944u, 112u, 128u, 0u},
    {1096u, 96u, 128u, 0u},
    {1248u, 112u, 128u, 0u},
    {1400u, 128u, 176u, 0u},
    {1576u, 128u, 184u, 0u},
    {272u, 80u, 64u, 1u},
    {360u, 56u, 88u, 1u},
    {752u, 96u, 72u, 1u},
    {848u, 72u, 80u, 1u},
    {1120u, 64u, 64u, 1u},
    {1208u, 48u, 88u, 1u},
};

static const PickupDef pickups_6[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {272u, 88u, 0u},
    {312u, 88u, 0u},
    {416u, 104u, 0u},
    {456u, 104u, 0u},
    {600u, 88u, 0u},
    {640u, 88u, 0u},
    {752u, 104u, 0u},
    {792u, 104u, 0u},
    {968u, 88u, 0u},
    {1008u, 88u, 0u},
    {1120u, 72u, 0u},
    {1160u, 72u, 0u},
    {1272u, 88u, 0u},
    {1312u, 88u, 0u},
    {1424u, 104u, 0u},
    {1464u, 104u, 0u},
    {288u, 56u, 0u},
    {376u, 32u, 0u},
    {408u, 32u, 2u},
    {768u, 72u, 0u},
    {864u, 48u, 0u},
    {888u, 48u, 2u},
    {1136u, 40u, 0u},
    {1224u, 24u, 0u},
    {1192u, 40u, 1u},
    {1256u, 24u, 2u},
};

static const EnemyDef enemies_6[] = {
    {320u, 96u, 8u, 0u},
    {472u, 112u, 24u, 0u},
    {656u, 96u, 16u, 0u},
    {824u, 112u, 24u, 0u},
    {1016u, 96u, 16u, 0u},
    {1304u, 96u, 16u, 0u},
};

/* Stage 12, room 2: Dreamcurrent Reef. */
static const PlatformDef platforms_7[] = {
    {0u, 128u, 224u, 0u},
    {256u, 112u, 104u, 0u},
    {400u, 96u, 128u, 0u},
    {560u, 80u, 112u, 0u},
    {704u, 104u, 128u, 1u},
    {864u, 128u, 144u, 0u},
    {1048u, 112u, 104u, 1u},
    {1184u, 96u, 128u, 0u},
    {1344u, 112u, 128u, 0u},
    {1496u, 128u, 144u, 0u},
    {1640u, 128u, 192u, 0u},
    {280u, 88u, 72u, 1u},
    {376u, 64u, 80u, 1u},
    {472u, 64u, 88u, 1u},
    {568u, 72u, 80u, 1u},
    {440u, 56u, 64u, 1u},
    {728u, 128u, 72u, 0u},
    {824u, 128u, 72u, 0u},
    {920u, 128u, 80u, 0u},
    {1016u, 104u, 72u, 1u},
    {1208u, 72u, 80u, 1u},
    {1304u, 48u, 80u, 1u},
    {1400u, 56u, 88u, 1u},
    {1496u, 72u, 88u, 1u},
};

static const PickupDef pickups_7[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {280u, 88u, 0u},
    {320u, 88u, 0u},
    {424u, 72u, 0u},
    {464u, 72u, 0u},
    {584u, 56u, 0u},
    {624u, 56u, 0u},
    {728u, 80u, 0u},
    {768u, 80u, 0u},
    {888u, 104u, 0u},
    {928u, 104u, 0u},
    {1072u, 88u, 0u},
    {1112u, 88u, 0u},
    {1208u, 72u, 0u},
    {1248u, 72u, 0u},
    {1368u, 88u, 0u},
    {1408u, 88u, 0u},
    {1520u, 104u, 0u},
    {1560u, 104u, 0u},
    {1664u, 104u, 0u},
    {1704u, 104u, 0u},
    {296u, 64u, 0u},
    {392u, 40u, 0u},
    {488u, 40u, 0u},
    {584u, 48u, 0u},
    {456u, 32u, 0u},
    {480u, 32u, 2u},
    {744u, 104u, 0u},
    {840u, 104u, 0u},
    {936u, 104u, 0u},
    {1032u, 80u, 0u},
    {960u, 104u, 2u},
    {1224u, 48u, 0u},
    {1320u, 24u, 0u},
    {1416u, 32u, 0u},
    {1512u, 48u, 0u},
    {1296u, 32u, 1u},
    {1392u, 40u, 1u},
    {1536u, 48u, 2u},
};

static const EnemyDef enemies_7[] = {
    {464u, 80u, 24u, 0u},
    {768u, 88u, 24u, 0u},
    {1100u, 96u, 24u, 0u},
    {1408u, 96u, 24u, 0u},
    {856u, 96u, 16u, 1u},
};

/* Stage 12, room 3: Comet Manta Roost. */
static const PlatformDef platforms_8[] = {
    {0u, 128u, 192u, 0u},
    {224u, 112u, 128u, 0u},
    {392u, 96u, 112u, 0u},
    {536u, 112u, 128u, 0u},
    {704u, 128u, 104u, 0u},
    {840u, 112u, 144u, 0u},
    {1016u, 96u, 112u, 0u},
    {1160u, 128u, 128u, 0u},
    {1288u, 128u, 144u, 0u},
    {1432u, 128u, 224u, 0u},
    {248u, 88u, 80u, 1u},
    {344u, 64u, 80u, 1u},
    {440u, 72u, 88u, 1u},
    {536u, 88u, 88u, 1u},
    {728u, 104u, 80u, 1u},
    {824u, 80u, 80u, 1u},
    {920u, 88u, 88u, 1u},
    {1016u, 88u, 88u, 1u},
    {1040u, 72u, 64u, 1u},
    {1136u, 48u, 80u, 1u},
    {1088u, 40u, 64u, 1u},
};

static const PickupDef pickups_8[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {248u, 88u, 0u},
    {288u, 88u, 0u},
    {416u, 72u, 0u},
    {456u, 72u, 0u},
    {560u, 88u, 0u},
    {600u, 88u, 0u},
    {728u, 104u, 0u},
    {768u, 104u, 0u},
    {864u, 88u, 0u},
    {904u, 88u, 0u},
    {1040u, 72u, 0u},
    {1080u, 72u, 0u},
    {1184u, 104u, 0u},
    {1224u, 104u, 0u},
    {1312u, 104u, 0u},
    {1352u, 104u, 0u},
    {264u, 64u, 0u},
    {360u, 40u, 0u},
    {456u, 48u, 0u},
    {552u, 64u, 0u},
    {576u, 64u, 2u},
    {744u, 80u, 0u},
    {840u, 56u, 0u},
    {936u, 64u, 0u},
    {1032u, 64u, 0u},
    {816u, 64u, 1u},
    {912u, 72u, 1u},
    {1056u, 64u, 2u},
    {1056u, 48u, 0u},
    {1152u, 24u, 0u},
    {1104u, 16u, 0u},
    {1128u, 16u, 2u},
};

static const EnemyDef enemies_8[] = {
    {448u, 80u, 24u, 0u},
    {756u, 112u, 24u, 0u},
    {1072u, 80u, 24u, 0u},
    {856u, 48u, 16u, 1u},
};

static const LevelDef definitions[9] = {
    {"Whale in the Sky", 1600u, 24u, 1552u, 896u, 3u, 112u, 128u, 128u, 0u, 14u, 25u, 5u, 0u},
    {"Pearlspine Garden", 1800u, 24u, 1752u, 920u, 3u, 112u, 128u, 128u, 0u, 23u, 37u, 5u, 0u},
    {"Moonfoam Hollows", 1784u, 24u, 1736u, 896u, 3u, 112u, 128u, 128u, 0u, 24u, 40u, 5u, 0u},
    {"Stardrift Current", 1760u, 24u, 1712u, 848u, 3u, 112u, 128u, 128u, 0u, 18u, 38u, 8u, 0u},
    {"Manta Slipstream", 1848u, 24u, 1800u, 960u, 3u, 112u, 128u, 112u, 0u, 24u, 40u, 5u, 0u},
    {"Starwake Lagoon", 1840u, 24u, 1792u, 936u, 3u, 112u, 128u, 112u, 0u, 22u, 38u, 5u, 0u},
    {"Heart of Moonwake", 1760u, 24u, 1712u, 824u, 3u, 112u, 128u, 128u, 0u, 16u, 28u, 6u, 0u},
    {"Dreamcurrent Reef", 1832u, 24u, 1784u, 936u, 3u, 112u, 128u, 128u, 0u, 24u, 40u, 5u, 0u},
    {"Comet Manta Roost", 1656u, 24u, 1608u, 1360u, 3u, 112u, 128u, 128u, 2u, 21u, 34u, 4u, 0u},
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
    {"A WHALE HOLDS SKY.", "ITS DREAM GROWS DIM.", "BRING BACK THE DAWN."},
    {"PEARLSPINE GARDEN", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
    {"MOONFOAM HOLLOWS", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
    {"STARS ARE A CURRENT.", "LANTERNS ARE ANCHORS", "CHASE THE WAKING SKY"},
    {"MANTA SLIPSTREAM", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
    {"STARWAKE LAGOON", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
    {"THE DREAM HAS A KNOT", "LOOSEN IT WITH LIGHT", "WAKE THE SKY SEA."},
    {"DREAMCURRENT REEF", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
    {"COMET MANTA ROOST", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
};

static const uint16_t pars[3] = {
    95u, 105u, 110u
};

static uint8_t room_index(uint8_t local_stage, uint8_t room) {
    if (local_stage >= 3u) local_stage = 0u;
    if (room >= ROOMS_PER_STAGE) room = 0u;
    return local_stage * ROOMS_PER_STAGE + room;
}

void campaign_3_load(uint8_t local_stage, uint8_t room, LevelDef *out,
                       PlatformDef *plats, PickupDef *picks, EnemyDef *enemies) BANKED {
    uint8_t index = room_index(local_stage, room);
    memcpy(out, &definitions[index], sizeof(LevelDef));
    memcpy(plats, platforms_sets[index], (uint16_t)out->platform_count * sizeof(PlatformDef));
    memcpy(picks, pickups_sets[index], (uint16_t)out->pickup_count * sizeof(PickupDef));
    memcpy(enemies, enemies_sets[index], (uint16_t)out->enemy_count * sizeof(EnemyDef));
}

void campaign_3_info(uint8_t local_stage, LevelDef *out) BANKED {
    memcpy(out, &definitions[room_index(local_stage, 0u)], sizeof(LevelDef));
}

void campaign_3_intro(uint8_t local_stage, uint8_t room, char *line1,
                        char *line2, char *line3) BANKED {
    uint8_t index = room_index(local_stage, room);
    strcpy(line1, intros[index][0]);
    strcpy(line2, intros[index][1]);
    strcpy(line3, intros[index][2]);
}

uint16_t campaign_3_par(uint8_t local_stage) BANKED {
    if (local_stage >= 3u) local_stage = 0u;
    return pars[local_stage];
}
