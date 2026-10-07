"""小型通用 opt 工具。学习说明：docs/stage-01-my-opt.md。

在项目根目录运行：
    python tools/my_opt.py test/E2E/mlir/stage01/02-cse.mlir --passes cse
"""

import argparse
import sys
from pathlib import Path

from xdsl.context import Context
from xdsl.dialects import arith, builtin, func
from xdsl.parser import Parser
from xdsl.printer import Printer
from xdsl.transforms.canonicalize import CanonicalizePass
from xdsl.transforms.common_subexpression_elimination import (
    CommonSubexpressionElimination,
)
from xdsl.transforms.dead_code_elimination import DeadCodeElimination
from xdsl.utils.exceptions import ParseError, PassFailedException, VerifyException


# 1. Pass 注册表：保存类，而非实例。MLIR 对应 PassRegistry 的部分职责。
# 这是 xDSL 实现的标准优化，不是在 Python 中调用 C++ MLIR Pass。
PASSES = {
    "canonicalize": CanonicalizePass,
    "cse": CommonSubexpressionElimination,
    "dce": DeadCodeElimination,
}


def create_context() -> Context:
    # 2. MLIR 对应 MLIRContext + DialectRegistry；这里只加载实际需要的方言。
    ctx = Context()
    ctx.load_dialect(builtin.Builtin)
    ctx.load_dialect(func.Func)
    ctx.load_dialect(arith.Arith)
    return ctx


def main() -> int:
    # 3. 参数：暂不实现 MLIR 的嵌套 pass-pipeline 语法。
    cli = argparse.ArgumentParser(description="读取、验证并优化 MLIR 文本（xDSL）")
    cli.add_argument("input", type=Path, help="输入 .mlir 文件")
    cli.add_argument("-o", "--output", type=Path, help="最终 IR 输出路径，默认 stdout")
    cli.add_argument("--passes", default="", help="按顺序执行：canonicalize,cse,dce")
    cli.add_argument("--dump-after-all", action="store_true", help="每个 Pass 后向 stderr 打印 IR")
    args = cli.parse_args()

    names = [name.strip() for name in args.passes.split(",")] if args.passes else []
    for name in names:
        if name not in PASSES:
            cli.error(f"未知 Pass：{name!r}；可用：{', '.join(PASSES)}")
    if args.output and args.output.resolve() == args.input.resolve():
        cli.error("输入和输出不能是同一个文件，请为 -o 指定新路径")

    try:
        # 4. MLIR 对应 parseSourceFile<ModuleOp> + verify。
        ctx = create_context()
        text = args.input.read_text(encoding="utf-8-sig")
        module = Parser(ctx, text, str(args.input)).parse_module()
        module.verify()

        # 5. MLIR 对应 PassManager 的顺序执行与 verify-each。
        # 显式循环便于学习；不实现其分析缓存、嵌套 Pass 等完整能力。
        for name in names:
            pass_instance = PASSES[name]()
            pass_instance.apply(ctx, module)
            module.verify()
            if args.dump_after_all:
                print(f"// after {name}", file=sys.stderr)
                Printer(stream=sys.stderr).print_op(module)
                print(file=sys.stderr)

        # 6. MLIR 对应 Operation::print。调试信息与可解析的最终 IR 分流。
        if args.output:
            with args.output.open("w", encoding="utf-8") as stream:
                Printer(stream=stream).print_op(module)
                print(file=stream)
        else:
            Printer(stream=sys.stdout).print_op(module)
            print()
    except (OSError, UnicodeError, ParseError, VerifyException, PassFailedException) as error:
        # 只处理预期的输入/编译诊断；程序错误仍保留 traceback 便于调试。
        print(f"my-opt: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
