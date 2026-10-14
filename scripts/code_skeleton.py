#!/usr/bin/env python3
"""
code_skeleton.py
基于 AST 与结构化特征的代码骨架提取器（Python / JS / TS / Go / Java / Rust）。
提取类、方法签名、类型注解与行号范围，将函数体折叠为省略号，实现 85%~95% Token 压缩。
"""

from __future__ import annotations

import ast
import os
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any


class CodeSkeletonExtractor:
    def __init__(self, max_line_len: int = 120):
        self.max_line_len = max_line_len

    def extract_file(self, file_path: Path) -> Dict[str, Any]:
        """提取单个文件的骨架信息"""
        if not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = file_path.suffix.lower()
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        total_lines = len(content.splitlines())

        if ext == ".py":
            skeleton_text, symbols_count = self._extract_python_ast(content)
        elif ext in (".ts", ".js", ".tsx", ".jsx"):
            skeleton_text, symbols_count = self._extract_c_like_signatures(content, "ts")
        elif ext in (".go", ".rs", ".java", ".cpp", ".c", ".h"):
            skeleton_text, symbols_count = self._extract_c_like_signatures(content, ext.lstrip("."))
        else:
            # 默认行首符号扫描
            skeleton_text, symbols_count = self._extract_generic_signatures(content)

        skeleton_lines = len(skeleton_text.splitlines())
        compression = (
            (1.0 - (skeleton_lines / max(total_lines, 1))) * 100.0 if total_lines > 0 else 0.0
        )

        return {
            "path": str(file_path),
            "total_lines": total_lines,
            "skeleton_lines": skeleton_lines,
            "symbols_count": symbols_count,
            "compression_ratio": f"{compression:.1f}%",
            "skeleton": skeleton_text,
        }

    def _extract_python_ast(self, content: str) -> tuple[str, int]:
        """使用标准库 ast 进行高保真提取"""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return self._extract_generic_signatures(content)

        lines: List[str] = []
        symbols_count = 0

        # 模块 Docstring
        mod_doc = ast.get_docstring(tree)
        if mod_doc:
            doc_first_line = mod_doc.strip().splitlines()[0]
            lines.append(f'"""{doc_first_line}"""\n')

        def format_args(args: ast.arguments) -> str:
            arg_strs = []
            for a in args.args:
                anno = f": {ast.unparse(a.annotation)}" if a.annotation else ""
                arg_strs.append(f"{a.arg}{anno}")
            if args.vararg:
                anno = f": {ast.unparse(args.vararg.annotation)}" if args.vararg.annotation else ""
                arg_strs.append(f"*{args.vararg.arg}{anno}")
            if args.kwarg:
                anno = f": {ast.unparse(args.kwarg.annotation)}" if args.kwarg.annotation else ""
                arg_strs.append(f"**{args.kwarg.arg}{anno}")
            return ", ".join(arg_strs)

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                symbols_count += 1
                bases_str = f"({', '.join(ast.unparse(b) for b in node.bases)})" if node.bases else ""
                end_lineno = getattr(node, "end_lineno", node.lineno)
                lines.append(f"[L{node.lineno}-L{end_lineno}] class {node.name}{bases_str}:")
                
                doc = ast.get_docstring(node)
                if doc:
                    lines.append(f'    """{doc.strip().splitlines()[0]}"""')

                # 类内方法与属性
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        symbols_count += 1
                        prefix = "async def " if isinstance(item, ast.AsyncFunctionDef) else "def "
                        ret = f" -> {ast.unparse(item.returns)}" if item.returns else ""
                        fn_end = getattr(item, "end_lineno", item.lineno)
                        arg_str = format_args(item.args)
                        lines.append(f"    [L{item.lineno}-L{fn_end}] {prefix}{item.name}({arg_str}){ret}: ...")
                    elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        lines.append(f"    [L{item.lineno}] {item.target.id}: {ast.unparse(item.annotation)}")

                lines.append("")

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols_count += 1
                prefix = "async def " if isinstance(node, ast.AsyncFunctionDef) else "def "
                ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
                end_lineno = getattr(node, "end_lineno", node.lineno)
                arg_str = format_args(node.args)
                lines.append(f"[L{node.lineno}-L{end_lineno}] {prefix}{node.name}({arg_str}){ret}: ...")

            elif isinstance(node, ast.Assign):
                # 提取全局常量或顶级声明
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        lines.append(f"[L{node.lineno}] {target.id} = ...")

        return "\n".join(lines).strip(), symbols_count

    def _extract_c_like_signatures(self, content: str, lang: str) -> tuple[str, int]:
        """针对 TS/JS/Go/Java/Rust 使用启发式正则提取"""
        lines = content.splitlines()
        skeleton_lines = []
        symbols_count = 0

        # 正则特征：类、接口、函数、方法、结构体
        patterns = [
            # export / class / interface / type (TS/JS)
            re.compile(r"^\s*(export\s+)?(class|interface|type|enum)\s+([A-Za-z0-9_]+)"),
            # function / async function / const func = (TS/JS)
            re.compile(r"^\s*(export\s+)?(async\s+)?function\s+([A-Za-z0-9_]+)\s*\("),
            re.compile(r"^\s*(export\s+)?const\s+([A-Za-z0-9_]+)\s*=\s*(async\s*)?\("),
            # Go: func / type Struct
            re.compile(r"^\s*func\s+(\([^\)]+\)\s+)?([A-Za-z0-9_]+)\s*\("),
            re.compile(r"^\s*type\s+([A-Za-z0-9_]+)\s+(struct|interface)"),
            # Rust: pub fn / pub struct / impl
            re.compile(r"^\s*(pub\s+)?(fn|struct|enum|trait|impl)\s+([A-Za-z0-9_]+)"),
            # Java: public/protected/private void/Type methodName(...)
            re.compile(r"^\s*(public|protected|private)?\s*(static\s+)?([A-Za-z0-9_<>]+\s+)+([A-Za-z0-9_]+)\s*\("),
        ]

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith(("//", "/*", "*", "#")):
                continue

            for pat in patterns:
                if pat.search(line):
                    symbols_count += 1
                    # 截取签名行
                    clean_sig = re.sub(r"\{.*$", "{ ... }", stripped)
                    if not clean_sig.endswith(("{ ... }", ";", ":")):
                        clean_sig += " { ... }"
                    skeleton_lines.append(f"[L{i}] {clean_sig}")
                    break

        return "\n".join(skeleton_lines), symbols_count

    def _extract_generic_signatures(self, content: str) -> tuple[str, int]:
        lines = content.splitlines()
        res = []
        symbols = 0
        for i, line in enumerate(lines, start=1):
            if re.match(r"^[A-Za-z_#]", line) and len(line.strip()) > 3:
                symbols += 1
                res.append(f"[L{i}] {line.strip()[:100]}")
        return "\n".join(res), symbols

    def scan_directory(
        self,
        dir_path: Path,
        extensions: Optional[List[str]] = None,
        max_depth: int = 3,
    ) -> List[Dict[str, Any]]:
        """递归扫描目录并提取骨架清单"""
        if not extensions:
            extensions = [".py", ".ts", ".js", ".go", ".rs", ".java"]

        results = []
        dir_path = dir_path.resolve()

        for root, dirs, files in os.walk(dir_path):
            # 过滤隐藏目录和构建目录
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ("node_modules", "vendor", "output", "__pycache__", "dist", "build")
            ]
            rel_depth = len(Path(root).relative_to(dir_path).parts)
            if rel_depth > max_depth:
                continue

            for f in sorted(files):
                f_path = Path(root) / f
                if f_path.suffix.lower() in extensions:
                    try:
                        res = self.extract_file(f_path)
                        results.append(res)
                    except Exception as e:
                        pass

        return results


def main():
    parser = argparse.ArgumentParser(description="AST & Signature Code Skeleton Extractor")
    parser.add_argument("--path", required=True, help="File or directory path to extract skeleton from")
    parser.add_argument("--format", default="text", choices=["text", "md", "json"], help="Output format")
    parser.add_argument("--depth", type=int, default=3, help="Max recursion depth for directories")
    args = parser.parse_args()

    extractor = CodeSkeletonExtractor()
    target = Path(args.path).resolve()

    if target.is_file():
        data = extractor.extract_file(target)
        if args.format == "json":
            import json
            print(json.dumps(data, indent=2, ensure_ascii=False))
        elif args.format == "md":
            print(f"### 📄 骨架投影：`{target.name}` (行数: {data['total_lines']} ➔ {data['skeleton_lines']} | 压缩率: {data['compression_ratio']})\n")
            print("```text\n" + data["skeleton"] + "\n```")
        else:
            print(f"[*] Skeleton for: {target} ({data['total_lines']}L -> {data['skeleton_lines']}L, saved {data['compression_ratio']})")
            print("-" * 60)
            print(data["skeleton"])

    elif target.is_dir():
        results = extractor.scan_directory(target, max_depth=args.depth)
        total_orig = sum(r["total_lines"] for r in results)
        total_skel = sum(r["skeleton_lines"] for r in results)
        total_comp = (1.0 - (total_skel / max(total_orig, 1))) * 100.0 if total_orig > 0 else 0.0

        if args.format == "json":
            import json
            print(json.dumps({"summary": {"files": len(results), "original_lines": total_orig, "skeleton_lines": total_skel, "compression": f"{total_comp:.1f}%"}, "files": results}, indent=2, ensure_ascii=False))
        else:
            print(f"[*] Repository Skeleton Summary: {len(results)} files, {total_orig} lines -> {total_skel} lines (Saved {total_comp:.1f}% tokens)")
            print("=" * 70)
            for r in results:
                rel_path = os.path.relpath(r["path"], str(target))
                print(f"\n[File: {rel_path}] ({r['total_lines']}L -> {r['skeleton_lines']}L, -{r['compression_ratio']})")
                print("-" * 50)
                print(r["skeleton"])


if __name__ == "__main__":
    main()
