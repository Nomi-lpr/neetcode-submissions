# duplicate-integer

## 一句话思路
用一个 set 记录已经见过的数字，如果遇到已经在 set 里的数，立刻返回 True，否则遍历完后返回 False。

## 复杂度分析
- **时间复杂度**：O(n)。  
  解释：for 循环遍历了 nums 里的每个元素（n 次），每次 set 的 add 和 in 操作在 Python 中均摊是 O(1)。
- **空间复杂度**：O(n)。  
  解释：最坏情况下 nums 中没有任何重复数字，set 需要存下全部 n 个数字。
- **能否更优**：这已经是最优复杂度。至少要遍历所有元素以确保无重复，时间复杂度不能优于 O(n)。空间上如果允许改变原数组，可以用原地排序 + 相邻比较，但那是 O(1) 额外空间但 O(n log n) 时间。

## 边界条件清单
- **空输入（[]）**：天然覆盖，循环不会进入，直接返回 False。
- **单元素（[a]）**：天然覆盖，循环只进行一次，不会遇到重复，返回 False。
- **全部相同（如 [7,7,7]）**：第二次出现时被检测出来，返回 True，覆盖。
- **包含负数、零**：set in 操作对任何可 hash 的 int 都有效，无影响，覆盖。
- **重复元素恰好出现在最后**：只要有重复都会被检出，覆盖。
- **极大输入**：set 占用 O(n) 空间，但不会溢出（除非超出内存），算法本身无特例处理。
- **非整数元素**：本题假设输入一定是 int 否则 set/in/add 也适用，按默认假设即可。

## Python 语法笔记
1. `seen = set()`
   - 作用：初始化一个空集合，集合只能存可 hash 的对象且不允许重复。
   - 示例：  
     ```python
     s = set()
     s.add(1)
     s.add(1)
     print(len(s))  # 输出1
     ```

2. `if num in seen:`
   - 作用：判断集合 seen 里是否已经有 num，集合的 in 操作是 O(1) 平均复杂度。
   - 示例：
     ```python
     s = {1, 2, 3}
     print(2 in s)  # True
     print(5 in s)  # False
     ```

3. `seen.add(num)`
   - 作用：将当前 num 加入到集合 seen 中。如果已经有就不变，集合内元素唯一。
   - 示例：
     ```python
     s = set()
     s.add(4)
     s.add(4)
     print(s)  # {4}
     ```

4. `return False`/`return True`
   - 作用：遍历过程中只要发现重复立刻返回 True，遍历完都没重复就返回 False。

## 面试口述剧本
「一开始可以用暴力法，两层循环依次比较每对数字，时间复杂度是 O(n^2)，但不高效。  
所以可以用集合 set 作为哈希表：每次遍历 nums 时，看当前数字是否已出现过，若出现过则有重复直接返回 True；否则加入 set。这样每次查找和插入是 O(1)，所以整体时间复杂度降到 O(n)，空间 O(n)。  
最终遍历完没有遇到重复就返回 False。」

## 同类题 & 可复用套路
套路：用 set/hashmap 记录“是否出现过”来高效查找重复元素。
- [Contains Duplicate](https://leetcode.com/problems/contains-duplicate/)（LeetCode 217）
- [Contains Duplicate II](https://leetcode.com/problems/contains-duplicate-ii/)（加窗口约束）
- [Happy Number](https://leetcode.com/problems/happy-number/)（记录 seen 检查循环）
