class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen={}
        ans=[]
        for i in range(len(nums)):
            seen[nums[i]]=i
        
        for i in range(len(nums)):
            n = nums[i]
            diff=target-n
            if diff in seen and seen[diff] != i:
                return [i, seen[diff]]
        
