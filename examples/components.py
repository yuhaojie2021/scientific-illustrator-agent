"""Diagnose Illustrator or render/update a component scene. No implicit saving."""
import argparse
import json
import sys
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from illustrator.com_client import IllustratorClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    doctor = sub.add_parser('doctor')
    doctor.add_argument('--connect', action='store_true', help='May launch Illustrator')
    doctor.add_argument('--remember', action='store_true', help='Record interpreter after all checks pass')
    sub.add_parser('inspect')
    render = sub.add_parser('render')
    render.add_argument('spec', type=Path)
    render.add_argument('--target', choices=['new', 'active'], default='new')
    render.add_argument('--expected-document')
    render.add_argument('--validate-only', action='store_true')
    render.add_argument('--preview', type=Path, help='Fresh PNG path; exports artwork bounds')
    render.add_argument('--report', type=Path, help='Fresh JSON report path')
    args = parser.parse_args()
    if args.command == 'doctor':
        try:
            from packaging.requirements import Requirement
        except ImportError:
            from pip._vendor.packaging.requirements import Requirement
        result = dict(python=sys.version, executable=sys.executable, dependencies={}, ready=True)
        for line in (ROOT / 'requirements.txt').read_text().splitlines():
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            req = Requirement(line)
            if req.marker and not req.marker.evaluate():
                continue
            try:
                version = metadata.version(req.name)
                ok = req.specifier.contains(version)
                result['dependencies'][req.name] = dict(version=version, compatible=ok)
                result['ready'] &= ok
            except metadata.PackageNotFoundError:
                result['dependencies'][req.name] = dict(error='missing')
                result['ready'] = False
        result['ready'] &= sys.version_info >= (3, 9)
        if result['ready']:
            try:
                import pythoncom, win32com.client, pydantic, PIL
            except ImportError as exc:
                result.update(ready=False, import_error=str(exc))
        if args.connect:
            try:
                with IllustratorClient() as client:
                    result['illustrator'] = client.health_check()
            except Exception as exc:
                result.update(ready=False, connection_error=str(exc))
        if args.remember:
            if not args.connect:
                raise ValueError('--remember requires --connect')
            if result['ready']:
                (ROOT / 'runtime.local.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0 if result['ready'] else 1
    if args.command == 'inspect':
        with IllustratorClient() as client:
            serializer = (ROOT / 'src/illustrator/jsx/serialize.jsx').read_text(encoding='utf-8')
            print(client.execute_jsx(serializer + '\nsciJSON((function(){if(!app.documents.length)throw new Error("No open document");var d=app.activeDocument;return {name:d.name,artboard:d.artboards[d.artboards.getActiveArtboardIndex()].artboardRect,objects:d.pageItems.length};})());', owned_document=False))
        return 0
    from models.component_spec import ComponentScene, expected_counts
    from renderer.component_renderer import render_components
    scene = ComponentScene.parse_raw(args.spec.read_text(encoding='utf-8-sig'))
    if args.validate_only:
        print(json.dumps(dict(valid=True, counts=expected_counts(scene))))
        return 0
    for output in [args.preview, args.report]:
        if output:
            if output.exists():
                raise FileExistsError('Refusing to overwrite: ' + str(output))
            output.parent.mkdir(parents=True, exist_ok=True)
    result = render_components(scene, args.target, args.expected_document)
    if args.preview:
        # A temporary artboard crops the preview without changing existing artboards.
        # Recheck document identity so export cannot silently target another document.
        script = r'''(function(){var d=app.activeDocument;if(d.name!==DOC)throw new Error('Active document changed before export');var g=d.layers.getByName(LAYER),b=g.groupItems[0].visibleBounds,index=d.artboards.getActiveArtboardIndex(),temp=null;try{temp=d.artboards.add([b[0]-12,b[1]+12,b[2]+12,b[3]-12]);d.artboards.setActiveArtboardIndex(d.artboards.length-1);var o=new ExportOptionsPNG24();o.antiAliasing=true;o.transparency=false;o.artBoardClipping=true;o.horizontalScale=200;o.verticalScale=200;d.exportFile(new File(OUTPUT),ExportType.PNG24,o);return 'exported';}finally{if(temp)temp.remove();d.artboards.setActiveArtboardIndex(index);}})();'''
        script = script.replace('DOC', json.dumps(result['document'])).replace('LAYER', json.dumps(result['layer'])).replace('OUTPUT', json.dumps(str(args.preview.resolve())))
        with IllustratorClient() as client:
            client.execute_jsx(script, owned_document=False)
        result['preview'] = str(args.preview.resolve())
    if args.report:
        args.report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

