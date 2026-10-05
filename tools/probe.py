from playtest import Tester
x=Tester();x.start();print(x.state());f=x.read('stage_frames',2);x.tick(120,['right']);print('120frames',x.state(),'game ticks',x.read('stage_frames',2)-f);x.shot('movement-probe');x.close()
