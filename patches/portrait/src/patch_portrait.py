from pathlib import Path
import shutil
p=Path('/home/user/oh/foundation/window/window_manager/dmserver/src/abstract_screen_controller.cpp')
backup=p.with_suffix('.cpp.before_portrait')
if not backup.exists(): shutil.copy2(p,backup)
s=backup.read_text()
a='absScreen->rsDisplayNode_->SetRotation(-90.0f * static_cast<uint32_t>(rotationAfter));'
b='displayNode->SetRotation(-90.f * static_cast<uint32_t>(rotationAfter));'
assert s.count(a)==1 and s.count(b)==1
s=s.replace(a,a+'\n            absScreen->rsDisplayNode_->SetScreenRotation(static_cast<uint32_t>(rotationAfter));')
s=s.replace(b,b+'\n    displayNode->SetScreenRotation(static_cast<uint32_t>(rotationAfter));')
p.write_text(s)
print('Added explicit RS screen rotation at startup and orientation changes')
