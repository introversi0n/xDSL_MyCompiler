# tools

这里放可以直接运行的 Python 工具。所有命令都在项目根目录执行，Windows / Linux / macOS 相同。

## my_opt.py 和 exercises 的关系

`my_opt.py` 是长期维护的主工具，可以理解为简化版 `mlir-opt`：

```text
读取 .mlir → 创建 Context / 注册 Dialect → 解析验证
→ 按顺序执行 Pass → 打印或保存
```

后面的 stage 只会让它支持更多 Dialect、Pass 和 Lowering，**不会每个 stage 复制一个新的 my_opt**。

`exercises/stage01_context.py` 是 stage 1 的习题：把主工具里的 Context、Dialect 注册、Pass 执行单独拆出来并留空，由学习者自己填写。它不影响主工具，也不会自动并入 `my_opt.py`。

- `my_opt.py` = 已经组装好的示例
- `exercises/*` = 拆开、留白的练习题

## 以后什么时候新增文件

| 情况 | 放哪里 |
|---|---|
| 主工具需要更多 Dialect / Pass | 扩充 `my_opt.py` |
| 独立职责（查看 IR、执行、导入 ONNX） | 在 `tools/` 下新增 `inspect_ir.py`、`run_ir.py`、`import_onnx.py` 等 |
| 每个 stage 的练习 | `tools/exercises/stageXX_*.py` |
| 多个工具真正复用的实现 | 以后抽到 `xdsl_mycompiler/` 包，`my_opt.py` 变成薄的命令行入口 |

## 运行

```text
python tools/my_opt.py test/E2E/mlir/stage01/01-add.mlir
python tools/my_opt.py test/E2E/mlir/stage01/02-cse.mlir --passes cse --dump-after-all
python tools/exercises/stage01_context.py
```

项目内搜索 `#TODO[USER]` 找到练习，搜索 `#TODO[AGENT]` 和 `#TODO[PLAN]` 查看实现与方案待办。详细说明见 [stage 1](../docs/stage-01-my-opt.md)。
