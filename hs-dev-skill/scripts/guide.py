"""Deterministic human navigation derived only from the reviewed 0.0.2 catalog."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_catalog(data):
    if data.get('version') != '0.0.2':
        raise ValueError('Catalog version must be 0.0.2')
    activities = [a for s in data['stages'] for a in s['activities']]
    lookup = {a['id']: a for a in activities}
    if len(lookup) != len(activities):
        raise ValueError('Duplicate activity ID')
    output_ids = set()
    for activity in activities:
        deps = activity.get('depends_on')
        if not isinstance(deps, list) or len(deps) != len(set(deps)) or any(d not in lookup for d in deps):
            raise ValueError('Unknown or duplicate dependency: ' + activity['id'])
        for output in activity['outputs']:
            if output['id'] in output_ids or not output['id'].startswith(activity['id'] + '.O'):
                raise ValueError('Invalid or duplicate output ID: ' + output['id'])
            output_ids.add(output['id'])
    visited, active = set(), set()
    def visit(aid):
        if aid in active:
            raise ValueError('Dependency cycle at ' + aid)
        if aid in visited:
            return
        active.add(aid)
        for dep in lookup[aid]['depends_on']:
            visit(dep)
        active.remove(aid)
        visited.add(aid)
    for aid in lookup:
        visit(aid)


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def render(data):
    validate_catalog(data)
    lines = ['# 阶段、活动与成果导航', '',
             '由 `scripts/guide.py` 从 [catalog.json](catalog.json) 确定性生成；只修改catalog后重新生成，不在本表维护第二份规则。', '',
             '依赖是当前输入可能对应的生产活动，不意味着全部重做。先核对本次实际消费事实，复用有效来源，只补必要缺口。', '',
             '输出的问题、证据和通过标准以catalog为准。只读所选活动和当前输出，不预先加载整阶段正文。', '',
             '| 阶段 | 活动 | 目标 | 输入 | 输出与层 | 候选依赖 |',
             '|---|---|---|---|---|---|']
    for stage in data['stages']:
        for activity in stage['activities']:
            outputs = '；'.join(o['id'] + ' ' + o['title'] + ' [' + o['layer'] + ']' for o in activity['outputs'])
            row = [stage['id'] + ' ' + stage['title'], activity['id'] + ' ' + activity['title'],
                   activity['goal'], '；'.join(activity['inputs']), outputs,
                   '、'.join(activity['depends_on']) or '按实际对象独立触发']
            lines.append('| ' + ' | '.join(cell(x) for x in row) + ' |')
    lines += ['', '## 按阶段审查', '', '阶段审查引用适用活动成果，不重复全文，也不把未执行活动自动记通过。', '']
    lines += [f'- [{s["id"]} {s["title"]}](templates/stage-{s["id"].lower()}-review.md) · `{s["skill"]}` · {s["questioning"]}' for s in data['stages']]
    lines += ['', '## 三层填写入口', '',
              '- [project：当前应然与实然](templates/project.md)',
              '- [delivery：真实沟通、取舍与反例](templates/delivery.md)',
              '- [execution：工具状态、实际证据与续做](templates/execution.md)', '']
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if the generated navigation is stale')
    args = parser.parse_args(argv)
    data = json.loads((ROOT / 'references/catalog.json').read_text(encoding='utf-8'))
    expected = render(data)
    file = ROOT / 'references/activities.md'
    if args.check:
        if not file.is_file() or file.read_text(encoding='utf-8') != expected:
            parser.exit(1, 'activities.md differs from catalog; run scripts/guide.py\n')
    else:
        file.write_text(expected, encoding='utf-8')
    print('Activity navigation matches catalog' if args.check else 'Generated references/activities.md')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
