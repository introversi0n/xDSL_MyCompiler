# stage 1：最小 my-opt

[总方案](总方案.md) · [开发约定](开发约定.md)

**本阶段提供可运行的 my-opt 示例，以及供你动手填写的 Context/Pass 习题。** 习题留白是教学设计；主工具可独立使用。

下面文件和命令都相对项目根目录，使用 Python 3.10+、xDSL 0.71.0。Windows、Linux、macOS 使用同样的 Python 入口。

## 1. 先看哪些文件

| 文件 | 用途 |
|---|---|
| `tools/my_opt.py` | 主示例，也是之后各阶段继续复用的 opt 工具 |
| `tools/exercises/stage01_context.py` | 短习题：Context、注册、Pass；不会破坏主工具 |
| `test/E2E/mlir/stage01/00-empty.mlir` | 空 module 的解析打印 |
| `test/E2E/mlir/stage01/01-add.mlir` | 函数参数、加法结果、返回值 |
| `test/E2E/mlir/stage01/02-cse.mlir` | 两次相同加法均被使用，观察 CSE |
| `test/E2E/mlir/stage01/03-dce.mlir` | 无用乘法、有用加法，观察 DCE |
| `test/E2E/mlir/stage01/04-canonicalize.mlir` | 1+2 的编译期常量折叠 |
| `test/E2E/mlir/stage01/05-invalid-syntax.mlir` | 故意引用未定义的 SSA 值 |
| `test/E2E/mlir/stage01/06-invalid-verify.mlir` | 返回类型不符：解析成功、验证失败 |

没有额外 expected 文件：每个输入注释已给预期，实际检查还验证了 IR 对象的结果与 uses。

## 2. 从这里运行

在项目根目录的终端中，使用你选择的 Python 环境：

```text
python -m pip install xdsl==0.71.0
python tools/my_opt.py --help
python tools/my_opt.py test/E2E/mlir/stage01/00-empty.mlir
python tools/my_opt.py test/E2E/mlir/stage01/01-add.mlir
```

初期不需要 pip install 本项目，也没有 pyproject.toml。依赖是已有的 xdsl==0.71.0；后续 onnx/numpy 与本阶段无关。

### 分别观察三个 Pass

```text
python tools/my_opt.py test/E2E/mlir/stage01/02-cse.mlir --passes cse
python tools/my_opt.py test/E2E/mlir/stage01/03-dce.mlir --passes dce
python tools/my_opt.py test/E2E/mlir/stage01/04-canonicalize.mlir --passes canonicalize
```

- CSE：两次 `arith.addi` 变一次，muli 的两个操作数引用同一个结果。
- DCE：无使用的 `arith.muli` 消失，addi 和 return 保留。没有结果被用不一定能删除，还要考虑可观察副作用。
- canonicalize：最终只需要 constant 3 和 return；它也可能执行 DCE，不代表三个 Pass 行为互斥。

组合并观察顺序：

```text
python tools/my_opt.py test/E2E/mlir/stage01/04-canonicalize.mlir --passes canonicalize,cse,dce --dump-after-all
```

调试标签与中间 IR 在 stderr，最终 IR 在 stdout，因此终端可能看到混合输出；文件输出不混入调试内容：

```text
python tools/my_opt.py test/E2E/mlir/stage01/04-canonicalize.mlir --passes canonicalize -o result.mlir
python tools/my_opt.py result.mlir
```

`-o` 的父目录需要已经存在，且不能与输入是同一路径。这里只保护输入本身，不自动管理输出目录。

### 观察错误

```text
python tools/my_opt.py test/E2E/mlir/stage01/05-invalid-syntax.mlir
python tools/my_opt.py test/E2E/mlir/stage01/06-invalid-verify.mlir
python tools/my_opt.py test/E2E/mlir/stage01/01-add.mlir --passes unknown
```

前两种返回 1，未知 Pass 由 argparse 返回 2；都不是成功。只捕获预期诊断，真正的编程错误保留 traceback。

不依赖 shell 的退出码检查方式：

```text
python -c "import subprocess,sys; p=subprocess.run([sys.executable,'tools/my_opt.py','test/E2E/mlir/stage01/06-invalid-verify.mlir']); print('exit:',p.returncode); sys.exit(0 if p.returncode == 1 else 1)"
```

## 3. 主脚本的六段逻辑

1. **Pass 表**：字典值是类，`PASSES[name]()` 才创建实例。
2. **Context**：加载 builtin/func/arith；工具本身没有重新定义它们。
3. **参数**：检查 Pass 名和输出路径；仅支持逗号分隔的顺序列表。
4. **解析与验证**：读取 UTF-8 文本，Parser 生成 ModuleOp，verify 检查结构和语义约束。
5. **执行 Pass**：每个 `apply(ctx, module)` 后再次 verify，可选打印。
6. **输出与诊断**：Printer 输出 IR，stderr 放错误和调试信息。

Context 不是 IR 容器；ModuleOp 才是这次解析出的程序。Pass 类也不是一个 Operation。这里没有执行 add 函数：常量折叠是编译期转换，运行时传入 1、2 检查 3 留到 stage 5。

## 4. MLIR 目录和 C++ 接口对照

下列 MLIR 路径以 llvm-project 根下的 `mlir/` 开始，是源码导航，不要求本地已下载；不同版本可能调整。

| 当前 Python | MLIR C++ 对应 | 目录/差异 |
|---|---|---|
| `tools/my_opt.py` | `mlir-opt.cpp`、`MlirOptMain` | `mlir/tools/mlir-opt/*`、`mlir/lib/Tools/mlir-opt/*`；这里手写少量驱动逻辑 |
| `Context()` | `MLIRContext` | `mlir/include/mlir/IR/MLIRContext.h`、`mlir/lib/IR/*` |
| `ctx.load_dialect(...)` | `DialectRegistry::insert`、Context 加载 Dialect | `mlir/include/mlir/IR/DialectRegistry.h`；Python 不必额外创建一个 Registry 对象 |
| `Parser(...).parse_module()` | `parseSourceFile<ModuleOp>` | `mlir/include/mlir/Parser/*`、`mlir/lib/Parser/*` |
| `module.verify()` | `mlir::verify`、Operation 验证流程 | `mlir/include/mlir/IR/Verifier.h`、`mlir/lib/IR/Verifier.cpp` |
| `PASSES` + 顺序 `apply` | Pass 注册、PassManager::addPass/run | `mlir/include/mlir/Pass/*`、`mlir/lib/Pass/*`；没有嵌套 pipeline、分析缓存与失效管理 |
| `Printer.print_op` | Operation 打印 | `mlir/lib/IR/AsmPrinter.cpp` |
| xDSL CSE/DCE/canonicalize | MLIR 通用优化/重写机制 | `mlir/lib/Transforms/*`；xDSL 是独立 Python 实现，并非调用 C++ Pass |

`dce` 是本工具采用的 xDSL Pass 名，不声称 MLIR 有完全一样的独立命令行 Pass。当前 xDSL DCE 源码也注明部分内存副作用判断与 MLIR 存在区别。

`--passes` 是我们的小接口；MLIR 可使用带嵌套作用域的 `--pass-pipeline`，本工具没有实现那套语法。`--dump-after-all` 对应观察目的，不能等同 MLIR 的完整 instrumentation。

## 5. C++ 构建：先把四件事分清

```text
普通 C++：
  .h 声明 → .cpp 编译成目标文件 → 链接目标文件/库 → 运行程序

MLIR 自定义 Dialect（stage 3 对照讲解）：
  .td → mlir-tblgen 生成 .inc → .h/.cpp 引入 → 编译库
      → opt 链接库 → 程序运行时注册 Dialect 到 Context
```

- `#include` 提供声明或定义给编译器；找不到头文件通常是编译问题。
- 只有函数声明但未链接实现，通常在链接阶段报未定义引用。
- 链接了 Dialect 库不等于 Context 已注册/加载它。
- Python `import` 让类可用，也不等于 `ctx.load_dialect(...)` 已执行。
- CMake 的 `target_include_directories` 配头文件搜索，`target_link_libraries` 配链接依赖；二者不可互相替代。

以上用于理解 MLIR 的实现方式。本项目代码使用 Python，不要求配置 C++ 编译器，也不添加 C++ 构建练习；后续自定义 Dialect/Pass 时继续在文档中对照 ODS、头文件、实现和注册过程。

## 6. 留给你的练习

运行：

```text
python tools/exercises/stage01_context.py
```

未填写时只提示需要完成 U1。阅读顺序建议：先主脚本的 `create_context`，再关掉主脚本独立完成。

- **U1**：创建 ctx，注册 builtin/func/arith。代码 TODO 留在练习脚本。
- **U2**：实例化 CSE，调用 apply，再 verify。完成后重复 addi 应合并。代码 TODO 留在练习脚本。

<!-- #TODO[USER][stage01-U3] 分别移除 func/arith 注册观察错误；比较未定义 SSA 值与错误返回类型，写下错误发生在注册、解析还是验证。 -->
<!-- #TODO[USER][stage01-U4] 修改 02-cse 的第二个 addi，让它不再与第一个等价，观察 CSE 是否仍合并并解释原因。 -->
<!-- #TODO[USER][stage01-U5] 比较 --passes cse 与 --passes canonicalize,cse 在两个不同输入上的结果，指出每一步是否真的改变 IR。 -->

公开版本保留这些 TODO 作为题目。你可以在自己的副本中填写实现、去掉标记并记录心得。它们不属于主示例的功能缺陷，运行主示例不需要先做完习题。

## 7. 本阶段开发日志

### 记录 1：方案整理

原先分别保存总方案、开发约定、MLIR/C++ 对照、执行验证、开发日志以及七份阶段方案。检查了用户已有的 resnet50 输入/输出头文件：char[1024] 和 char[10]；未修改模型与数据。

本轮将未开始的阶段、执行验证合同合入 `docs/总方案.md`，约定改为 `docs/开发约定.md`，删除被合并的重复文件。日志及当前 MLIR/C++ 对应放入本文件。

### 记录 2：my-opt 与样例

新增 `tools/my_opt.py`、`tools/exercises/stage01_context.py` 和 `test/E2E/mlir/stage01/*` 七个输入；更新 README。没有创建 Python 包、插件、额外 runtime 或后续目录。

核对的 xDSL 0.71 API：`CommonSubexpressionElimination`（cse）、`DeadCodeElimination`（dce）、`CanonicalizePass`（canonicalize），均通过 `apply(ctx,module)` 执行。

### 记录 3：实际验收

在 Windows、Python 3.11、xDSL 0.71.0 环境实跑 CLI，并用一次性检查脚本重新解析输出，检查 op 与 operands，而不是只比较打印字符串。一次性脚本放在系统临时目录，不增加项目学习负担。代码采用跨平台 Python 接口；尚未在 Linux/macOS 实机验证。

| 检查 | 实际结果 |
|---|---|
| 五个正确输入解析/验证/打印，再解析输出 | 通过 |
| CSE 后只有一次 addi，muli 两个输入是同一个 SSA 对象 | 通过 |
| DCE 删除无用 muli、保留有用 addi | 通过 |
| canonicalize,cse,dce 按序运行，最终 constant 值为 3 | 通过 |
| dump 只在 stderr，stdout 仍为可解析 IR | 通过 |
| 未定义 SSA、错误返回类型、缺文件、未知/空 Pass 项 | 非零退出，无最终 IR |
| 输入和 -o 指向同一路径 | 拒绝覆盖输入 |
| -o 输出文件再交给 my-opt 读取 | 通过 |
| 习题初始模板 | 给出填写提示，不影响主工具 |

这些是编译工具验收，不是模型推理或 runtime 执行测试。本阶段作为示例与习题一并提供；没有执行 C++ 程序或构建 MLIR。

### 记录 4：目录职责与跨平台入口

更新 `docs/总方案.md`、`docs/开发约定.md`：后续 Python 实现使用按需创建的 `xdsl_mycompiler/`。补全旧大目录方案的保留/合并/推迟理由，以及自定义 Dialect/Pass 的 Python 模块与 C++ 声明、ODS、实现、构建对应要求。C++ 内容限于文档对照。

阶段运行入口统一为本文的 Python 命令，移除平台专用启动器及调用说明。README 改为学习项目简介、三项主旨和快速开始。习题留白作为教材内容发布，不将其标记为项目欠缺。本轮没有初始化 Git、提交或上传；base/stage1 的提交边界在对话中说明。

移除启动器后重新通过 Python CLI 验收：五个正确输入、CSE 的 SSA 替换、DCE、常量折叠与 Pass 顺序、错误退出、输出文件再解析以及习题提示均通过。实际运行环境仍为 Windows，Linux/macOS 的实机验证不在此次结果中。
