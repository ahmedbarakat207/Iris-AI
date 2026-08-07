# Python Problem Solving and Algorithms

This RAG corpus provides optimized Python solutions for classic algorithms and data structures. Python's concise syntax, powerful standard library (like `collections` and `heapq`), and dynamic typing make it excellent for competitive programming and technical interviews.

---

## 1. Sliding Window & Two Pointers

### 1.1 Longest Substring Without Repeating Characters
A classic sliding window problem utilizing a dictionary to track the most recent index of seen characters.

```python
def length_of_longest_substring(s: str) -> int:
    """
    Finds the length of the longest substring without repeating characters.
    Time Complexity: O(N)
    Space Complexity: O(min(N, M)) where M is the charset size.
    """
    char_index_map = {}
    left = 0
    max_length = 0
    
    for right, char in enumerate(s):
        if char in char_index_map and char_index_map[char] >= left:
            # Move the left pointer to the right of the previous occurrence
            left = char_index_map[char] + 1
            
        char_index_map[char] = right
        max_length = max(max_length, right - left + 1)
        
    return max_length
```

### 1.2 Container With Most Water
Two pointers moving towards the center to maximize area.

```python
def max_area(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    max_water = 0
    
    while left < right:
        width = right - left
        # Area is determined by the shorter line
        current_water = min(height[left], height[right]) * width
        max_water = max(max_water, current_water)
        
        # Always move the shorter line in hopes of finding a taller one
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
            
    return max_water
```

---

## 2. Graph Algorithms (BFS / DFS / Topological Sort)

### 2.1 Course Schedule (Topological Sort with Kahn's Algorithm)
Detecting cycles and ordering dependencies using in-degrees and BFS.

```python
from collections import deque, defaultdict

def can_finish_courses(numCourses: int, prerequisites: list[list[int]]) -> bool:
    """
    Determines if all courses can be finished given prerequisite pairs.
    """
    graph = defaultdict(list)
    in_degree = [0] * numCourses
    
    # Build graph and in-degree array
    for course, pre in prerequisites:
        graph[pre].append(course)
        in_degree[course] += 1
        
    # Start with courses that have no prerequisites
    queue = deque([i for i in range(numCourses) if in_degree[i] == 0])
    courses_taken = 0
    
    while queue:
        current = queue.popleft()
        courses_taken += 1
        
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
                
    return courses_taken == numCourses
```

### 2.2 Word Ladder (Shortest Path with BFS)
Finding the shortest transformation sequence from a begin word to an end word.

```python
from collections import deque

def ladder_length(beginWord: str, endWord: str, wordList: list[str]) -> int:
    word_set = set(wordList)
    if endWord not in word_set:
        return 0
        
    queue = deque([(beginWord, 1)])
    
    while queue:
        current_word, level = queue.popleft()
        
        if current_word == endWord:
            return level
            
        # Try changing each character of the current word
        for i in range(len(current_word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                if c == current_word[i]:
                    continue
                    
                next_word = current_word[:i] + c + current_word[i+1:]
                
                if next_word in word_set:
                    word_set.remove(next_word) # Avoid revisiting
                    queue.append((next_word, level + 1))
                    
    return 0
```

---

## 3. Dynamic Programming

### 3.1 0/1 Knapsack Problem (Tabulation)
Solving the classic knapsack problem using a 1D DP array for space optimization.

```python
def knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    """
    Returns the maximum value that can be put in a knapsack of a given capacity.
    Time Complexity: O(N * W), Space Complexity: O(W)
    """
    n = len(weights)
    # dp[w] will hold the maximum value achievable with capacity w
    dp = [0] * (capacity + 1)
    
    for i in range(n):
        # Traverse backwards to prevent using the same item multiple times
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
            
    return dp[capacity]
```

### 3.2 Lowest Common Ancestor (DFS & Backtracking)

```python
class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None

def lowest_common_ancestor(root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
    # Base cases: empty tree or we found one of the targets
    if not root or root == p or root == q:
        return root
        
    # Recurse on left and right subtrees
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    
    # If both return non-null, this root is the LCA
    if left and right:
        return root
        
    # Otherwise, return the non-null child
    return left if left else right
```

---

## 4. Backtracking

### 4.1 N-Queens Solver
An elegant backtracking solution using sets to track attacked columns and diagonals.

```python
def solveNQueens(n: int) -> list[list[str]]:
    cols = set()
    pos_diag = set()  # r + c
    neg_diag = set()  # r - c
    
    res = []
    board = [["."] * n for _ in range(n)]
    
    def backtrack(r):
        if r == n:
            copy = ["".join(row) for row in board]
            res.append(copy)
            return
            
        for c in range(n):
            if c in cols or (r + c) in pos_diag or (r - c) in neg_diag:
                continue
                
            cols.add(c)
            pos_diag.add(r + c)
            neg_diag.add(r - c)
            board[r][c] = "Q"
            
            backtrack(r + 1)
            
            cols.remove(c)
            pos_diag.remove(r + c)
            neg_diag.remove(r - c)
            board[r][c] = "."
            
    backtrack(0)
    return res
```

---

## 5. Priority Queues / Heaps

### 5.1 K-th Largest Element in an Array
Using a Min-Heap of size K to maintain the top K elements. Optimized `O(N log K)` time complexity.

```python
import heapq

def findKthLargest(nums: list[int], k: int) -> int:
    min_heap = []
    
    for num in nums:
        heapq.heappush(min_heap, num)
        if len(min_heap) > k:
            heapq.heappop(min_heap)
            
    return min_heap[0]
```
