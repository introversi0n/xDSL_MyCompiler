// --passes canonicalize：编译期折叠成 arith.constant 3，不是执行整个程序。
builtin.module {
  func.func @fold() -> i32 {
    %one = arith.constant 1 : i32
    %two = arith.constant 2 : i32
    %sum = arith.addi %one, %two : i32
    func.return %sum : i32
  }
}
