#!/usr/bin/env python3
"""Fail packaging on a wrong ELF ABI or an accidentally bundled emulator core."""
import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path

ABIS={'armeabi-v7a':(1,40),'arm64-v8a':(2,183),'x86_64':(2,62)}
def check_elf(data,abi):
    assert data[:4]==b'\x7fELF' and data[5]==1, f'{abi}: invalid ELF encoding'
    assert (data[4],struct.unpack_from('<H',data,18)[0])==ABIS[abi], f'{abi}: wrong CPU architecture'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--apk',type=Path);parser.add_argument('--cores',type=Path);parser.add_argument('--write-manifest',action='store_true');parser.add_argument('--demo',action='store_true');args=parser.parse_args()
    result={}
    if args.apk:
        libraries=[]
        with zipfile.ZipFile(args.apk) as apk:
            assert 'classes.dex' in apk.namelist(), 'APK lacks compiled application code'
            for name in apk.namelist():
                if name.endswith('.so'):
                    allowed={'libretro_bridge.so','libretro_gambatte.so'} if args.demo else {'libretro_bridge.so'}
                    assert name.startswith('lib/') and name.rsplit('/',1)[-1] in allowed, f'Unexpected native code bundled: {name}'
                if name.startswith('lib/') and name.endswith('.so'):
                    _,abi,filename=name.split('/')
                    check_elf(apk.read(name),abi)
                    assert filename in allowed, f'Unexpected native library bundled: {name}'
                    libraries.append(name)
            assert {'lib/armeabi-v7a/libretro_bridge.so','lib/arm64-v8a/libretro_bridge.so'} <= set(libraries), 'Required bridge ABI missing'
        if args.demo:
            assert {'lib/armeabi-v7a/libretro_gambatte.so','lib/arm64-v8a/libretro_gambatte.so'} <= set(libraries), 'Demo core missing'
        result['apk']={'sha256':hashlib.sha256(args.apk.read_bytes()).hexdigest(),'bytes':args.apk.stat().st_size,'native_libraries':libraries,'emulator_cores_bundled':args.demo}
    if args.cores:
        entries=[]
        for abi in ABIS:
            path=args.cores/abi/'libretro_gambatte.so';data=path.read_bytes();check_elf(data,abi)
            entries.append({'abi':abi,'filename':str(path.relative_to(args.cores)),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
        result['core_release']={'core':'gambatte','source_url':'https://github.com/libretro/gambatte-libretro','commit':'d9d6cd06382d1ced30de34d56d3609452323dab1','ndk':'28.2.13676358','minimum_api':28,'license':'GPL-2.0','artifacts':entries,'notice':'Local integrity metadata only; not a signed online catalog.'}
        manifest_path=args.cores/'manifest.json'
        if manifest_path.exists() and not args.write_manifest:
            expected=json.loads(manifest_path.read_text())
            assert expected['artifacts']==entries, 'Core bytes differ from the recorded manifest'
        if args.write_manifest: (args.cores/'manifest.json').write_text(json.dumps(result['core_release'],indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
