// 解析打印不会执行此函数。后续阶段才用 runtime 调用它。
builtin.module {
  func.func @add(%a: i32, %b: i32) -> i32 {
    %sum = arith.addi %a, %b : i32
    func.return %sum : i32
  }
}
