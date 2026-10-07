# xDSL MyCompiler

**从一条 IR 开始，亲手搭建自己的编译器。**

这是一个持续演进的编译器学习项目：用 Python + xDSL，逐步理解 MLIR 的 IR、Dialect、Pass、Lowering 和执行流程。它的价值不是支持多少语言和模型，而是让每一步都能运行、看懂、修改。

## 想保留的三件事

- **理解权**：知道每个 Python 步骤对应 MLIR 的什么机制，而不只会调用 API。
- **动手空间**：提供能运行的示例，也留下需要你填写的习题。留白是教材的一部分，不是项目故障。
- **可追溯性**：从阶段文档和开发记录里，找到每段实现为什么出现、怎样验证。

当前提供 **stage 1：最小 my-opt**，以及 Context、Dialect 注册和 Pass 练习。C++/MLIR 仅作为文档中的接口与构建对照，本项目实现使用 Python。

## 快速开始

需要 Python 3.10+。在你选择的 Python 环境中安装依赖，并在项目根目录运行以下命令；Windows、Linux、macOS 使用相同入口：

```text
python -m pip install xdsl==0.71.0
python tools/my_opt.py test/E2E/mlir/stage01/01-add.mlir
python tools/my_opt.py test/E2E/mlir/stage01/02-cse.mlir --passes cse --dump-after-all
python tools/my_opt.py test/E2E/mlir/stage01/04-canonicalize.mlir --passes canonicalize,cse,dce
```

工具目前支持 builtin/func/arith 和上述三个 Pass；它优化 IR，尚不执行程序。`-o result.mlir` 保存最终 IR，`--dump-after-all` 向 stderr 打印每一步。

然后试着自己完成：

```text
python tools/exercises/stage01_context.py
```

项目内搜索 `#TODO[USER]` 找到练习。预留的练习代码只影响练习入口，不影响主示例。

## 阅读路线

- [stage 1：最小 my-opt](docs/stage-01-my-opt.md)：运行命令、文件说明、MLIR/C++ 对照、习题和开发记录。
- [总方案](docs/总方案.md)：后续阶段、目录设计和执行验证路线。
- [开发约定](docs/开发约定.md)：怎样保持代码简单、示例可靠、文档与实现一致。

`tools/` 放可运行工具和练习，`test/E2E/` 放教学输入与期望数据，`docs/` 放说明。后续有需要才建立 `xdsl_mycompiler/` 包；不预先铺满目录，也不额外维护 shell 启动脚本。
