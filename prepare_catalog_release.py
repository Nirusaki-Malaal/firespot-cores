#!/usr/bin/env python3
"""Stage the public release and sign its catalog with a local, unpublished key."""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_artifacts import check_elf
from generate_starter_games import game
from build_online_cores import CORES,ABIS
p=argparse.ArgumentParser();p.add_argument('--key',type=Path,required=True);p.add_argument('--out',type=Path,default=Path('artifacts/catalog-release'));a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
base='https://github.com/Nirusaki-Malaal/firespot-cores/releases/download/phase1-v1'
def artifact(path,name,abi=None):
 shutil.copy2(path,a.out/name)
 item={'file':path.name,'url':f'{base}/{name}','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
 if abi:item['abi']=abi;check_elf(path.read_bytes(),abi)
 return item
cores=[]
for id,title,consoles,license in [('gambatte','Gambatte',['gameboy'],'GPL-2.0'),('fceumm','FCEUmm',['nes'],'GPL-2.0'),('mgba','mGBA',['gba'],'MPL-2.0'),('pcsx','PCSX ReARMed',['ps1'],'GPL-2.0-or-later')]:
 if id=='gambatte':
  folder=Path('artifacts/gameboy');file='libretro_gambatte.so';url='https://github.com/libretro/gambatte-libretro';pin='d9d6cd06382d1ced30de34d56d3609452323dab1';source=folder/'gambatte-source.tar.gz';notice=folder/'COPYING'
 else:
  folder=Path('artifacts/online-cores')/id;url,pin,_,file=CORES[id];source=folder/f'{id}-source.tar.gz';notice=folder/'LICENSE.txt'
 shutil.copy2(source,a.out/f'{id}-source.tar.gz');shutil.copy2(notice,a.out/f'{id}-LICENSE.txt')
 cores.append({'id':id,'title':title,'consoleIds':consoles,'license':license,'sourceUrl':url,'sourceCommit':pin,'sourceArchiveUrl':f'{base}/{id}-source.tar.gz','licenseUrl':f'{base}/{id}-LICENSE.txt','experimental':id!='gambatte','minimumAndroidApi':28,'artifacts':[artifact(folder/abi/file,f'{id}-{abi}.so',abi) for abi in ABIS]})
# The third title is a deliberately small checkpoint variant that exercises battery RAM.
new=Path('artifacts/signal-runner.gb');new.write_bytes(game('SIGNAL RUNNER',1,battery=True))
games=[]
for id,title,source,description in [
 ('orbit-collector','Orbit Collector',Path('app/src/main/assets/starter/orbit-collector.gb'),'Collect diamond checkpoints in a small original pocket arcade game.'),
 ('pocket-courier','Pocket Courier',Path('app/src/main/assets/starter/pocket-courier.gb'),'A faster checkpoint course. D-pad moves; A or B makes a tone.'),
 ('signal-runner','Signal Runner',new,'A downloadable checkpoint variant with cartridge battery progress. Collect diamonds; your points survive starting a new session.')]:
 games.append({'id':id,'title':title,'consoleId':'gameboy','description':description,'license':'CC0-1.0','author':'FireSpot','artifact':artifact(source,source.name)})
shutil.copy2('app/src/main/assets/starter/LICENSE.txt',a.out/'games-LICENSE.txt')
shutil.copy2('scripts/generate_starter_games.py',a.out/'generate_starter_games.py')
shutil.copy2('scripts/build_online_cores.py',a.out/'build_online_cores.py')
shutil.copy2('scripts/build_gameboy.sh',a.out/'build_gameboy.sh')
catalog={'schema':1,'revision':1,'release':'phase1-v1','cores':cores,'games':games}
manifest=a.out/'catalog.json';manifest.write_text(json.dumps(catalog,indent=2)+'\n')
subprocess.run(['openssl','dgst','-sha256','-sign',str(a.key),'-out',str(a.out/'catalog.sig'),str(manifest)],check=True)
for name in ['catalog.json','catalog.sig']:shutil.copy2(a.out/name,Path('app/src/main/assets/catalog')/name)
(a.out/'SHA256SUMS').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n' for f in sorted(a.out.iterdir()) if f.is_file() and f.name!='SHA256SUMS'))
print(f'Staged {len(cores)} cores across {len(ABIS)} ABIs, three CC0 games, signed catalog, source and licenses.')
