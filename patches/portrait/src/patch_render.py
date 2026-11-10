from pathlib import Path
import shutil,re,subprocess
root=Path('/home/user/oh')
p=root/'foundation/graphic/graphic_2d/rosen/modules/render_service/core/pipeline/main_thread/rs_render_service_visitor.cpp'
backup=p.with_suffix('.cpp.before_portrait')
if not backup.exists():shutil.copy2(p,backup)
s=backup.read_bytes().decode()
a='''void RSRenderServiceVisitor::PrepareLogicalDisplayRenderNode(RSLogicalDisplayRenderNode& node)
{
    PrepareChildren(node);
}'''
b='''void RSRenderServiceVisitor::PrepareLogicalDisplayRenderNode(RSLogicalDisplayRenderNode& node)
{
    if (!canvas_) {
        PrepareChildren(node);
        return;
    }
    // Divided rendering must propagate the logical display transform to each
    // surface's destination rectangle and compositor matrix, just as it does
    // for nested surfaces. Otherwise portrait windows are clipped to the
    // physical landscape canvas before their rotation is applied.
    const auto saveCount = canvas_->SaveAllStatus();
    const auto& properties = node.GetRenderProperties();
    canvas_->MultiplyAlpha(properties.GetAlpha());
    auto& geometry = properties.GetBoundsGeometry();
    if (geometry != nullptr) {
        geometry->UpdateByMatrixFromSelf();
        canvas_->ConcatMatrix(geometry->GetMatrix());
    }
    PrepareChildren(node);
    canvas_->RestoreStatus(saveCount);
}'''
assert s.count(a)==1
p.write_bytes(s.replace(a,b).encode())
out=root/'out/opi5plus'
t=(out/'obj/foundation/graphic/graphic_2d/rosen/modules/render_service/librender_service.ninja').read_text()
blocks=re.split(r'(?=^build )',t,flags=re.M)
selected=[v for v in blocks[1:] if 'rs_render_service_visitor.o:' in v.split('\n')[0] or ': solink ' in v.split('\n')[0]]
assert len(selected)==2,[v.split('\n')[0][:160] for v in selected]
rules=(out/'toolchain.ninja').read_text()
header='ninja_required_version = 1.7.2\nroot_out_dir = .\npool build_toolchain_link_pool\n  depth = 1\n'
for name in ['cxx','solink']:
 m=re.search(r'^rule '+name+r'\n(?:[ \t].*\n)*',rules,re.M);assert m
 header+=m.group().replace('/usr/bin/env "../../build/toolchain/gcc_solink_wrapper.py"','/usr/bin/python3 "../../build/toolchain/gcc_solink_wrapper.py"')+'\n'
content=header+blocks[0]+'\n'+''.join(re.sub(r' \|\|[^\n]*','',v) for v in selected)
content=content.replace('--thinlto-jobs=16','--thinlto-jobs=4')
(out/'portrait-render-only.ninja').write_text(content)
log=open('/tmp/portrait-render-build.log','w')
p=subprocess.Popen([str(root/'prebuilts/build-tools/linux-x86/bin/ninja'),'-C',str(out),'-f','portrait-render-only.ninja',selected[-1].split()[1].rstrip(':'),'-j2'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print('render service build PID',p.pid)
