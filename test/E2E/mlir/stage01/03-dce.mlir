// --passes dce：unused 无使用且无可观察副作用，可以删除；sum 与 return 保留。
builtin.module {
  func.func @dead_code(%a: i32, %b: i32) -> i32 {
    %unused = arith.muli %a, %b : i32
    %sum = arith.addi %a, %b : i32
    func.return %sum : i32
  }
}
