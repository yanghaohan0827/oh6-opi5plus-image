from pathlib import Path
import re,subprocess
root=Path('/home/user/oh')
out=root/'out/opi5plus'
t=(out/'obj/foundation/window/window_manager/dmserver/libdms.ninja').read_text()
blocks=re.split(r'(?=^build )',t,flags=re.M)
selected=[v for v in blocks[1:] if 'abstract_screen_controller.o:' in v.split('\n')[0] or ': solink ' in v.split('\n')[0]]
assert len(selected)==2
rules=(out/'toolchain.ninja').read_text()
header='ninja_required_version = 1.7.2\nroot_out_dir = .\npool build_toolchain_link_pool\n  depth = 1\n'
for name in ['cxx','solink']:
 m=re.search(r'^rule '+name+r'\n(?:[ \t].*\n)*',rules,re.M)
 assert m
 header+=m.group().replace('/usr/bin/env \"../../build/toolchain/gcc_solink_wrapper.py\"', '/usr/bin/python3 \"../../build/toolchain/gcc_solink_wrapper.py\"')+'\n'
content=header+blocks[0]+'\n'+''.join(re.sub(r' \|\|[^\n]*','',v) for v in selected)
(out/'portrait-only.ninja').write_text(content)
log=open('/tmp/portrait-build.log','w')
p=subprocess.Popen([str(root/'prebuilts/build-tools/linux-x86/bin/ninja'),'-C',str(out),'-f','portrait-only.ninja','window/window_manager/libdms.z.so','-j2'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print('portrait component build PID',p.pid)
