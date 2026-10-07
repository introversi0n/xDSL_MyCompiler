// --passes cse：两次相同 addi 合并为一次，muli 的两个输入引用同一结果。
builtin.module {
  func.func @duplicate(%a: i32, %b: i32) -> i32 {
    %first = arith.addi %a, %b : i32
    %second = arith.addi %a, %b : i32
    %product = arith.muli %first, %second : i32
    func.return %product : i32
  }
}
