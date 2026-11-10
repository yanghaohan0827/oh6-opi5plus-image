import os,subprocess,shutil
from pathlib import Path
root=Path('/home/user/oh'); src=root/'out/opi5plus/kernel/src_tmp/linux-6.6'; out=root/'out/opi5plus/kernel/OBJ/linux-6.6'
for config in [out/'.config',src/'arch/arm64/configs/orangepi5plus_oh_defconfig',root/'device/board/opc/opi5plus/kernel/configs/orangepi5plus_oh_defconfig']:
 backup=config.with_name(config.name+'.before_browser')
 if not backup.exists():shutil.copy2(config,backup)
 subprocess.run([str(src/'scripts/config'),'--file',str(config),'--enable','PID_NS'],check=True)
env=os.environ.copy();env.update(ROOT_DIR=str(root),KBUILD_OUTPUT=str(out),INSTALL_MOD_PATH=str(root/'out/opi5plus/driver_modules'),PRODUCT_PATH='vendor/opc/opi5plus',DEVICE_NAME='opi5plus',PRODUCT_COMPANY='opc')
env['PATH']=str(root/'prebuilts/clang/ohos/linux-x86_64/llvm/bin')+':'+str(root/'prebuilts/gcc/linux-x86/aarch64/gcc-linaro-7.5.0-2019.12-x86_64_aarch64-linux-gnu/bin')+':'+str(root/'prebuilts/develop_tools/pahole/bin')+':'+env['PATH']
script=Path('/tmp/build_browser_kernel.sh');script.write_text('''#!/bin/bash
set -e
cd /home/user/oh/out/opi5plus/kernel/src_tmp/linux-6.6
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- LLVM=1 LLVM_IAS=1 olddefconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- LLVM=1 LLVM_IAS=1 Image modules -j6
echo BROWSER_KERNEL_BUILD_SUCCESS
''')
p=subprocess.Popen(['/bin/bash',str(script)],env=env,stdout=open('/tmp/browser-kernel-build.log','w'),stderr=subprocess.STDOUT,start_new_session=True)
print('kernel build PID',p.pid)
