"""独立习题，不影响 my_opt.py。见 docs/stage-01-my-opt.md 的 U1/U2。

在项目根目录运行：python tools/exercises/stage01_context.py
"""

from pathlib import Path

from xdsl.context import Context
from xdsl.dialects import arith, builtin, func
from xdsl.parser import Parser
from xdsl.transforms.common_subexpression_elimination import CommonSubexpressionElimination


#TODO[USER][stage01-U1] 创建 Context，并依次注册 builtin、func、arith。
# 提示：Context()；ctx.load_dialect(方言对象)。方言对象可从上面三个模块查找。
ctx = None


def main():
    if ctx is None:
        print("请先完成 stage01-U1：创建 Context 并注册三个 Dialect。")
        return

    source = Path("test/E2E/mlir/stage01/02-cse.mlir")
    module = Parser(ctx, source.read_text(encoding="utf-8"), str(source)).parse_module()
    module.verify()

    #TODO[USER][stage01-U2] 实例化 CSE Pass 并调用 apply(ctx, module)，随后再次 verify。
    # 提示：导入的是类 CommonSubexpressionElimination，类名不等于 CLI 名 cse。
    print(module)


if __name__ == "__main__":
    main()
