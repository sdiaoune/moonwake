#!/usr/bin/env python3
"""Render Moonwake's native APU using PyBoy, not synthetic host instruments.

The small harness links the exact production src/music.c in bank 7. Harness
RAM controls select scenes and trigger effects; no soundtrack code is copied.
A fixed 20Hz high-pass removes PyBoy's unsigned DAC DC offset (the physical GB
has an analog high-pass), then a fixed gain encodes 16-bit stereo WAV. There is
no per-track normalization, EQ, reverb, limiter or rearrangement.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, wave, importlib.metadata, os
import numpy as np
from pyboy import PyBoy
ROOT=Path(__file__).resolve().parents[1]
GBDK=Path(os.environ.get('GBDK', '/opt/gbdk'))
OUT=ROOT/'docs/audio'
BUILD=ROOT/'build/audio-harness'
TRACKS=['01-a-scarf-for-the-sleeping-sea','02-persimmon-postcard',
        '03-rain-on-a-giant-lotus','04-brass-clock-violet-sky',
        '05-the-whale-that-carried-tomorrow','06-wake-up-sleepstorm',
        '07-a-little-more-sky','08-home-in-the-open-sky']
TEMPOS=[15,12,14,11,16,10,12,17]
HARNESS=r'''
#include <gb/gb.h>
#include <stdint.h>
#include "music.h"
volatile uint8_t render_scene=0,render_energy=0,render_effect=255,render_mute=0,render_reset=0;
volatile uint16_t render_frames=0;
volatile uint8_t render_lead_regs[5];
volatile uint8_t render_test_mode=0,render_test_reset=0;
volatile uint16_t render_test_frames=0,render_test_hash=5381;
extern uint8_t audio_step;
void main(void) {
    audio_init();
    while(1) {
        vsync();
        if(render_test_reset) {
            audio_init();render_test_reset=0;render_test_frames=0;render_test_hash=5381;
        }
        if(render_reset) { audio_init(); render_reset=0; }
        audio_scene(render_scene);
        audio_enable(!render_mute);
        if(render_effect!=255) { audio_sfx(render_effect); render_effect=255; }
        if(render_test_mode==2 && render_test_frames%60u==20u)
            audio_sfx((uint8_t)(render_test_frames/60u));
        audio_tick(render_energy);
        render_lead_regs[0]=NR10_REG; render_lead_regs[1]=NR11_REG;
        render_lead_regs[2]=NR12_REG; render_lead_regs[3]=NR13_REG;
        render_lead_regs[4]=NR14_REG;
        if(render_test_mode && render_test_frames<480u) {
            render_test_hash=(render_test_hash*33u)^render_lead_regs[0];
            render_test_hash=(render_test_hash*33u)^render_lead_regs[1];
            render_test_hash=(render_test_hash*33u)^render_lead_regs[2];
            render_test_hash=(render_test_hash*33u)^audio_step;
            render_test_frames++;
            if(render_test_frames==480u)render_test_mode=0;
        }
        render_frames++;
    }
}
'''
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
    return rom,symbols

def write_wav(path,samples,sample_rate):
    raw=np.asarray(samples,dtype=np.float64).reshape(-1,2)
    # x[n]-x[n-1]+a*y[n-1]: deterministic first-order hardware-like DC removal.
    a=float(np.exp(-2*np.pi*20/sample_rate))
    y=np.empty_like(raw);prev_x=np.zeros(2);prev_y=np.zeros(2)
    for i,x in enumerate(raw):
        cur=x-prev_x+a*prev_y
        y[i]=cur;prev_x=x;prev_y=cur
    scaled=np.rint(y*900)
    clips=int(np.count_nonzero(np.abs(scaled)>32767))
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

def record_tracks(rom,symbols):
    reports=[]
    for t,name in enumerate(TRACKS):
        pb=emulator(rom)
        pb.memory[symbols['_render_scene'][1]]=t
        pb.memory[symbols['_render_reset'][1]]=1
        pb.tick(render=False,sound=True)
        parts=[];status_counts=[]
        frames=TEMPOS[t]*128
        for f in range(frames):
            # Energy enters for the B section, recedes before the final cadence.
            pb.memory[symbols['_render_energy'][1]]=int(frames//2<=f<frames*3//4)
            pb.tick(render=False,sound=True)
            parts.append(pb.sound.ndarray.copy())
            status_counts.append(pb.memory[0xFF26]&15)
        path=OUT/(name+'.wav')
        report=write_wav(path,np.concatenate(parts),pb.sound.sample_rate)
        report.update({'scene':t,'name':name,'score_frames':frames,
                       'channels_observed':int(np.bitwise_or.reduce(status_counts)),
                       'energy_frames':[frames//2,frames*3//4],
                       'phrase_steps':128,'score_step_after':pb.memory[symbols['_audio_step'][1]],
                       'score_loops_after':pb.memory[symbols['_audio_loops'][1]]})
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
    for f in range(90):
        pb.tick(render=False,sound=True);parts.append(pb.sound.ndarray.copy());frame+=1
    res=write_wav(OUT/'09-sfx-and-mute.wav',np.concatenate(parts),pb.sound.sample_rate)
    res.update({'effects':list(range(8)),'sfx_frame_positions':event_positions,
                'muted_frames_checked':mute_frames,'mute_nonzero_samples':mute_nonzero,
                'mute_freezes_score':before==after,'channels_after_resume':pb.memory[0xFF26]&15})
    pb.stop(save=False)
    print('sfx and mute',res,flush=True)
    return res

def check_sfx_melody_preserved(rom,symbols):
    """Compare actual channel1 registers with/without SFX in the same score.

    The capture changes harness inputs only. No campaign memory is edited.
    """
    hashes=[];emulated_frame_counts=[]
    for effects in (False,True):
        pb=emulator(rom)
        pb.memory[symbols['_render_scene'][1]]=1
        pb.memory[symbols['_render_test_reset'][1]]=1
        pb.memory[symbols['_render_test_mode'][1]]=2 if effects else 1
        emu_frames=0
        while True:
            pb.tick(render=False,sound=True)
            emu_frames+=1
            ad=symbols['_render_test_frames'][1]
            now=pb.memory[ad] | (pb.memory[ad+1]<<8)
            if now==480:break
            assert emu_frames<500, 'Audio harness fell behind video frames'
        ad=symbols['_render_test_hash'][1]
        hashes.append(pb.memory[ad] | (pb.memory[ad+1]<<8));pb.stop(save=False)
        emulated_frame_counts.append(emu_frames)
    return {'channel1_registers_identical':hashes[0]==hashes[1],
            'frames_compared':480,'effects_tested':list(range(8)),
            'emulated_frames_without_and_with_sfx':emulated_frame_counts,
            'register_hashes_without_and_with_sfx':hashes,
            'method':'16-bit rolling hash of NR10/NR11/NR12 and audio_step after every sequencer tick'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--quick',action='store_true')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    rom,symbols=build()
    report={'method':'Exact production music.c linked to a bank7 CGB harness, rendered by PyBoy '+importlib.metadata.version('pyboy'),
            'sample_rate':24000,'encoding':'16-bit stereo, fixed gain900, 20Hz DC-removal only',
            'music_sha256':hashlib.sha256((ROOT/'src/music.c').read_bytes()).hexdigest(),
            'harness_sha256':hashlib.sha256(rom.read_bytes()).hexdigest(),
            'tracks':[] if args.quick else record_tracks(rom,symbols),
            'effects_and_mute':record_sfx(rom,symbols),
            'sfx_preserves_melody':check_sfx_melody_preserved(rom,symbols)}
    assert report['sfx_preserves_melody']['channel1_registers_identical'], 'SFX interrupted the melody'
    assert report['effects_and_mute']['mute_freezes_score'], 'Mute moved score position'
    assert report['effects_and_mute']['mute_nonzero_samples']==0, 'Muted APU produced samples'
    for track in report['tracks']:
        assert track['channels_observed']==15, 'Missing native sound channel'
        assert track['clipped_samples']==0, 'PCM capture clipped'
    (OUT/'render-report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
