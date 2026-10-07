// 故意错误：引用未定义的 SSA 值，应在解析阶段失败。
builtin.module {
  func.func @bad() -> i32 {
    func.return %missing : i32
  }
}
