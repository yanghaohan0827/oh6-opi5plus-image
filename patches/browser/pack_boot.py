from pathlib import Path
import hashlib,shutil,subprocess,tarfile
root=Path('/home/user/oh'); out=root/'out/opi5plus/kernel/OBJ/linux-6.6';work=Path('/home/user/browser-repair');work.mkdir(exist_ok=True)
assert 'BROWSER_KERNEL_BUILD_SUCCESS' in Path('/tmp/browser-kernel-build.log').read_text()
image=work/'boot.fixed.img'; assert image.parent==work
shutil.copyfile('/home/user/browser-boot.original.img',image)
def dbg(command):
 p=subprocess.run(['debugfs','-w','-R',command,str(image)],capture_output=True,text=True);print(p.stdout,p.stderr);p.check_returncode()
kernel=out/'arch/arm64/boot/Image';assert kernel.stat().st_size>10000000
# Preserve the actual board's extlinux.conf and HDMI device tree.
dbg('rm /extlinux/Image');dbg('write '+str(kernel)+' /extlinux/Image')
check=work/'Image.verified';dbg('dump /extlinux/Image '+str(check))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(check)==sha(kernel),'Packed kernel verification failed'
modules=out/'drivers/net/wireless/realtek/rtw89'
with tarfile.open(work/'modules.fixed.tar','w') as archive:
 for name in ['rtw89_core','rtw89_pci','rtw89_8852b','rtw89_8852be']:
  p=modules/(name+'.ko');assert p.is_file();archive.add(p,arcname='modules/'+p.name)
(work/'manifest.txt').write_text('kernel_sha256='+sha(kernel)+'\nboot_sha256='+sha(image)+'\nboot_bytes='+str(image.stat().st_size)+'\n')
print((work/'manifest.txt').read_text());print('BOOT_PACKAGE_VERIFIED')
