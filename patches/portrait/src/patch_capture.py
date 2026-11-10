from pathlib import Path
import shutil,re,subprocess
root=Path('/home/user/oh')
p=root/'foundation/graphic/graphic_2d/rosen/modules/render_service/core/feature/capture/rs_surface_capture_task.cpp'
backup=p.with_suffix('.cpp.before_portrait')
if not backup.exists():shutil.copy2(p,backup)
s=backup.read_bytes().decode();newline='\r\n' if '\r\n' in s else '\n';s=s.replace('\r\n','\n')
a='''void RSSurfaceCaptureVisitor::ProcessLogicalDisplayRenderNode(RSLogicalDisplayRenderNode& node)
{
    ProcessChildren(node);
}'''
b='''void RSSurfaceCaptureVisitor::ProcessLogicalDisplayRenderNode(RSLogicalDisplayRenderNode& node)
{
    if (canvas_ == nullptr) {
        return;
    }
    Drawing::AutoCanvasRestore restore(*canvas_.get(), true);
    // Surface matrices include the logical-display transform in divided
    // rendering. Display snapshots are requested in logical coordinates.
    auto& geometry = node.GetRenderProperties().GetBoundsGeometry();
    if (geometry != nullptr) {
        geometry->UpdateByMatrixFromSelf();
        Drawing::Matrix inverse;
        if (geometry->GetMatrix().Invert(inverse)) {
            canvas_->ConcatMatrix(inverse);
        }
    }
    ProcessChildren(node);
}'''
assert s.count(a)==1
p.write_bytes(s.replace(a,b).replace('\n',newline).encode())
out=root/'out/opi5plus'
t=(out/'obj/foundation/graphic/graphic_2d/rosen/modules/render_service/librender_service.ninja').read_text()
blocks=re.split(r'(?=^build )',t,flags=re.M)
selected=[v for v in blocks[1:] if 'rs_render_service_visitor.o:' in v.split('\n')[0] or 'rs_surface_capture_task.o:' in v.split('\n')[0] or ': solink ' in v.split('\n')[0]]
assert len(selected)==3
rules=(out/'toolchain.ninja').read_text()
header='ninja_required_version = 1.7.2\nroot_out_dir = .\npool build_toolchain_link_pool\n  depth = 1\n'
for name in ['cxx','solink']:
 m=re.search(r'^rule '+name+r'\n(?:[ \t].*\n)*',rules,re.M);assert m
 header+=m.group().replace('/usr/bin/env "../../build/toolchain/gcc_solink_wrapper.py"','/usr/bin/python3 "../../build/toolchain/gcc_solink_wrapper.py"')+'\n'
content=header+blocks[0]+'\n'+''.join(re.sub(r' \|\|[^\n]*','',v) for v in selected)
content=content.replace('--thinlto-jobs=16','--thinlto-jobs=4')
(out/'portrait-render-only.ninja').write_text(content)
log=open('/tmp/portrait-capture-build.log','w')
p=subprocess.Popen([str(root/'prebuilts/build-tools/linux-x86/bin/ninja'),'-C',str(out),'-f','portrait-render-only.ninja',selected[-1].split()[1].rstrip(':'),'-j2'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print('capture build PID',p.pid)
