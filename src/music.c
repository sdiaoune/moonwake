/* MOONWAKE: original music by the Moonwake production team.
 * A sixteen-bar melody, changing harmony, answering pulse, triangle bass,
 * and carefully gated percussion run on the four physical CGB channels.
 * Sound effects borrow the answering pulse, so jumps never cut the melody.
 */
#pragma bank 7
#include <gb/gb.h>
#include <gb/hardware.h>
#include <stdint.h>
#include "music.h"

#define R 254u
#define T 255u
#define C3 0u
#define CS3 1u
#define D3 2u
#define DS3 3u
#define E3 4u
#define F3 5u
#define FS3 6u
#define G3 7u
#define GS3 8u
#define A3 9u
#define AS3 10u
#define B3 11u
#define BS3 12u
#define C4 12u
#define CS4 13u
#define D4 14u
#define DS4 15u
#define E4 16u
#define F4 17u
#define FS4 18u
#define G4 19u
#define GS4 20u
#define A4 21u
#define AS4 22u
#define B4 23u
#define C5 24u
#define CS5 25u
#define D5 26u
#define DS5 27u
#define E5 28u
#define F5 29u
#define FS5 30u
#define G5 31u
#define GS5 32u
#define A5 33u

/* Observable counters used by the PCM capture harness. */
uint8_t audio_track, audio_step, audio_enabled;
uint16_t audio_loops;
static uint8_t clock_tick, energy_on, lead_note, lead_volume, lead_decay;
static uint8_t effect_id, effect_left, effect_age, effect_priority;
static uint8_t counter_note, counter_volume, wave_volume;
static uint16_t wave_frequency;
static const uint16_t periods[48] = {
    1046,1102,1155,1205,1253,1297,1339,1379,1417,1452,1486,1517,
    1547,1575,1602,1627,1650,1673,1694,1714,1732,1750,1767,1783,
    1798,1812,1825,1837,1849,1860,1871,1881,1890,1899,1907,1915,
    1923,1930,1936,1943,1949,1954,1959,1964,1969,1974,1978,1982
};

/* Each line is one 4/4 bar of eighth notes. T ties; R breathes.
 * The E-B-C#-G# scarf motif returns in title, harbor and ending, with
 * different harmony and rhythm. The other worlds have their own themes. */
static const uint8_t melody[8][128] = {
    { /* 0: A Scarf for the Sleeping Sea — E major, invitation */
        E4,T,B4,CS5,T,GS4,R,FS4,
        A4,T,GS4,FS4,E4,T,R,B3,
        CS4,E4,GS4,T,B4,T,A4,GS4,
        FS4,T,DS4,FS4,B4,T,T,R,
        E4,T,B4,CS5,T,E5,DS5,B4,
        CS5,T,A4,GS4,FS4,T,E4,R,
        A4,T,CS5,E5,DS5,CS5,B4,A4,
        GS4,T,FS4,DS4,E4,T,T,R,
        B4,T,E5,FS5,T,E5,CS5,B4,
        A4,CS5,E5,T,CS5,B4,A4,R,
        GS4,T,B4,CS5,DS5,T,B4,GS4,
        FS4,A4,CS5,T,B4,GS4,FS4,R,
        E4,GS4,B4,T,CS5,T,GS4,FS4,
        A4,T,GS4,FS4,E4,FS4,GS4,A4,
        B4,T,DS5,FS5,E5,DS5,B4,FS4,
        GS4,T,FS4,DS4,E4,T,T,R
    },
    { /* 1: Persimmon Postcard — E major, propulsive offbeat pop */
        E4,R,B4,CS5,T,GS4,R,FS4,
        A4,R,GS4,FS4,E4,T,R,B3,
        CS4,E4,GS4,R,B4,GS4,E4,R,
        FS4,A4,B4,R,DS5,CS5,B4,R,
        E4,GS4,B4,CS5,R,E5,DS5,B4,
        CS5,R,A4,GS4,FS4,E4,CS4,R,
        A4,CS5,E5,R,DS5,CS5,B4,A4,
        GS4,R,FS4,DS4,E4,T,R,B3,
        B4,R,E5,FS5,T,E5,CS5,B4,
        A4,CS5,E5,R,CS5,B4,A4,R,
        GS4,B4,CS5,DS5,R,B4,GS4,R,
        FS4,A4,CS5,R,B4,GS4,FS4,R,
        E4,R,B4,CS5,T,GS4,FS4,E4,
        A4,R,CS5,B4,A4,GS4,FS4,R,
        B4,DS5,FS5,R,E5,DS5,B4,FS4,
        GS4,R,FS4,DS4,E4,T,R,B3
    },
    { /* 2: Rain on a Giant Lotus — D minor Dorian, skipping rain */
        A4,T,D5,R,C5,A4,F4,R,
        G4,A4,C5,T,A4,G4,E4,R,
        F4,R,A4,C5,D5,T,C5,A4,
        E4,G4,B4,T,A4,G4,E4,R,
        A4,T,D5,F5,E5,D5,C5,R,
        G4,R,C5,E5,D5,C5,A4,G4,
        F4,A4,C5,R,D5,C5,A4,F4,
        E4,GS4,B4,R,A4,T,T,R,
        F5,T,E5,D5,C5,R,A4,C5,
        E5,T,D5,C5,A4,R,G4,E4,
        D5,F5,E5,D5,C5,A4,F4,R,
        B4,D5,C5,B4,A4,G4,E4,R,
        A4,D5,F5,R,E5,D5,C5,A4,
        G4,C5,E5,R,D5,C5,A4,G4,
        F4,R,A4,C5,D5,C5,A4,F4,
        E4,GS4,B4,D5,CS5,A4,T,R
    },
    { /* 3: Brass Clock, Violet Sky — C# minor, ticking funk */
        CS4,R,GS4,E4,FS4,R,GS4,B4,
        A4,R,E4,FS4,GS4,B4,A4,R,
        FS4,R,A4,CS5,B4,A4,FS4,R,
        GS4,DS5,R,CS5,B4,GS4,FS4,R,
        CS5,R,GS4,CS5,E5,DS5,CS5,R,
        A4,CS5,R,E5,DS5,CS5,B4,A4,
        FS4,A4,CS5,R,DS5,E5,CS5,A4,
        GS4,R,B4,DS5,CS5,B4,GS4,R,
        E5,DS5,CS5,R,GS4,B4,CS5,R,
        FS5,E5,CS5,R,B4,A4,GS4,R,
        A4,CS5,E5,R,FS5,E5,CS5,A4,
        B4,DS5,FS5,R,E5,DS5,B4,R,
        CS4,R,GS4,E4,FS4,GS4,B4,CS5,
        A4,R,E5,DS5,CS5,B4,A4,GS4,
        FS4,A4,CS5,DS5,E5,R,DS5,CS5,
        BS3,R,GS4,DS5,CS5,T,R,GS3
    },
    { /* 4: The Whale That Carried Tomorrow — A major, floating hope */
        CS5,T,E5,T,B4,T,A4,GS4,
        FS4,T,A4,CS5,B4,T,A4,R,
        E4,GS4,B4,T,E5,T,DS5,B4,
        A4,T,GS4,FS4,E4,T,T,R,
        CS5,T,E5,FS5,E5,CS5,B4,T,
        D5,T,CS5,A4,FS4,T,A4,R,
        GS4,B4,E5,T,FS5,E5,DS5,B4,
        CS5,T,B4,GS4,A4,T,T,R,
        E5,T,FS5,E5,CS5,T,B4,A4,
        D5,T,FS5,E5,D5,CS5,A4,R,
        B4,T,E5,DS5,CS5,B4,GS4,T,
        A4,CS5,E5,T,DS5,B4,A4,R,
        CS5,E5,FS5,T,E5,CS5,B4,A4,
        FS4,A4,D5,T,CS5,A4,FS4,R,
        GS4,B4,E5,FS5,E5,DS5,B4,GS4,
        A4,T,GS4,E4,A4,T,T,R
    },
    { /* 5: Wake Up, Sleepstorm! — C# minor, urgent call-and-response */
        CS4,GS4,R,CS5,B4,GS4,E4,R,
        A4,E5,R,CS5,B4,A4,GS4,R,
        FS4,CS5,R,A4,B4,CS5,A4,R,
        GS4,DS5,R,B4,DS5,E5,DS5,R,
        CS5,GS4,CS5,E5,R,DS5,CS5,B4,
        A4,E5,FS5,E5,R,CS5,B4,A4,
        FS4,A4,CS5,E5,R,DS5,CS5,A4,
        GS4,B4,DS5,FS5,R,E5,DS5,B4,
        E5,R,DS5,CS5,GS4,CS5,R,B4,
        FS5,R,E5,CS5,A4,CS5,R,B4,
        E5,CS5,A4,R,FS4,A4,CS5,R,
        DS5,B4,GS4,R,DS5,E5,FS5,R,
        CS5,GS4,E5,DS5,CS5,R,GS4,B4,
        A4,CS5,FS5,E5,CS5,R,B4,A4,
        FS4,A4,CS5,E5,DS5,CS5,A4,FS4,
        GS4,B4,DS5,FS5,E5,DS5,CS5,R
    },
    { /* 6: A Little More Sky — E major, bright celebration */
        E4,GS4,B4,R,CS5,E5,T,R,
        FS5,E5,CS5,B4,A4,T,GS4,R,
        A4,CS5,E5,R,FS5,E5,CS5,R,
        DS5,B4,GS4,FS4,E4,T,T,R,
        E4,GS4,B4,CS5,E5,T,DS5,B4,
        CS5,A4,FS4,A4,CS5,T,B4,R,
        A4,CS5,E5,FS5,E5,DS5,B4,GS4,
        FS4,DS4,E4,T,T,T,R,R,
        E5,T,CS5,B4,GS4,R,B4,CS5,
        FS5,T,E5,CS5,A4,R,CS5,E5,
        A4,B4,CS5,E5,DS5,T,B4,R,
        A4,GS4,FS4,DS4,E4,T,T,R,
        E4,GS4,B4,R,CS5,E5,T,R,
        FS5,E5,CS5,B4,A4,T,GS4,R,
        A4,CS5,E5,DS5,CS5,B4,GS4,FS4,
        E4,T,T,T,T,T,R,R
    },
    { /* 7: Home in the Open Sky — E major, scarf theme with a warm answer */
        E4,T,B4,CS5,T,GS4,FS4,T,
        A4,T,GS4,FS4,E4,T,R,B3,
        CS4,E4,GS4,T,B4,T,A4,GS4,
        FS4,T,DS4,FS4,B4,T,T,R,
        E4,GS4,B4,T,CS5,E5,DS5,B4,
        CS5,T,A4,GS4,FS4,T,E4,R,
        A4,CS5,E5,T,DS5,CS5,B4,A4,
        GS4,T,FS4,DS4,E4,T,T,R,
        B4,T,E5,FS5,E5,T,CS5,B4,
        A4,CS5,E5,T,CS5,B4,A4,R,
        GS4,B4,CS5,DS5,E5,T,DS5,B4,
        FS4,A4,CS5,T,B4,GS4,FS4,R,
        E4,GS4,B4,CS5,E5,T,DS5,B4,
        A4,CS5,E5,FS5,E5,CS5,B4,A4,
        B4,DS5,FS5,T,E5,DS5,B4,FS4,
        GS4,T,FS4,DS4,E4,T,T,R
    }
};

/* Roots are in octave 3 for pulses, octave 2 for the wave bass.
 * Quality: 0 major, 1 minor, 2 suspended fourth, 3 dominant seventh. */
static const uint8_t roots[8][16] = {
    {E3,A3,CS3,B3,E3,FS3,A3,E3,CS3,A3,E3,B3,E3,A3,B3,E3},
    {E3,A3,CS3,B3,E3,FS3,A3,E3,CS3,A3,E3,B3,E3,A3,B3,E3},
    {D3,C3,AS3,G3,D3,C3,AS3,A3,AS3,C3,D3,G3,D3,C3,AS3,A3},
    {CS3,A3,FS3,GS3,CS3,A3,FS3,GS3,CS3,A3,FS3,B3,CS3,A3,FS3,GS3},
    {A3,FS3,E3,D3,A3,D3,E3,A3,FS3,D3,E3,A3,A3,D3,E3,A3},
    {CS3,A3,FS3,GS3,CS3,A3,FS3,GS3,CS3,A3,FS3,GS3,CS3,A3,FS3,GS3},
    {E3,A3,FS3,E3,E3,FS3,A3,E3,CS3,A3,B3,E3,E3,A3,B3,E3},
    {E3,A3,CS3,B3,E3,FS3,A3,E3,CS3,A3,E3,B3,E3,A3,B3,E3}
};
static const uint8_t qualities[8][16] = {
    {0,0,1,3,0,1,0,0,1,0,0,3,0,0,3,0},
    {0,0,1,3,0,1,0,0,1,0,0,3,0,0,3,0},
    {1,0,0,0,1,0,0,3,0,0,1,0,1,0,0,3},
    {1,0,1,3,1,0,1,3,1,0,1,0,1,0,1,3},
    {0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0},
    {1,0,1,3,1,0,1,3,1,0,1,3,1,0,1,3},
    {0,0,1,0,0,1,0,0,1,0,3,0,0,0,3,0},
    {0,0,1,3,0,1,0,0,1,0,0,3,0,0,3,0}
};
/* 60 fps frames/eighth: approximately 120,150,129,164,113,180,150,106 BPM. */
static const uint8_t tempos[8]={15,12,14,11,16,10,12,17};
static const uint8_t duties[8]={0x80,0x40,0x80,0x40,0x80,0x40,0x40,0x80};
static const uint8_t decays[8]={4,2,3,2,6,2,3,6};
static const uint8_t volumes[8]={5,6,5,5,5,6,6,5};
static const uint8_t counter_duties[8]={0x40,0x00,0x40,0x00,0x40,0x00,0x40,0x40};
/* Different chord rhythms, with deliberate holes for the tune and the SFX. */
static const uint8_t counter_masks[8]={0xA2,0xAA,0x52,0xB5,0x44,0xAD,0xAA,0xA2};
static const uint8_t arp_shapes[8][8]={
    {2,0,1,4,2,1,3,2}, {0,2,1,3,2,4,1,2},
    {3,1,2,0,4,2,1,3}, {0,3,1,2,0,2,4,1},
    {2,4,1,3,0,2,1,4}, {0,2,3,1,0,3,2,4},
    {0,1,2,3,2,1,4,2}, {2,0,1,4,3,1,2,4}
};
static const uint8_t bass_masks[8]={0x11,0x55,0x29,0xAD,0x11,0xDD,0x55,0x11};
static const uint8_t drum_patterns[8][8]={
    {1,0,0,3,2,0,3,0}, {1,3,2,3,1,0,2,3},
    {1,0,3,1,2,3,0,3}, {1,3,2,0,1,1,2,3},
    {1,0,0,0,2,0,3,0}, {1,3,2,1,1,3,2,3},
    {1,3,2,0,1,3,2,3}, {1,0,3,0,2,0,3,0}
};
static const uint8_t bass_wave[16]={
    0x89,0xAB,0xCD,0xEF,0xFE,0xDC,0xBA,0x98,
    0x76,0x54,0x32,0x10,0x01,0x23,0x45,0x67
};
static const uint8_t effect_lengths[8]={7,12,13,17,9,31,12,10};
static const uint8_t effect_priorities[8]={0,1,3,2,1,3,1,2};

static void quiet_lead(void){NR10_REG=0;NR12_REG=0x08;NR14_REG=0x80;}
static void quiet_counter(void){NR22_REG=0x08;NR24_REG=0x80;}
static void pulse_lead(uint8_t note,uint8_t v){
    uint16_t f=periods[note];
    NR10_REG=0;NR11_REG=duties[audio_track];NR12_REG=(v<<4)|lead_decay;
    NR13_REG=(uint8_t)f;NR14_REG=0x80u|(uint8_t)(f>>8);
}
static void pulse_counter(uint8_t note,uint8_t v,uint8_t duty,uint8_t decay){
    uint16_t f=periods[note];
    NR21_REG=duty;NR22_REG=(v<<4)|decay;
    NR23_REG=(uint8_t)f;NR24_REG=0x80u|(uint8_t)(f>>8);
}
static void restore_counter(void){
    if(counter_volume && counter_note<48u)
        pulse_counter(counter_note,counter_volume,counter_duties[audio_track],1);
    else quiet_counter();
}
static uint8_t chord_tone(uint8_t root,uint8_t quality,uint8_t index){
    uint8_t degree=arp_shapes[audio_track][index&7u];
    uint8_t third=quality==1u?3u:quality==2u?5u:4u;
    return root+12u+(degree==0u?0u:degree==1u?third:degree==2u?7u:degree==3u?12u:14u);
}
static void drum(uint8_t kind,uint8_t v){
    /* Noise length: kick 86 ms, snare 47 ms, closed hat 12 ms. */
    NR41_REG=kind==1u?42u:kind==2u?52u:61u;
    NR42_REG=(v<<4)|1u;
    NR43_REG=kind==1u?0x61u:kind==2u?0x42u:0x01u;
    NR44_REG=0xC0;
}
static void score_step(uint8_t step){
    uint8_t bar=step>>3,eighth=step&7u,section=bar>>2;
    uint8_t root=roots[audio_track][bar],q=qualities[audio_track][bar];
    uint8_t n=melody[audio_track][step],v,hit;
    uint16_t f;
    lead_volume=volumes[audio_track]+(section==2u?1u:0u);
    if(n!=T){
        lead_note=n;
        /* Long melody tones ring naturally; short notes retain their pluck.
         * Fast envelopes alone would silence a tie before it had finished. */
        lead_decay=melody[audio_track][(step+1u)&127u]==T?6u:decays[audio_track];
        if(n==R)quiet_lead();else pulse_lead(n,lead_volume);
    }
    if(counter_masks[audio_track]&(1u<<eighth)){
        counter_note=chord_tone(root,q,eighth+(section&1u));
        counter_volume=(section==0u?2u:3u)+(energy_on?1u:0u);
        if(!effect_left)restore_counter();
    }
    if(bass_masks[audio_track]&(1u<<eighth)){
        /* Root/fifth alternation with an octave pickup at the turnaround. */
        n=root+((eighth==2u||eighth==6u)?7u:0u);
        if(eighth==7u)n=root+12u;
        f=periods[n];wave_frequency=f;wave_volume=0x40;
        NR32_REG=wave_volume;NR31_REG=0;
        NR33_REG=(uint8_t)f;NR34_REG=0x80u|(uint8_t)(f>>8);
    }
    hit=drum_patterns[audio_track][eighth];
    if(section==0u && (audio_track==0u||audio_track==4u||audio_track==7u) && hit==2u)hit=0;
    if((bar&3u)==3u && eighth==7u && audio_track!=4u)hit=2;
    if(!hit && energy_on && (eighth&1u))hit=3;
    if(hit){v=hit==1u?3u:hit==2u?2u:1u;drum(hit,v);}
}

static void effect_tick(void){
    uint8_t n=E4,v=5,duty=0x40,decay=1,retrigger=0;
    uint16_t f;
    switch(effect_id){
    case 0: /* jump: quick fourth, a friendly rubbery hop */
        n=effect_age<3u?E4:A4;v=4;retrigger=effect_age==0u||effect_age==3u;break;
    case 1: /* star: light descending major third, then a high answer */
        n=effect_age<4u?E5:effect_age<8u?CS5:FS5;
        v=4;retrigger=(effect_age&3u)==0u;break;
    case 2: /* hurt: a brief falling low dyad */
        n=effect_age<4u?CS4:effect_age<8u?GS3:E3;
        v=6;duty=0x80;retrigger=(effect_age&3u)==0u;break;
    case 3: /* lantern: ascending open fifth / ninth, airy and clear */
        n=effect_age<4u?E4:effect_age<8u?B4:effect_age<12u?E5:FS5;
        v=4;duty=0x00;retrigger=(effect_age&3u)==0u;break;
    case 4: /* scarf dash: downward clean gliss, distinct from the jump */
        n=E5-effect_age;v=5;duty=0x00;retrigger=effect_age==0u;break;
    case 5: /* goal: scarf motif and a warm tonic landing */
        n=effect_age<5u?E4:effect_age<10u?B4:effect_age<15u?CS5:
          effect_age<20u?GS4:effect_age<25u?FS4:E4;
        v=6;duty=0x80;decay=3;retrigger=effect_age%5u==0u;break;
    case 6: /* spring: bouncy upward bend */
        n=CS4+effect_age;v=5;duty=0x80;retrigger=effect_age==0u;break;
    default: /* boss hit: two percussive brass notes */
        n=effect_age<5u?GS4:E4;v=6;duty=0x40;retrigger=effect_age==0u||effect_age==5u;break;
    }
    if(retrigger)pulse_counter(n,v,duty,decay);
    else if(effect_id==4u||effect_id==6u){
        f=periods[n];NR23_REG=(uint8_t)f;NR24_REG=(uint8_t)(f>>8);
    }
    effect_age++;effect_left--;
    if(!effect_left){effect_priority=0;restore_counter();}
}
static void power_up(void){
    uint8_t i;
    NR52_REG=0x80;NR50_REG=0x55;NR51_REG=0xFF;
    NR30_REG=0;for(i=0;i<16u;i++)AUD3WAVE[i]=bass_wave[i];NR30_REG=0x80;
    NR10_REG=0;NR12_REG=0x08;NR22_REG=0x08;NR42_REG=0x08;NR32_REG=0;
}
void audio_init(void) BANKED{
    power_up();audio_enabled=1;audio_track=255;audio_scene(0);
}
void audio_scene(uint8_t scene) BANKED{
    if(scene>7u)scene=0;
    if(scene==audio_track)return;
    audio_track=scene;audio_step=0;audio_loops=0;clock_tick=tempos[scene]-1u;
    effect_left=0;effect_priority=0;energy_on=0;lead_note=R;
    counter_note=R;counter_volume=wave_volume=0;lead_volume=volumes[scene];
    lead_decay=decays[scene];
    if(audio_enabled){quiet_lead();quiet_counter();NR32_REG=0;NR42_REG=0x08;NR44_REG=0x80;}
}
void audio_tick(uint8_t energy) BANKED{
    if(!audio_enabled)return;
    energy_on=energy!=0u;
    if(effect_left)effect_tick();
    if(++clock_tick>=tempos[audio_track]){
        clock_tick=0;score_step(audio_step);audio_step=(audio_step+1u)&127u;
        if(!audio_step)audio_loops++;
    }else if(clock_tick==tempos[audio_track]-2u){
        /* A tiny articulation gap; tied melody notes stay unbroken. */
        if(melody[audio_track][audio_step]!=T)quiet_lead();
        if(!effect_left)quiet_counter();
    }
}
void audio_sfx(uint8_t effect) BANKED{
    if(!audio_enabled||effect>7u)return;
    if(effect_left&&effect_priorities[effect]<effect_priority)return;
    effect_id=effect;effect_left=effect_lengths[effect];effect_age=0;
    effect_priority=effect_priorities[effect];effect_tick();
}
void audio_enable(uint8_t enabled) BANKED{
    enabled=enabled!=0u;if(enabled==audio_enabled)return;
    audio_enabled=enabled;
    if(!enabled){NR52_REG=0;effect_left=0;effect_priority=0;}
    else{
        power_up();restore_counter();
        if(wave_volume){NR32_REG=wave_volume;NR33_REG=(uint8_t)wave_frequency;NR34_REG=0x80u|(uint8_t)(wave_frequency>>8);}
        if(lead_note<48u)pulse_lead(lead_note,lead_volume);else quiet_lead();
    }
}
