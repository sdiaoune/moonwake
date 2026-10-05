from pathlib import Path
import sys,json,hashlib
p=Path(sys.argv[1]);d=p.read_bytes()
assert len(d)<=2097152
assert d[0x143]==0xC0 and d[0x147]==0x1B and d[0x149]==2
assert len(d)==32768<<d[0x148]
c=0
for b in d[0x134:0x14d]:c=(c-b-1)&255
assert c==d[0x14d]
assert (sum(d)-d[0x14e]-d[0x14f])&65535==int.from_bytes(d[0x14e:0x150],'big')
r=dict(title='MOONWAKE',bytes=len(d),sha256=hashlib.sha256(d).hexdigest(),cgb_only=True,mapper='MBC5 + RAM + battery',sram_bytes=8192,checksums_valid=True)
p.with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
