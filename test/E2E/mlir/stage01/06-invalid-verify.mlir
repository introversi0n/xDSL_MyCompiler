// 故意错误：语法有效，但函数声明返回 i32，实际返回 i64，应在 verify 时失败。
builtin.module {
  func.func @bad() -> i32 {
    %value = arith.constant 1 : i64
    func.return %value : i64
  }
}
