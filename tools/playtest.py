"""Controller-only native ROM planner. Branches emulator states; never edits RAM.
The resulting controller recording is replayed linearly from a fresh save.
"""
from pathlib import Path
import io,json,re,hashlib,sys
from PIL import Image
from pyboy import PyBoy
ROOT=Path(__file__).resolve().parents[1]
ROUTES=json.loads((ROOT/'docs/routes.json').read_text())['levels']
ROM=ROOT/'dist/moonwake.gbc'
SYMS={s[1]:(int(s[0].split(':')[0],16),int(s[0].split(':')[1],16)) for l in ROM.with_suffix('.sym').read_text().splitlines() if len(s:=l.split())==2 and ':' in s[0]}
class Tester:
 def __init__(self,ram=None):
  self.ram=ram or io.BytesIO(bytes(8192));self.p=PyBoy(str(ROM),window='null',cgb=True,ram_file=self.ram,sound_emulated=True);self.p.set_emulation_speed(0);self.held=set();self.frames=0;self.trace=[];self.observed={};self.p.hook_register(*SYMS['_draw_objects'],self.observe,None)
 def raw(self,n,size=1,signed=False):
  a=SYMS['_'+n][1];v=sum(self.p.memory[a+i]<<(i*8) for i in range(size));return v-(1<<(size*8)) if signed and v>=(1<<(size*8-1)) else v
 def observe(self,_):
  self.observed={n:self.raw(n,z,s) for n,z,s in [('player_x',2,True),('player_y',2,True),('velocity_x',2,True),('velocity_y',2,True),('grounded',1,False)]}
 def read(self,n,size=1,signed=False):return self.observed.get(n,self.raw(n,size,signed))
 def pos(self):return self.read('player_x',2,True)/16,self.read('player_y',2,True)/16
 def state(self):return {'x':self.pos()[0],'y':self.pos()[1],'vx':self.read('velocity_x',2,True)/16,'vy':self.read('velocity_y',2,True)/16,**{n:self.read(n) for n in ['game_mode','stage_id','health','grounded','dash_charge','seal_count']},'deaths':self.read('deaths',2),'camera':self.read('camera_x',2)}
 def tick(self,n=1,buttons=()):
  buttons=set(buttons)
  for b in self.held-buttons:self.p.button_release(b)
  for b in buttons-self.held:self.p.button_press(b)
  self.held=buttons;self.p.tick(n);self.frames+=n;self.trace.append([n,sorted(buttons)])
 def tap(self,b,wait=12):self.tick(3,[b]);self.tick(wait)
 def shot(self,name):
  d=ROOT/'docs/screenshots';d.mkdir(parents=True,exist_ok=True);self.p.screen.image.save(d/(name+'-native.png'));self.p.screen.image.resize((800,720),Image.Resampling.NEAREST).save(d/(name+'.png'))
 def checkpoint(self):
  s=io.BytesIO();self.p.save_state(s);return s.getvalue(),self.held.copy(),self.frames,len(self.trace),dict(self.observed)
 def rollback(self,s):self.p.load_state(io.BytesIO(s[0]));self.held=s[1].copy();self.frames=s[2];self.trace=self.trace[:s[3]];self.observed=dict(s[4])
 def start(self):
  self.tick(180);self.shot('title');self.tap('start',120);self.shot('story');self.tap('a',90);assert self.read('game_mode')==1,self.state();self.shot('harbor')
 def current_platform(self):
  x,y=self.pos();r=ROUTES[self.read('stage_id')]
  for i,p in enumerate(r['platforms']):
   if x+12>p['x'] and x+3<p['x']+p['w'] and abs(y+16-p['y'])<2:return i
  return None
 def walk(self,target,limit=220):
  death=self.read('deaths',2)
  for _ in range(limit):
   x,y=self.pos();vx=self.read('velocity_x',2,True)/16;delta=target-x
   if abs(delta)<2 and abs(vx)<.35 and self.read('grounded'):self.tick(2);return
   steer=[] if abs(delta)<abs(vx)**2*1.4+1 and delta*vx>=0 else ['right' if delta>0 else 'left']
   # Dash through a patrol on the same safe platform. Keep jumps separate.
   r=ROUTES[self.read('stage_id')]
   near=any(e['kind']!=2 and abs(e['x']-x)<22 and abs(e['y']-y)<12 for e in r['enemies'])
   # Walk does not auto-dash: preserve the intended launch edge.
   self.tick(1,steer)
   if self.read('deaths',2)!=death:raise AssertionError(('walk died',target,self.state()))
   if self.read('game_mode')!=1:return
  raise AssertionError(('walk timeout',target,self.state()))
 def jump(self,index,collect=None):
  r=ROUTES[self.read('stage_id')];p=r['platforms'][index]
  # A foe can knock Kip airborne just after landing. Wait for the recoil
  # to settle before issuing the next jump; do not assume a double jump.
  if not self.read('grounded') and self.current_platform() is None:
   settle=self.checkpoint();death=self.read('deaths',2)
   for _ in range(45):
    self.tick(1)
    if self.read('grounded') or self.read('deaths',2)!=death:break
   if self.read('deaths',2)!=death:self.rollback(settle)
  base=self.checkpoint();cp=self.current_platform()
  targets=[p['x']+p['w']/2-8,p['x']+8,p['x']+p['w']-24]
  if collect is not None:targets=[r['pickups'][collect]['x']-4]+targets
  for target in targets:
   for hold in [24,36,14,48]:
    for dash_at in [-1,10,17,5]:
     self.rollback(base);death=self.read('deaths',2)
     if cp is not None and r['platforms'][cp]['kind'] not in (2,3):
      src=r['platforms'][cp];x,y=self.pos();launch=x if abs(target-x)<=72 else max(src['x']-2,min(src['x']+src['w']-16,target-52 if target>x else target+52))
      try:self.walk(launch,180)
      except AssertionError:self.rollback(base)
     self.tick(2);air=False
     for f in range(110):
      x,y=self.pos();vx=self.read('velocity_x',2,True)/16;delta=target-x
      buttons=['a'] if f<hold else []
      if abs(delta)>abs(vx)**2*1.25+1 or delta*vx<0:buttons+=['right' if delta>0 else 'left']
      if f==dash_at:buttons+=['b']
      self.tick(1,buttons)
      if not self.read('grounded'):air=True
      if self.read('deaths',2)!=death or self.read('game_mode')!=1:break
      x,y=self.pos();taken=collect is None or self.p.memory[SYMS['_pickup_taken'][1]+collect]
      if air and f>5 and x+12>p['x'] and x+3<p['x']+p['w'] and abs(y+16-p['y'])<2 and taken and (self.read('grounded') or p['kind']==2 and self.read('velocity_y',2,True)<0):
       if p['kind']!=2:
        self.tick(3)
        if self.read('deaths',2)!=death or self.read('game_mode')!=1:break
       return
  self.rollback(base);(ROOT/'build/failed-state.bin').write_bytes(base[0]);(ROOT/'build/failed-state.json').write_text(json.dumps({'held':list(base[1]),'frames':base[2],'observed':base[4],'trace':self.trace}));raise AssertionError(('cannot jump',index,collect,self.state(),p))
 def boss(self):
  r=ROUTES[11]
  # Deflect a low shot and cross the broad arena before attacking from
  # the opposite side. The whale's first projectile lane points left.
  self.tick(10,['right','b']);self.tick(3,['right']);self.walk(r['goal_x']+24)
  base=self.checkpoint();(ROOT/'build/boss-state.bin').write_bytes(base[0]);(ROOT/'build/boss-state.json').write_text(json.dumps({'held':list(base[1]),'frames':base[2],'observed':base[4],'trace':self.trace}));self.shot('boss')
  for hit in range(6):
   base=self.checkpoint();hp=self.read('boss_hp');death=self.read('deaths',2);hp_before=self.read('health');success=False
   for wait in [0,15,30,45,60]:
    for dash_at in [14,10,18,22,-1]:
     self.rollback(base);self.tick(wait);self.tick(2)
     for f in range(95):
      x,y=self.pos();bossx=r['goal_x']-48;target=bossx+4;vx=self.read('velocity_x',2,True)/16;delta=target-x
      buttons=['a'] if f<36 else []
      if abs(delta)>abs(vx)**2*1.25+1 or delta*vx<0:buttons+=['right' if delta>0 else 'left']
      if f==dash_at:buttons+=['b']
      self.tick(1,buttons)
      if self.read('deaths',2)!=death:break
      if self.read('boss_hp')<hp:
       if not self.read('boss_hp'):success=True
       else:
        recoil=self.checkpoint()
        for hold in [28,40,20,0]:
         for dash in [-1,38,48,25]:
          self.rollback(recoil);target=r['goal_x']+24
          for recovery in range(56):
           x,y=self.pos();vx=self.read('velocity_x',2,True)/16;delta=target-x;retreat=['a'] if recovery<hold else []
           if abs(delta)>abs(vx)**2*1.25+1 or delta*vx<0:retreat+=['right' if delta>0 else 'left']
           if recovery==dash:retreat+=['b']
           self.tick(1,retreat)
           if self.read('deaths',2)!=death:break
          if self.read('deaths',2)==death and self.read('health')>=hp_before and self.read('grounded'):success=True;break
         if success:break
       if success:self.shot('boss-hit-'+str(hit+1))
       break
     if success:break
    if success:break
   assert success,('boss hit failed',hp,self.state())
  assert not self.read('boss_hp'),self.state()
 def finish(self):
  r=ROUTES[self.read('stage_id')];death=self.read('deaths',2)
  for _ in range(250):
   if self.read('game_mode')==3:break
   x,y=self.pos();buttons=['right']
   near=any(e['kind']!=2 and abs(e['x']-x)<55 and self.p.memory[SYMS['_enemy_alive'][1]+i] for i,e in enumerate(r['enemies']))
   if near and self.read('dash_charge'):buttons+=['b']
   self.tick(1,buttons)
   if self.read('deaths',2)!=death:raise AssertionError(('goal approach died',self.state()))
  self.tick(15)
  assert self.read('game_mode')==3,self.state();self.clear_frames=self.read('stage_frames',2);self.shot('stage-'+str(r['id']+1)+'-clear');self.tap('a',120)
  if self.read('game_mode')==5:self.tap('a',90)
 def close(self):self.ram.seek(0);self.p.stop(ram_file=self.ram);self.ram.seek(0)
def run():
 t=Tester();t.start();results=[]
 for r in ROUTES:
  assert t.read('stage_id')==r['id'];print('STAGE',r['id'],r['name'],flush=True)
  if r['id']%3==0:t.shot('world-'+str(r['biome']+1))
  main=r['main_route'];branches={b['entry_main_platform']:b for b in r['seal_routes']};skip_to=-1
  for idx in main:
   if idx<skip_to:continue
   if t.current_platform()!=idx and not (r['platforms'][idx]['kind']==3 and t.p.memory[SYMS['_crumble'][1]+idx]>=40):t.jump(idx)
   if idx in branches:
    b=branches[idx]
    for j,bi in enumerate(b['platform_indices']):
     if r['platforms'][bi]['kind']==3 and t.p.memory[SYMS['_crumble'][1]+bi]>=40:continue
     t.jump(bi,collect=b['seal_pickup_index'] if j==len(b['platform_indices'])-1 else None)
    t.jump(b['rejoin_main_platform']);skip_to=b['rejoin_main_platform']
  if r['boss']:t.boss()
  assert t.read('seal_count')==3,('missing seal',r['id'],t.state())
  deaths=t.read('deaths',2);t.finish()
  results.append({'id':r['id'],'name':r['name'],'seals':3,'frames':t.clear_frames,'par_seconds':r['par_seconds'],'deaths':deaths});(ROOT/'build/progress.json').write_text(json.dumps(results,indent=2))
 assert t.read('game_mode')==6 and t.read('completed');t.shot('ending');trace=[]
 for n,b in t.trace:
  if trace and trace[-1][1]==b:trace[-1][0]+=n
  else:trace.append([n,b])
 h=hashlib.sha256(ROM.read_bytes()).hexdigest();artifact={'rom_sha256':h,'frames':t.frames,'inputs':trace};(ROOT/'dist/verified-inputs.json').write_text(json.dumps(artifact,separators=(',',':'))+'\n')
 t.close();(ROOT/'build/completed-test.sav').write_bytes(t.ram.getvalue()[:8192]);again=Tester(t.ram);again.tick(180);assert again.read('completed') and again.read('unlocked')==11 and all(again.p.memory[SYMS['_seal_bits'][1]+i]==7 for i in range(12));again.close()
 # This second fresh emulator replays buttons without loading states or planning.
 linear=Tester()
 for n,b in trace:linear.tick(n,b)
 assert linear.read('completed') and linear.read('game_mode')==6 and all(linear.p.memory[SYMS['_seal_bits'][1]+i]==7 for i in range(12)),linear.state();linear.shot('linear-ending');linear.close();(ROOT/'build/linear-earned.sav').write_bytes(linear.ram.getvalue()[:8192])
 report={'rom_sha256':h,'input_only':True,'linear_replay_passed':True,'all_12_stages_completed':True,'all_36_seals_collected':True,'saved_completion_restored':True,'frames':artifact['frames'],'stages':results}
 (ROOT/'dist/playtest-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':run()
