#!/usr/bin/env python3
"""Bounded JSON command interface for the 0.0.2 development cycle."""
import argparse
import json
from pathlib import Path
import sys
from hsdev import __version__, knowledge, templates
from hsdev.presentation import compact_result


def value(text):
    if text is None:
        return None
    return json.loads(Path(text[1:]).read_text()) if text.startswith('@') else json.loads(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--root', default='.')
    parser.add_argument('--compact', action='store_true', help='Summarize control responses without changing stored evidence')
    parser.add_argument('command', choices=['init','status','start','source-add','source-get','evidence-read','question','question-resolve','answer','reflect','readiness','assess','plan','authorize','lock','apply','produce','record-output','run','submit','rollback','resume','unlock','advance','reindex','locate','read','template','catalog-check'])
    parser.add_argument('delivery', nargs='?')
    parser.add_argument('question_id', nargs='?')
    parser.add_argument('--blocking', choices=['true','false'])
    parser.add_argument('--affected-work')
    parser.add_argument('--nonblocking-reason')
    for key in ['title','activity','scope','record','id','question','reason','options','recommendation','source','understanding','scenario','outcome','plan-digest','changes','checks','query','path','digest','output']:
        parser.add_argument('--'+key)
    for key, default in [('start',1),('end',None),('limit',5),('max-bytes',None)]:
        parser.add_argument('--'+key,type=int,default=default)
    args = vars(parser.parse_args(argv))
    compact = args.pop('compact')
    if args.get('blocking') is not None:
        args['blocking'] = args['blocking'] == 'true'
    root = Path(args.pop('root')).resolve()
    command = args.pop('command')
    try:
        for key in ['record','changes','checks','options']:
            if args.get(key) is not None:
                args[key] = value(args[key])
        if command == 'source-add': result = knowledge.register_source(root,args['record'])
        elif command == 'source-get': result = knowledge.get_source(root,args['id'],args['max_bytes'] or 12000)
        elif command == 'evidence-read': result = knowledge.read_evidence(root,args['path'],args['digest'],args['max_bytes'] or 24000)
        elif command == 'reindex': result = knowledge.reindex(root)
        elif command == 'locate': result = knowledge.locate(root,args['query'],args['limit'],args['max_bytes'] or 12000)
        elif command == 'read': result = knowledge.read_unit(root,args['path'],args['start'],args['end'],args['digest'],args['max_bytes'] or 24000)
        elif command == 'template': result = templates.contract(args['activity'],args['output'])
        elif command == 'catalog-check': result = templates.verify_catalog()
        else:
            from hsdev.engine import dispatch
            result = dispatch(root,command,{k:v for k,v in args.items() if v is not None})
        if compact:
            result = compact_result(command, result, args.get('delivery'))
        if isinstance(result,dict) and result.get('ok') is False:
            print(json.dumps({'ok':False,'result':result},ensure_ascii=False,indent=2),file=sys.stderr)
            return 2
        print(json.dumps({'ok':True,'result':result},ensure_ascii=False,indent=2))
        return 0
    except (ValueError,KeyError,TypeError,OSError,json.JSONDecodeError) as exc:
        print(json.dumps({'ok':False,'error':str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
