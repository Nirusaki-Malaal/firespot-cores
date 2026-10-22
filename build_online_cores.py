#!/usr/bin/env python3
"""Build the pinned downloadable cores, keeping each upstream's source and license."""
import argparse,subprocess,os,shutil
from pathlib import Path
CORES={
 'fceumm':('https://github.com/libretro/libretro-fceumm','ac0d00a7fc01166f84c7bac01d1084ebfd2b865e','Copying','libretro_fceumm.so'),
 'mgba':('https://github.com/libretro/mgba','7a12d6d4b9acb14c0ae62c9166b6a2f3d08007f6','LICENSE','libretro_mgba.so'),
 'pcsx':('https://github.com/libretro/pcsx_rearmed','c8816799b50388e61cfe237fe2cdbb7d8175f20a','COPYING','libretro_pcsx_rearmed.so'),
}
ABIS=['armeabi-v7a','arm64-v8a','x86_64']
def run(args,**kwargs):subprocess.run(list(map(str,args)),check=True,**kwargs)
def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,default=Path('.tooling/online-cores'));p.add_argument('--out',type=Path,default=Path('artifacts/online-cores'));p.add_argument('--package-only',action='store_true',help='Package already-built output in the work directory');a=p.parse_args()
 ndk=Path(os.environ.get('ANDROID_NDK_HOME','/missing-ndk'));a.work.mkdir(parents=True,exist_ok=True);a.out.mkdir(parents=True,exist_ok=True)
 for name,(url,pin,license,file) in CORES.items():
  src=a.work/name
  if not a.package_only:
   if not (src/'.git').exists():run(['git','clone','--no-checkout',url,src])
   run(['git','-C',src,'fetch','--depth','1','origin',pin]);run(['git','-C',src,'checkout','--detach',pin])
   if name!='mgba':run([ndk/'ndk-build','-C',src/'jni','APP_ABI='+' '.join(ABIS),'APP_PLATFORM=android-28',f'NDK_OUT={a.work.resolve()}/{name}-obj',f'NDK_LIBS_OUT={a.work.resolve()}/{name}-libs','-j2'])
   else:
    for abi in ABIS:
     build=a.work/f'mgba-build-{abi}'
     args=['cmake','-S',src,'-B',build,f'-DCMAKE_TOOLCHAIN_FILE={ndk}/build/cmake/android.toolchain.cmake',f'-DANDROID_ABI={abi}','-DANDROID_PLATFORM=android-28','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_POLICY_VERSION_MINIMUM=3.5','-DBUILD_LIBRETRO=ON']
     args += [f'-D{option}=OFF' for option in ['BUILD_QT','BUILD_SDL','BUILD_SHARED','BUILD_STATIC','USE_FFMPEG','USE_LIBZIP','USE_PNG','USE_ZLIB','USE_MINIZIP','USE_SQLITE3','USE_ELF','USE_LUA','USE_LZMA','USE_DISCORD_RPC','USE_JSON_C','USE_FREETYPE','BUILD_TEST','BUILD_SUITE','BUILD_PERF']]
     run(args);run(['cmake','--build',build,'--target','mgba_libretro','-j2'])
  actual=subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip();assert actual==pin,(name,actual)
  dest=a.out/name;dest.mkdir(exist_ok=True)
  for abi in ABIS:
   path=(a.work/f'mgba-build-{abi}'/'mgba_libretro.so') if name=='mgba' else (a.work/f'{name}-libs'/abi/'libretro.so')
   (dest/abi).mkdir(exist_ok=True);shutil.copy2(path,dest/abi/file)
  shutil.copy2(src/license,dest/'LICENSE.txt')
  with (dest/f'{name}-source.tar.gz').open('wb') as f:run(['git','-C',src,'archive','--format=tar.gz',f'--prefix={name}/',pin],stdout=f)
 print('Packaged pinned core binaries with matching source and licenses.')
if __name__=='__main__':main()
