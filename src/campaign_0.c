/* Generated from docs/routes.json by tools/build_campaign.py. */
/* Saffron Harbor: three stages, nine continuous rooms. */
#pragma bank 16
#include "levels.h"
#include <string.h>

/* Stage 1, room 1: Lantern Quay. */
static const PlatformDef platforms_0[] = {
    {0u, 128u, 224u, 0u},
    {224u, 128u, 176u, 0u},
    {424u, 128u, 176u, 0u},
    {624u, 112u, 128u, 0u},
    {776u, 128u, 176u, 0u},
    {976u, 128u, 160u, 0u},
    {1160u, 112u, 152u, 0u},
    {1336u, 128u, 200u, 0u},
    {176u, 96u, 64u, 1u},
    {264u, 72u, 80u, 1u},
    {632u, 80u, 72u, 1u},
    {728u, 56u, 80u, 1u},
    {1064u, 96u, 64u, 1u},
    {1152u, 72u, 96u, 1u},
};

static const PickupDef pickups_0[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {248u, 104u, 0u},
    {288u, 104u, 0u},
    {448u, 104u, 0u},
    {488u, 104u, 0u},
    {648u, 88u, 0u},
    {688u, 88u, 0u},
    {800u, 104u, 0u},
    {840u, 104u, 0u},
    {1000u, 104u, 0u},
    {1040u, 104u, 0u},
    {1184u, 88u, 0u},
    {1224u, 88u, 0u},
    {1360u, 104u, 0u},
    {1400u, 104u, 0u},
    {192u, 72u, 0u},
    {280u, 48u, 0u},
    {304u, 48u, 2u},
    {648u, 56u, 0u},
    {744u, 32u, 0u},
    {768u, 32u, 2u},
    {1080u, 72u, 0u},
    {1168u, 48u, 0u},
    {1200u, 48u, 2u},
};

static const EnemyDef enemies_0[] = {
    {496u, 112u, 24u, 0u},
    {896u, 112u, 24u, 0u},
    {1256u, 96u, 24u, 0u},
};

/* Stage 1, room 2: Paperboat Reach. */
static const PlatformDef platforms_1[] = {
    {0u, 128u, 224u, 0u},
    {248u, 128u, 128u, 0u},
    {408u, 112u, 96u, 0u},
    {528u, 96u, 144u, 0u},
    {696u, 112u, 112u, 0u},
    {840u, 128u, 160u, 0u},
    {1024u, 112u, 112u, 0u},
    {1176u, 96u, 128u, 0u},
    {1328u, 112u, 112u, 0u},
    {1464u, 128u, 144u, 0u},
    {1608u, 128u, 192u, 0u},
    {272u, 104u, 80u, 1u},
    {368u, 80u, 80u, 1u},
    {464u, 88u, 88u, 1u},
    {560u, 88u, 88u, 1u},
    {720u, 88u, 72u, 1u},
    {816u, 64u, 80u, 1u},
    {912u, 64u, 88u, 1u},
    {1008u, 88u, 80u, 1u},
    {880u, 56u, 64u, 1u},
    {1200u, 72u, 80u, 1u},
    {1296u, 48u, 80u, 1u},
    {1392u, 56u, 88u, 1u},
    {1488u, 72u, 88u, 1u},
};

static const PickupDef pickups_1[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {272u, 104u, 0u},
    {312u, 104u, 0u},
    {432u, 88u, 0u},
    {472u, 88u, 0u},
    {552u, 72u, 0u},
    {592u, 72u, 0u},
    {720u, 88u, 0u},
    {760u, 88u, 0u},
    {864u, 104u, 0u},
    {904u, 104u, 0u},
    {1048u, 88u, 0u},
    {1088u, 88u, 0u},
    {1200u, 72u, 0u},
    {1240u, 72u, 0u},
    {1352u, 88u, 0u},
    {1392u, 88u, 0u},
    {1488u, 104u, 0u},
    {1528u, 104u, 0u},
    {1632u, 104u, 0u},
    {1672u, 104u, 0u},
    {288u, 80u, 0u},
    {384u, 56u, 0u},
    {480u, 64u, 0u},
    {576u, 64u, 0u},
    {600u, 64u, 2u},
    {736u, 64u, 0u},
    {832u, 40u, 0u},
    {928u, 40u, 0u},
    {1024u, 64u, 0u},
    {896u, 32u, 0u},
    {920u, 32u, 2u},
    {1216u, 48u, 0u},
    {1312u, 24u, 0u},
    {1408u, 32u, 0u},
    {1504u, 48u, 0u},
    {1288u, 32u, 1u},
    {1384u, 40u, 1u},
    {1528u, 48u, 2u},
};

static const EnemyDef enemies_1[] = {
    {456u, 96u, 24u, 0u},
    {752u, 96u, 24u, 0u},
    {1080u, 96u, 24u, 0u},
    {1384u, 96u, 24u, 0u},
};

/* Stage 1, room 3: Firefly Tide. */
static const PlatformDef platforms_2[] = {
    {0u, 128u, 192u, 0u},
    {216u, 112u, 144u, 0u},
    {384u, 96u, 128u, 0u},
    {544u, 96u, 96u, 0u},
    {672u, 112u, 144u, 0u},
    {840u, 128u, 160u, 0u},
    {1032u, 112u, 104u, 0u},
    {1176u, 112u, 120u, 0u},
    {1328u, 96u, 136u, 0u},
    {1488u, 128u, 144u, 0u},
    {1632u, 128u, 192u, 0u},
    {240u, 88u, 80u, 1u},
    {336u, 64u, 80u, 1u},
    {432u, 72u, 88u, 1u},
    {528u, 88u, 88u, 1u},
    {696u, 88u, 80u, 1u},
    {792u, 64u, 80u, 1u},
    {888u, 72u, 88u, 1u},
    {984u, 88u, 88u, 1u},
    {1200u, 88u, 64u, 1u},
    {1296u, 64u, 80u, 1u},
    {1248u, 56u, 64u, 1u},
};

static const PickupDef pickups_2[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {240u, 88u, 0u},
    {280u, 88u, 0u},
    {408u, 72u, 0u},
    {448u, 72u, 0u},
    {568u, 72u, 0u},
    {608u, 72u, 0u},
    {696u, 88u, 0u},
    {736u, 88u, 0u},
    {864u, 104u, 0u},
    {904u, 104u, 0u},
    {1056u, 88u, 0u},
    {1096u, 88u, 0u},
    {1200u, 88u, 0u},
    {1240u, 88u, 0u},
    {1352u, 72u, 0u},
    {1392u, 72u, 0u},
    {1512u, 104u, 0u},
    {1552u, 104u, 0u},
    {1656u, 104u, 0u},
    {1696u, 104u, 0u},
    {256u, 64u, 0u},
    {352u, 40u, 0u},
    {448u, 48u, 0u},
    {544u, 64u, 0u},
    {328u, 48u, 1u},
    {424u, 56u, 1u},
    {568u, 64u, 2u},
    {712u, 64u, 0u},
    {808u, 40u, 0u},
    {904u, 48u, 0u},
    {1000u, 64u, 0u},
    {1024u, 64u, 2u},
    {1216u, 64u, 0u},
    {1312u, 40u, 0u},
    {1264u, 32u, 0u},
    {1288u, 32u, 2u},
};

static const EnemyDef enemies_2[] = {
    {448u, 80u, 24u, 0u},
    {744u, 96u, 24u, 0u},
    {1084u, 96u, 24u, 0u},
    {1396u, 80u, 24u, 0u},
};

/* Stage 2, room 1: Apricot Rooftops. */
static const PlatformDef platforms_3[] = {
    {0u, 128u, 192u, 0u},
    {208u, 112u, 144u, 0u},
    {376u, 96u, 144u, 0u},
    {544u, 112u, 152u, 0u},
    {720u, 128u, 184u, 0u},
    {928u, 112u, 144u, 0u},
    {1096u, 96u, 144u, 0u},
    {1264u, 112u, 128u, 0u},
    {1416u, 128u, 184u, 0u},
    {240u, 80u, 64u, 1u},
    {328u, 56u, 88u, 1u},
    {736u, 96u, 64u, 1u},
    {824u, 72u, 88u, 1u},
    {1120u, 64u, 64u, 1u},
    {1216u, 48u, 88u, 1u},
};

static const PickupDef pickups_3[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {232u, 88u, 0u},
    {272u, 88u, 0u},
    {400u, 72u, 0u},
    {440u, 72u, 0u},
    {568u, 88u, 0u},
    {608u, 88u, 0u},
    {744u, 104u, 0u},
    {784u, 104u, 0u},
    {952u, 88u, 0u},
    {992u, 88u, 0u},
    {1120u, 72u, 0u},
    {1160u, 72u, 0u},
    {1288u, 88u, 0u},
    {1328u, 88u, 0u},
    {1440u, 104u, 0u},
    {1480u, 104u, 0u},
    {256u, 56u, 0u},
    {344u, 32u, 0u},
    {368u, 32u, 2u},
    {752u, 72u, 0u},
    {840u, 48u, 0u},
    {864u, 48u, 2u},
    {1136u, 40u, 0u},
    {1232u, 24u, 0u},
    {1184u, 48u, 1u},
    {1264u, 24u, 2u},
};

static const EnemyDef enemies_3[] = {
    {296u, 96u, 24u, 0u},
    {616u, 96u, 24u, 0u},
    {1000u, 96u, 24u, 0u},
    {1320u, 96u, 16u, 0u},
};

/* Stage 2, room 2: Tea House Attic. */
static const PlatformDef platforms_4[] = {
    {0u, 128u, 192u, 0u},
    {208u, 112u, 128u, 0u},
    {360u, 96u, 112u, 0u},
    {496u, 80u, 144u, 0u},
    {664u, 96u, 96u, 1u},
    {792u, 128u, 176u, 0u},
    {992u, 112u, 120u, 1u},
    {1136u, 96u, 96u, 0u},
    {1264u, 112u, 128u, 0u},
    {1416u, 128u, 144u, 0u},
    {1560u, 128u, 192u, 0u},
    {232u, 88u, 72u, 1u},
    {328u, 64u, 80u, 1u},
    {424u, 64u, 88u, 1u},
    {520u, 72u, 80u, 1u},
    {392u, 56u, 64u, 1u},
    {688u, 128u, 72u, 0u},
    {784u, 128u, 72u, 0u},
    {880u, 128u, 80u, 0u},
    {976u, 104u, 72u, 1u},
    {1160u, 72u, 80u, 1u},
    {1248u, 48u, 80u, 1u},
    {1336u, 56u, 88u, 1u},
    {1424u, 72u, 88u, 1u},
};

static const PickupDef pickups_4[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {232u, 88u, 0u},
    {272u, 88u, 0u},
    {384u, 72u, 0u},
    {424u, 72u, 0u},
    {520u, 56u, 0u},
    {560u, 56u, 0u},
    {688u, 72u, 0u},
    {728u, 72u, 0u},
    {816u, 104u, 0u},
    {856u, 104u, 0u},
    {1016u, 88u, 0u},
    {1056u, 88u, 0u},
    {1160u, 72u, 0u},
    {1200u, 72u, 0u},
    {1288u, 88u, 0u},
    {1328u, 88u, 0u},
    {1440u, 104u, 0u},
    {1480u, 104u, 0u},
    {1584u, 104u, 0u},
    {1624u, 104u, 0u},
    {248u, 64u, 0u},
    {344u, 40u, 0u},
    {440u, 40u, 0u},
    {536u, 48u, 0u},
    {408u, 32u, 0u},
    {432u, 32u, 2u},
    {704u, 104u, 0u},
    {800u, 104u, 0u},
    {896u, 104u, 0u},
    {992u, 80u, 0u},
    {920u, 104u, 2u},
    {1176u, 48u, 0u},
    {1264u, 24u, 0u},
    {1352u, 32u, 0u},
    {1440u, 48u, 0u},
    {1464u, 48u, 2u},
};

static const EnemyDef enemies_4[] = {
    {416u, 80u, 24u, 0u},
    {712u, 80u, 24u, 0u},
    {1052u, 96u, 24u, 0u},
    {1328u, 96u, 24u, 0u},
};

/* Stage 2, room 3: Cloudpost Row. */
static const PlatformDef platforms_5[] = {
    {0u, 128u, 224u, 0u},
    {256u, 112u, 112u, 0u},
    {392u, 128u, 144u, 0u},
    {576u, 112u, 96u, 0u},
    {696u, 96u, 128u, 0u},
    {848u, 112u, 160u, 0u},
    {1040u, 128u, 104u, 0u},
    {1184u, 112u, 112u, 0u},
    {1320u, 96u, 144u, 0u},
    {1488u, 128u, 128u, 0u},
    {1616u, 128u, 192u, 0u},
    {280u, 88u, 80u, 1u},
    {376u, 64u, 80u, 1u},
    {472u, 72u, 88u, 1u},
    {568u, 88u, 88u, 1u},
    {720u, 72u, 80u, 1u},
    {816u, 48u, 80u, 1u},
    {912u, 56u, 88u, 1u},
    {1008u, 72u, 88u, 1u},
    {1208u, 88u, 72u, 1u},
    {1304u, 64u, 80u, 1u},
    {1400u, 64u, 88u, 1u},
    {1496u, 88u, 80u, 1u},
    {1368u, 56u, 64u, 1u},
};

static const PickupDef pickups_5[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {280u, 88u, 0u},
    {320u, 88u, 0u},
    {416u, 104u, 0u},
    {456u, 104u, 0u},
    {600u, 88u, 0u},
    {640u, 88u, 0u},
    {720u, 72u, 0u},
    {760u, 72u, 0u},
    {872u, 88u, 0u},
    {912u, 88u, 0u},
    {1064u, 104u, 0u},
    {1104u, 104u, 0u},
    {1208u, 88u, 0u},
    {1248u, 88u, 0u},
    {1344u, 72u, 0u},
    {1384u, 72u, 0u},
    {1512u, 104u, 0u},
    {1552u, 104u, 0u},
    {1640u, 104u, 0u},
    {1680u, 104u, 0u},
    {296u, 64u, 0u},
    {392u, 40u, 0u},
    {488u, 48u, 0u},
    {584u, 64u, 0u},
    {608u, 64u, 2u},
    {736u, 48u, 0u},
    {832u, 24u, 0u},
    {928u, 32u, 0u},
    {1024u, 48u, 0u},
    {808u, 32u, 1u},
    {904u, 40u, 1u},
    {1048u, 48u, 2u},
    {1224u, 64u, 0u},
    {1320u, 40u, 0u},
    {1416u, 40u, 0u},
    {1512u, 64u, 0u},
    {1384u, 32u, 0u},
    {1408u, 32u, 2u},
};

static const EnemyDef enemies_5[] = {
    {464u, 112u, 24u, 0u},
    {760u, 80u, 24u, 0u},
    {1092u, 112u, 24u, 0u},
    {1392u, 80u, 24u, 0u},
};

/* Stage 3, room 1: Kitewake Causeway. */
static const PlatformDef platforms_6[] = {
    {0u, 128u, 224u, 0u},
    {248u, 128u, 160u, 0u},
    {456u, 112u, 128u, 0u},
    {624u, 128u, 176u, 0u},
    {832u, 128u, 160u, 0u},
    {1032u, 112u, 128u, 0u},
    {1208u, 128u, 176u, 0u},
    {1416u, 128u, 248u, 0u},
    {264u, 96u, 64u, 1u},
    {352u, 72u, 88u, 1u},
    {648u, 96u, 72u, 1u},
    {752u, 72u, 72u, 1u},
    {856u, 56u, 72u, 1u},
    {1216u, 96u, 64u, 1u},
    {1312u, 72u, 88u, 1u},
};

static const PickupDef pickups_6[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {272u, 104u, 0u},
    {312u, 104u, 0u},
    {480u, 88u, 0u},
    {520u, 88u, 0u},
    {648u, 104u, 0u},
    {688u, 104u, 0u},
    {856u, 104u, 0u},
    {896u, 104u, 0u},
    {1056u, 88u, 0u},
    {1096u, 88u, 0u},
    {1232u, 104u, 0u},
    {1272u, 104u, 0u},
    {1440u, 104u, 0u},
    {1480u, 104u, 0u},
    {280u, 72u, 0u},
    {368u, 48u, 0u},
    {400u, 48u, 2u},
    {664u, 72u, 0u},
    {768u, 48u, 0u},
    {872u, 32u, 0u},
    {728u, 64u, 1u},
    {832u, 48u, 1u},
    {896u, 32u, 2u},
    {1232u, 72u, 0u},
    {1328u, 48u, 0u},
    {1296u, 64u, 1u},
    {1360u, 48u, 2u},
    {440u, 88u, 1u},
    {1192u, 88u, 1u},
};

static const EnemyDef enemies_6[] = {
    {336u, 112u, 24u, 0u},
    {712u, 112u, 24u, 0u},
    {1104u, 96u, 24u, 0u},
    {1512u, 112u, 32u, 0u},
    {816u, 64u, 24u, 1u},
};

/* Stage 3, room 2: Windchime Pier. */
static const PlatformDef platforms_7[] = {
    {0u, 128u, 192u, 0u},
    {216u, 128u, 160u, 0u},
    {416u, 112u, 104u, 0u},
    {544u, 96u, 128u, 0u},
    {704u, 96u, 112u, 0u},
    {848u, 128u, 160u, 0u},
    {1048u, 112u, 96u, 0u},
    {1176u, 112u, 128u, 0u},
    {1344u, 96u, 112u, 0u},
    {1480u, 128u, 144u, 0u},
    {1624u, 128u, 192u, 0u},
    {240u, 104u, 80u, 1u},
    {336u, 80u, 80u, 1u},
    {432u, 88u, 88u, 1u},
    {528u, 88u, 88u, 1u},
    {728u, 72u, 72u, 1u},
    {824u, 48u, 80u, 1u},
    {920u, 48u, 88u, 1u},
    {1016u, 72u, 80u, 1u},
    {888u, 40u, 64u, 1u},
    {1200u, 88u, 80u, 1u},
    {1296u, 64u, 80u, 1u},
    {1392u, 72u, 88u, 1u},
    {1488u, 88u, 88u, 1u},
};

static const PickupDef pickups_7[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {240u, 104u, 0u},
    {280u, 104u, 0u},
    {440u, 88u, 0u},
    {480u, 88u, 0u},
    {568u, 72u, 0u},
    {608u, 72u, 0u},
    {728u, 72u, 0u},
    {768u, 72u, 0u},
    {872u, 104u, 0u},
    {912u, 104u, 0u},
    {1072u, 88u, 0u},
    {1112u, 88u, 0u},
    {1200u, 88u, 0u},
    {1240u, 88u, 0u},
    {1368u, 72u, 0u},
    {1408u, 72u, 0u},
    {1504u, 104u, 0u},
    {1544u, 104u, 0u},
    {1648u, 104u, 0u},
    {1688u, 104u, 0u},
    {256u, 80u, 0u},
    {352u, 56u, 0u},
    {448u, 64u, 0u},
    {544u, 64u, 0u},
    {328u, 64u, 1u},
    {424u, 72u, 1u},
    {568u, 64u, 2u},
    {744u, 48u, 0u},
    {840u, 24u, 0u},
    {936u, 24u, 0u},
    {1032u, 48u, 0u},
    {904u, 16u, 0u},
    {928u, 16u, 2u},
    {1216u, 64u, 0u},
    {1312u, 40u, 0u},
    {1408u, 48u, 0u},
    {1504u, 64u, 0u},
    {1528u, 64u, 2u},
};

static const EnemyDef enemies_7[] = {
    {468u, 96u, 24u, 0u},
    {760u, 80u, 24u, 0u},
    {1096u, 96u, 24u, 0u},
    {1400u, 80u, 24u, 0u},
};

/* Stage 3, room 3: Wishkite Crossing. */
static const PlatformDef platforms_8[] = {
    {0u, 128u, 224u, 0u},
    {256u, 112u, 112u, 0u},
    {408u, 128u, 128u, 0u},
    {576u, 112u, 112u, 0u},
    {712u, 96u, 144u, 0u},
    {888u, 112u, 128u, 0u},
    {1056u, 128u, 104u, 0u},
    {1208u, 112u, 112u, 0u},
    {1352u, 96u, 112u, 0u},
    {1496u, 128u, 144u, 0u},
    {1640u, 128u, 192u, 0u},
    {280u, 88u, 80u, 1u},
    {376u, 64u, 80u, 1u},
    {472u, 72u, 88u, 1u},
    {568u, 88u, 88u, 1u},
    {736u, 72u, 80u, 1u},
    {832u, 48u, 80u, 1u},
    {928u, 56u, 88u, 1u},
    {1024u, 72u, 88u, 1u},
    {1232u, 88u, 64u, 1u},
    {1328u, 64u, 80u, 1u},
    {1280u, 56u, 64u, 1u},
};

static const PickupDef pickups_8[] = {
    {72u, 104u, 0u},
    {120u, 104u, 0u},
    {280u, 88u, 0u},
    {320u, 88u, 0u},
    {432u, 104u, 0u},
    {472u, 104u, 0u},
    {600u, 88u, 0u},
    {640u, 88u, 0u},
    {736u, 72u, 0u},
    {776u, 72u, 0u},
    {912u, 88u, 0u},
    {952u, 88u, 0u},
    {1080u, 104u, 0u},
    {1120u, 104u, 0u},
    {1232u, 88u, 0u},
    {1272u, 88u, 0u},
    {1376u, 72u, 0u},
    {1416u, 72u, 0u},
    {1520u, 104u, 0u},
    {1560u, 104u, 0u},
    {1664u, 104u, 0u},
    {1704u, 104u, 0u},
    {296u, 64u, 0u},
    {392u, 40u, 0u},
    {488u, 48u, 0u},
    {584u, 64u, 0u},
    {608u, 64u, 2u},
    {752u, 48u, 0u},
    {848u, 24u, 0u},
    {944u, 32u, 0u},
    {1040u, 48u, 0u},
    {824u, 32u, 1u},
    {920u, 40u, 1u},
    {1064u, 48u, 2u},
    {1248u, 64u, 0u},
    {1344u, 40u, 0u},
    {1296u, 32u, 0u},
    {1320u, 32u, 2u},
};

static const EnemyDef enemies_8[] = {
    {472u, 112u, 24u, 0u},
    {784u, 80u, 24u, 0u},
    {1108u, 112u, 24u, 0u},
    {1408u, 80u, 24u, 0u},
};

static const LevelDef definitions[9] = {
    {"Lantern Quay", 1536u, 24u, 1488u, 840u, 0u, 112u, 128u, 128u, 0u, 14u, 25u, 3u, 0u},
    {"Paperboat Reach", 1800u, 24u, 1752u, 920u, 0u, 112u, 128u, 128u, 0u, 24u, 40u, 4u, 0u},
    {"Firefly Tide", 1824u, 24u, 1776u, 920u, 0u, 112u, 128u, 128u, 0u, 22u, 38u, 4u, 0u},
    {"Apricot Rooftops", 1600u, 24u, 1552u, 808u, 0u, 112u, 128u, 128u, 0u, 15u, 28u, 4u, 0u},
    {"Tea House Attic", 1752u, 24u, 1704u, 880u, 0u, 112u, 128u, 128u, 0u, 24u, 38u, 4u, 0u},
    {"Cloudpost Row", 1808u, 24u, 1760u, 928u, 0u, 112u, 128u, 112u, 0u, 24u, 40u, 4u, 0u},
    {"Kitewake Causeway", 1664u, 24u, 1616u, 896u, 0u, 112u, 128u, 128u, 0u, 15u, 31u, 5u, 0u},
    {"Windchime Pier", 1816u, 24u, 1768u, 928u, 0u, 112u, 128u, 128u, 0u, 24u, 40u, 4u, 0u},
    {"Wishkite Crossing", 1832u, 24u, 1784u, 952u, 0u, 112u, 128u, 112u, 0u, 22u, 38u, 4u, 0u},
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
    {"THE SKY SEA SLEEPS.", "KIP, LIGHT THE WAY.", "A HOP. B SCARF DASH."},
    {"PAPERBOAT REACH", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
    {"FIREFLY TIDE", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
    {"ROOFS HOLD THE HEAT.", "STARS SHOW THE WAY.", "LET YOUR SCARF FLY."},
    {"TEA HOUSE ATTIC", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
    {"CLOUDPOST ROW", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
    {"KITES CARRY WISHES.", "TOUCH A LANTERN.", "DASH AGAIN IN AIR."},
    {"WINDCHIME PIER", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
    {"WISHKITE CROSSING", "FOLLOW SMALL STARS.", "EXPLORE YOUR WAY."},
};

static const uint16_t pars[3] = {
    95u, 100u, 100u
};

static uint8_t room_index(uint8_t local_stage, uint8_t room) {
    if (local_stage >= 3u) local_stage = 0u;
    if (room >= ROOMS_PER_STAGE) room = 0u;
    return local_stage * ROOMS_PER_STAGE + room;
}

void campaign_0_load(uint8_t local_stage, uint8_t room, LevelDef *out,
                       PlatformDef *plats, PickupDef *picks, EnemyDef *enemies) BANKED {
    uint8_t index = room_index(local_stage, room);
    memcpy(out, &definitions[index], sizeof(LevelDef));
    memcpy(plats, platforms_sets[index], (uint16_t)out->platform_count * sizeof(PlatformDef));
    memcpy(picks, pickups_sets[index], (uint16_t)out->pickup_count * sizeof(PickupDef));
    memcpy(enemies, enemies_sets[index], (uint16_t)out->enemy_count * sizeof(EnemyDef));
}

void campaign_0_info(uint8_t local_stage, LevelDef *out) BANKED {
    memcpy(out, &definitions[room_index(local_stage, 0u)], sizeof(LevelDef));
}

void campaign_0_intro(uint8_t local_stage, uint8_t room, char *line1,
                        char *line2, char *line3) BANKED {
    uint8_t index = room_index(local_stage, room);
    strcpy(line1, intros[index][0]);
    strcpy(line2, intros[index][1]);
    strcpy(line3, intros[index][2]);
}

uint16_t campaign_0_par(uint8_t local_stage) BANKED {
    if (local_stage >= 3u) local_stage = 0u;
    return pars[local_stage];
}
