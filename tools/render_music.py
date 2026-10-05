#!/usr/bin/env python3
"""Capture the exact production sequencer through PyBoy's native four-channel APU.

Fixed 20 Hz DAC DC removal and gain 900 encode stereo PCM; no normalization,
limiting, reverb, samples, or host-instrument arrangement is added. Tests use
harness controls, not campaign or production state edits.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, wave, importlib.metadata, os, re
import numpy as np
from pyboy import PyBoy
ROOT=Path(__file__).resolve().parents[1]
# Both conventional GBDK installs and this project's portable toolchain work.
GBDK=Path(os.environ.get('GBDK', ROOT.parents[1]/'.tools/gbdk'))
if not (GBDK/'bin/lcc').exists(): GBDK=Path('/opt/gbdk')
OUT=ROOT/'docs/audio'
BUILD=ROOT/'build/audio-harness'
TRACKS=['01-a-scarf-for-the-sleeping-sea','02-persimmon-postcard',
        '03-rain-on-a-giant-lotus','04-brass-clock-violet-sky',
        '05-the-whale-that-carried-tomorrow','06-wake-up-sleepstorm',
        '07-a-little-more-sky','08-home-in-the-open-sky',
        '10-paper-lanterns-amber-sparks','11-constellations-in-a-teacup',
        '12-apples-of-the-northern-lights','13-margins-full-of-morning',
        '14-ring-the-rainbell','15-the-manta-writes-a-meteor',
        '16-a-prism-with-no-shadow']
PHRASE_STEPS=256
FRAME_CYCLES=70224
HARNESS=r'''
#include <gb/gb.h>
#include <stdint.h>
#include "music.h"
volatile uint8_t render_scene=0,render_energy=0,render_effect=255,render_mute=0,render_reset=0;
volatile uint16_t render_frames=0;
volatile uint8_t render_lead_regs[4],render_max_div=0;
volatile uint8_t render_test_mode=0,render_test_reset=0;
volatile uint16_t render_test_frames=0;
volatile uint8_t render_test_trace[2400];
extern uint8_t audio_step,audio_lead_note;
void main(void) {
    uint8_t stamp,cost,j,trigger;
    uint16_t trace;
    audio_init();
    while(1) {
        vsync();
        if(render_test_reset) {
            audio_init();render_test_reset=0;render_test_frames=0;render_max_div=0;
        }
        if(render_reset) { audio_init(); render_reset=0;render_max_div=0; }
        audio_scene(render_scene);
        audio_enable(!render_mute);
        trigger=render_effect;render_effect=255;
        if(render_test_mode==2 && render_test_frames%60u==20u)
            trigger=(uint8_t)(render_test_frames/60u);
        stamp=DIV_REG;
        if(trigger!=255)audio_sfx(trigger);
        audio_tick(render_energy);
        cost=DIV_REG-stamp;
        if(cost>render_max_div)render_max_div=cost;
        render_lead_regs[0]=NR10_REG; render_lead_regs[1]=NR11_REG;
        render_lead_regs[2]=NR12_REG; render_lead_regs[3]=audio_lead_note;
        if(render_test_mode && render_test_frames<480u) {
            trace=render_test_frames*5u;
            for(j=0;j<4u;j++)render_test_trace[trace+j]=render_lead_regs[j];
            render_test_trace[trace+4u]=audio_step;
            render_test_frames++;
            if(render_test_frames==480u)render_test_mode=0;
        }
        render_frames++;
    }
}
'''

def score_metadata():
    source=(ROOT/'src/music.c').read_text()
    tempos=[int(x.strip()) for x in re.search(r'tempos\[AUDIO_SCENE_COUNT\]=\{(.*?)\}',source)[1].split(',')]
    constants={name:int(value) for name,value in re.findall(r'^#define\s+(\w+)\s+(\d+)u$',source,re.M)}
    constants['ES5']=constants['F5']
    body=source.split('static const uint8_t melody[AUDIO_SCENE_COUNT][256] = {',1)[1].split('\n};',1)[0]
    phrases=[]
    for phrase in re.findall(r'\{ /\*.*?\*/(.*?)\n    \}',body,re.S):
        notes=[constants[token.strip()] for token in phrase.split(',')]
        assert len(notes)==PHRASE_STEPS, 'Incomplete 32-bar phrase'
        assert all(n<48 or n in (254,255) for n in notes), 'APU period out of bounds'
        assert notes[0]!=255, 'Phrase starts with an uninitialized tie'
        phrases.append(notes)
    assert len(tempos)==len(phrases)==len(TRACKS)==15
    # Each newly authored melody must have a distinct interval/rhythm identity;
    # absolute pitch alone would allow a transposed copy to pass this check.
    identities=[]
    for notes in phrases:
        previous=next(n for n in notes if n<48)
        identity=[]
        for n in notes:
            if n<48: identity.append(n-previous);previous=n
            else: identity.append(n)
        identities.append(identity)
    assert all(identities[t]!=identities[o] for t in range(8,15) for o in range(t)), 'Transposed duplicate theme'
    return tempos,{'phrases':len(phrases),'bars_per_phrase':32,'steps_per_phrase':256,
        'new_scenes_have_distinct_interval_and_rhythm_sequences':True,
        'unique_melody_sha256':[hashlib.sha256(bytes(n)).hexdigest() for n in phrases]}

def build():
    BUILD.mkdir(parents=True,exist_ok=True)
    (BUILD/'main.c').write_text(HARNESS)
    rom=BUILD/'audio.gb'
    subprocess.run([str(GBDK/'bin/lcc'),'-I'+str(ROOT/'src'),'-Wl-m','-Wl-j',
                    '-Wm-yC','-Wm-yS','-Wm-yt0x19','-Wm-yo8','-Wm-ynWAKEAUDIO',
                    '-o',str(rom),str(BUILD/'main.c'),str(ROOT/'src/music.c')],check=True)
    symbols={}
    for line in rom.with_suffix('.sym').read_text().splitlines():
        s=line.split()
        if len(s)==2 and ':' in s[0]:
            bank,addr=s[0].split(':')
            symbols[s[1]]=(int(bank,16),int(addr,16))
    used=int(re.search(r'^_CODE_7\s+\w+\s+(\w+)',rom.with_suffix('.map').read_text(),re.M)[1],16)
    assert used<=16384, 'Music overflowed bank 7'
    return rom,symbols,used

def read16(pb,symbols,name):
    address=symbols[name][1]
    return pb.memory[address] | (pb.memory[address+1]<<8)

def write_wav(path,samples,sample_rate):
    raw=np.asarray(samples,dtype=np.float64).reshape(-1,2)
    # x[n]-x[n-1]+a*y[n-1]: deterministic first-order hardware-like DC removal.
    a=float(np.exp(-2*np.pi*20/sample_rate))
    y=np.empty_like(raw);prev_x=np.zeros(2);prev_y=np.zeros(2)
    for i,x in enumerate(raw):
        cur=x-prev_x+a*prev_y
        y[i]=cur;prev_x=x;prev_y=cur
    scaled=np.rint(y*900)
    clips=int(np.count_nonzero((scaled>32767)|(scaled<-32768)))
    pcm=np.clip(scaled,-32768,32767).astype('<i2')
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(sample_rate);f.writeframes(pcm.tobytes())
    return {'seconds':round(len(raw)/sample_rate,3),'raw_dac_peak':float(raw.max()),
            'pcm_peak':int(np.abs(pcm.astype(np.int32)).max()),'clipped_samples':clips,
            'rms':round(float(np.sqrt(np.mean(pcm.astype(np.float64)**2))),2),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def emulator(rom):
    pb=PyBoy(str(rom),window='null',sound_emulated=True,sound_sample_rate=24000)
    pb.set_emulation_speed(0)
    for _ in range(90):pb.tick(render=False,sound=True)
    return pb

def record_tracks(rom,symbols,tempos):
    reports=[]
    for t,name in enumerate(TRACKS):
        pb=emulator(rom)
        pb.memory[symbols['_render_scene'][1]]=t
        pb.memory[symbols['_render_reset'][1]]=1
        pb.tick(render=False,sound=True)
        parts=[];status_counts=[];step_changes=0;prev=pb.memory[symbols['_audio_step'][1]]
        frame_start=read16(pb,symbols,'_render_frames')
        frames=tempos[t]*PHRASE_STEPS
        for f in range(frames):
            # Energy enters during each third section, recedes for its cadence.
            pb.memory[symbols['_render_energy'][1]]=int(frames//4<=f<frames*3//8 or frames*3//4<=f<frames*7//8)
            pb.tick(render=False,sound=True)
            parts.append(pb.sound.ndarray.copy())
            status_counts.append(pb.memory[0xFF26]&15)
            now=pb.memory[symbols['_audio_step'][1]]
            if now!=prev:step_changes+=1
            prev=now
        report=write_wav(OUT/(name+'.wav'),np.concatenate(parts),pb.sound.sample_rate)
        report.update({'scene':t,'name':name,'score_frames':frames,
                       'channels_observed':int(np.bitwise_or.reduce(status_counts)),
                       'channel_active_frames':[sum(bool(s&(1<<c)) for s in status_counts) for c in range(4)],
                       'energy_frames':[[frames//4,frames*3//8],[frames*3//4,frames*7//8]],
                       'phrase_bars':32,'phrase_steps':PHRASE_STEPS,'observed_step_advances':step_changes,
                       'score_step_after':pb.memory[symbols['_audio_step'][1]],
                       'score_loops_after':read16(pb,symbols,'_audio_loops'),
                       'harness_video_frames':(read16(pb,symbols,'_render_frames')-frame_start)&65535,
                       'max_audio_div_ticks':pb.memory[symbols['_render_max_div'][1]]})
        pb.stop(save=False)
        reports.append(report)
        print(name,report,flush=True)
    return reports

def record_sfx(rom,symbols):
    pb=emulator(rom)
    pb.memory[symbols['_render_scene'][1]]=1
    parts=[];event_positions=[]
    mute_frames=0;mute_nonzero=0
    frame=0
    for e in range(8):
        for f in range(120):
            if f==30:
                pb.memory[symbols['_render_effect'][1]]=e;event_positions.append(frame)
            pb.tick(render=False,sound=True);parts.append(pb.sound.ndarray.copy());frame+=1
    before=pb.memory[symbols['_audio_step'][1]]
    pb.memory[symbols['_render_mute'][1]]=1
    for f in range(45):
        pb.tick(render=False,sound=True)
        chunk=pb.sound.ndarray.copy();parts.append(chunk);frame+=1
        # The first mute frame can contain samples before the vblank write.
        if f>0:
            mute_frames+=1;mute_nonzero+=int(np.count_nonzero(chunk))
    after=pb.memory[symbols['_audio_step'][1]]
    pb.memory[symbols['_render_mute'][1]]=0
    resumed_channels=0
    for f in range(90):
        pb.tick(render=False,sound=True);parts.append(pb.sound.ndarray.copy());frame+=1
        resumed_channels|=pb.memory[0xFF26]&15
    res=write_wav(OUT/'09-sfx-and-mute.wav',np.concatenate(parts),pb.sound.sample_rate)
    res.update({'effects':list(range(8)),'sfx_frame_positions':event_positions,
                'muted_frames_checked':mute_frames,'mute_nonzero_samples':mute_nonzero,
                'mute_freezes_score':before==after,'channels_observed_after_resume':resumed_channels})
    pb.stop(save=False)
    print('sfx and mute',res,flush=True)
    return res

def check_sfx_melody_preserved(rom,symbols):
    """Compare every frame's channel-1 instrument, played note, and score clock.

    Frequency registers are write-only. The source's observable played-note
    counter verifies pitch without pretending those registers can be read.
    """
    results=[]
    for scene in range(len(TRACKS)):
        captures=[];emulated_frame_counts=[];div_max=0
        for effects in (False,True):
            pb=emulator(rom)
            pb.memory[symbols['_render_scene'][1]]=scene
            pb.memory[symbols['_render_test_reset'][1]]=1
            pb.memory[symbols['_render_test_mode'][1]]=2 if effects else 1
            emu_frames=0
            while True:
                pb.tick(render=False,sound=True);emu_frames+=1
                now=read16(pb,symbols,'_render_test_frames')
                if now==480:break
                assert emu_frames<500, 'Audio harness fell behind video frames'
            trace=symbols['_render_test_trace'][1]
            captures.append(bytes(pb.memory[trace+i] for i in range(2400)))
            div_max=max(div_max,pb.memory[symbols['_render_max_div'][1]])
            pb.stop(save=False);emulated_frame_counts.append(emu_frames)
        results.append({'scene':scene,'channel1_state_identical':captures[0]==captures[1],
            'frames_compared':480,'effects_tested':list(range(8)),
            'emulated_frames_without_and_with_sfx':emulated_frame_counts,
            'sha256_without_and_with_sfx':[hashlib.sha256(c).hexdigest() for c in captures],
            'max_audio_and_sfx_div_ticks':div_max})
        print('lead continuity',scene,results[-1]['channel1_state_identical'],flush=True)
    return {'all_scenes_preserved':all(r['channel1_state_identical'] for r in results),'scenes':results,
        'method':'Exact per-frame byte comparison of NR10/NR11/NR12, observable played lead note, and audio_step'}

def check_scene_controls(rom,symbols):
    results=[]
    for scene in range(len(TRACKS)):
        pb=emulator(rom)
        pb.memory[symbols['_render_scene'][1]]=scene
        for _ in range(60):pb.tick(render=False,sound=True)
        before=(pb.memory[symbols['_audio_step'][1]],read16(pb,symbols,'_audio_loops'))
        pb.memory[symbols['_render_mute'][1]]=1
        nonzero=0
        for frame in range(45):
            pb.tick(render=False,sound=True)
            if frame:nonzero+=int(np.count_nonzero(pb.sound.ndarray))
        after=(pb.memory[symbols['_audio_step'][1]],read16(pb,symbols,'_audio_loops'))
        pb.memory[symbols['_render_mute'][1]]=0
        channels=0
        for _ in range(150):
            pb.tick(render=False,sound=True);channels|=pb.memory[0xFF26]&15
        # The harness reselects the same scene every video frame. Completing
        # these steps also checks the API's promise not to restart that scene.
        advanced=pb.memory[symbols['_audio_step'][1]]!=after[0]
        results.append({'scene':scene,'muted_frames_checked':44,
            'mute_nonzero_samples':nonzero,'score_position_preserved':before==after,
            'resumed_channels_observed':channels,'same_scene_selection_allows_progress':advanced})
        pb.memory[symbols['_render_scene'][1]]=255
        pb.tick(render=False,sound=True);pb.tick(render=False,sound=True)
        assert pb.memory[symbols['_audio_track'][1]]==0, 'Invalid scene did not select title'
        pb.stop(save=False)
    return {'all_scenes_passed':all(r['mute_nonzero_samples']==0 and r['score_position_preserved'] and
        r['resumed_channels_observed']==15 and r['same_scene_selection_allows_progress'] for r in results),
        'invalid_scene_selects_title':True,'scenes':results}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--quick',action='store_true')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    tempos,score_checks=score_metadata()
    rom,symbols,used=build()
    report={'method':'Exact production music.c linked to bank7 CGB harness, rendered by PyBoy '+importlib.metadata.version('pyboy'),
            'sample_rate':24000,'encoding':'16-bit stereo, fixed gain900, 20Hz DC-removal only',
            'music_sha256':hashlib.sha256((ROOT/'src/music.c').read_bytes()).hexdigest(),
            'harness_sha256':hashlib.sha256(rom.read_bytes()).hexdigest(),
            'music_bank7_bytes':used,'music_bank7_capacity':16384,
            'score_checks':score_checks,
            'tracks':[] if args.quick else record_tracks(rom,symbols,tempos),
            'effects_and_mute':record_sfx(rom,symbols),
            'sfx_preserves_melody':check_sfx_melody_preserved(rom,symbols),
            'scene_controls':check_scene_controls(rom,symbols)}
    div_max=max([t['max_audio_div_ticks'] for t in report['tracks']]+[t['max_audio_and_sfx_div_ticks'] for t in report['sfx_preserves_melody']['scenes']])
    cycle_bound=(div_max+1)*256
    report['cpu_observation']={'max_div_ticks':div_max,'conservative_audio_cycle_upper_bound':cycle_bound,
        'video_frame_cycles':FRAME_CYCLES,'frame_budget_percent_upper_bound':round(cycle_bound/FRAME_CYCLES*100,2),
        'method':'DIV before/after BANKED audio_tick plus any SFX dispatch; 256-cycle resolution, normal-speed CGB; excludes rendering/game logic'}
    assert report['sfx_preserves_melody']['all_scenes_preserved'], 'SFX interrupted the melody'
    assert report['effects_and_mute']['mute_freezes_score'], 'Mute moved score position'
    assert report['effects_and_mute']['mute_nonzero_samples']==0, 'Muted APU produced samples'
    assert report['effects_and_mute']['channels_observed_after_resume']==15, 'Mute did not restore all channels'
    assert report['effects_and_mute']['clipped_samples']==0, 'SFX capture clipped'
    assert report['scene_controls']['all_scenes_passed'], 'Mute, resume, or scene selection failed'
    for track in report['tracks']:
        assert track['channels_observed']==15, 'Missing native sound channel'
        assert track['clipped_samples']==0, 'PCM capture clipped'
        assert track['observed_step_advances']==PHRASE_STEPS and track['score_loops_after']==1, 'Phrase did not complete exactly'
        assert track['harness_video_frames']==track['score_frames'], 'Audio fell behind video frames'
    print('CPU observation',report['cpu_observation'],flush=True)
    assert cycle_bound<FRAME_CYCLES//4, 'Audio exceeded 25% native frame budget'
    (OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('CPU and bank budget',report['cpu_observation'],'bank7',used,flush=True)
if __name__=='__main__':main()
