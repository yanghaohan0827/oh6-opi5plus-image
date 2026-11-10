from pathlib import Path
import shutil,re,subprocess
root=Path('/home/user/oh')
p=root/'foundation/window/window_manager/wmserver/src/input_window_monitor.cpp'
backup=p.with_suffix('.cpp.before_portrait')
if not backup.exists():shutil.copy2(p,backup)
s=backup.read_bytes().decode();newline='\r\n' if '\r\n' in s else '\n';s=s.replace('\r\n','\n')
s=s.replace('#include <ipc_skeleton.h>','#include <ipc_skeleton.h>\n#include <parameters.h>')
s=s.replace('''        if (displayInfo->GetRotation() == Rotation::ROTATION_90 ||
            displayInfo->GetRotation() == Rotation::ROTATION_270) {''','''        // Opt-in for external screens whose display-node transform already
        // maps logical pointer coordinates into the physical HDMI output.
        const bool logicalPointer = system::GetBoolParameter("persist.window.logical_pointer", false);
        if (!logicalPointer && (displayInfo->GetRotation() == Rotation::ROTATION_90 ||
            displayInfo->GetRotation() == Rotation::ROTATION_270)) {''')
s=s.replace('.direction = GetDisplayDirectionForMmi(displayInfo->GetRotation()),','.direction = logicalPointer ? MMI::DIRECTION0 : GetDisplayDirectionForMmi(displayInfo->GetRotation()),')
s=s.replace('.displayDirection = GetDisplayDirectionForMmi(displayInfo->GetRotation()),','.displayDirection = logicalPointer ? MMI::DIRECTION0 : GetDisplayDirectionForMmi(displayInfo->GetRotation()),')
assert s.count('const bool logicalPointer')==1
p.write_bytes(s.replace('\n',newline).encode())
out=root/'out/opi5plus'
t=(out/'obj/foundation/window/window_manager/wmserver/libwms.ninja').read_text()
blocks=re.split(r'(?=^build )',t,flags=re.M)
selected=[v for v in blocks[1:] if 'input_window_monitor.o:' in v.split('\n')[0] or ': solink ' in v.split('\n')[0]]
assert len(selected)==2
rules=(out/'toolchain.ninja').read_text()
header='ninja_required_version = 1.7.2\nroot_out_dir = .\npool build_toolchain_link_pool\n  depth = 1\n'
for name in ['cxx','solink']:
 m=re.search(r'^rule '+name+r'\n(?:[ \t].*\n)*',rules,re.M);assert m
 header+=m.group().replace('/usr/bin/env "../../build/toolchain/gcc_solink_wrapper.py"','/usr/bin/python3 "../../build/toolchain/gcc_solink_wrapper.py"')+'\n'
content=header+blocks[0]+'\n'+''.join(re.sub(r' \|\|[^\n]*','',v) for v in selected)
content=content.replace('--thinlto-jobs=16','--thinlto-jobs=4')
(out/'portrait-input-only.ninja').write_text(content)
log=open('/tmp/portrait-input-build.log','w')
p=subprocess.Popen([str(root/'prebuilts/build-tools/linux-x86/bin/ninja'),'-C',str(out),'-f','portrait-input-only.ninja',selected[-1].split()[1].rstrip(':'),'-j2'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print('input monitor build PID',p.pid)
