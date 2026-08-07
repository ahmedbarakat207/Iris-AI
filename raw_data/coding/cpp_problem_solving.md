# C++ Problem Solving and Algorithms

This RAG corpus contains high-performance C++ implementations of advanced algorithms. C++ is the standard for competitive programming due to its speed, low-level memory control, and the rich Standard Template Library (STL).

---

## 1. Advanced Graph Algorithms

### 1.1 Dijkstra's Algorithm (Shortest Path)
Using `std::priority_queue` to efficiently find the shortest path from a source node to all other nodes in a weighted graph.

```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <limits>

using namespace std;

const int INF = numeric_limits<int>::max();

// Define graph as adjacency list: pair<weight, target_node>
typedef pair<int, int> pii;
typedef vector<vector<pii>> Graph;

vector<int> dijkstra(int source, const Graph& graph) {
    int n = graph.size();
    vector<int> dist(n, INF);
    
    // Min-heap priority queue
    priority_queue<pii, vector<pii>, greater<pii>> pq;
    
    dist[source] = 0;
    pq.push({0, source});
    
    while (!pq.empty()) {
        int current_dist = pq.top().first;
        int u = pq.top().second;
        pq.pop();
        
        // Skip stale pairs in the priority queue
        if (current_dist > dist[u]) continue;
        
        for (const auto& edge : graph[u]) {
            int weight = edge.first;
            int v = edge.second;
            
            if (dist[u] + weight < dist[v]) {
                dist[v] = dist[u] + weight;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}
```

### 1.2 Disjoint Set / Union-Find with Path Compression
An extremely efficient data structure for keeping track of a partition of a set into disjoint subsets. Excellent for finding Minimum Spanning Trees (Kruskal's).

```cpp
#include <vector>

class UnionFind {
private:
    std::vector<int> parent;
    std::vector<int> rank;

public:
    UnionFind(int size) {
        parent.resize(size);
        rank.resize(size, 0);
        for (int i = 0; i < size; ++i) {
            parent[i] = i;
        }
    }

    int find(int i) {
        if (parent[i] == i)
            return i;
        // Path compression
        return parent[i] = find(parent[i]);
    }

    bool unite(int i, int j) {
        int rootI = find(i);
        int rootJ = find(j);

        if (rootI != rootJ) {
            // Union by rank
            if (rank[rootI] < rank[rootJ]) {
                parent[rootI] = rootJ;
            } else if (rank[rootI] > rank[rootJ]) {
                parent[rootJ] = rootI;
            } else {
                parent[rootJ] = rootI;
                rank[rootI]++;
            }
            return true;
        }
        return false;
    }
};
```

---

## 2. Dynamic Programming & Advanced Searching

### 2.1 Longest Increasing Subsequence (O(N log N))
Using binary search (`std::lower_bound`) to optimize the standard O(N^2) dynamic programming solution.

```cpp
#include <vector>
#include <algorithm>

using namespace std;

int lengthOfLIS(vector<int>& nums) {
    if (nums.empty()) return 0;
    
    vector<int> tails;
    
    for (int x : nums) {
        auto it = lower_bound(tails.begin(), tails.end(), x);
        if (it == tails.end()) {
            tails.push_back(x); // Append if x is larger than all elements in tails
        } else {
            *it = x; // Replace to maintain the smallest possible tail for the sequence length
        }
    }
    
    return tails.size();
}
```

---

## 3. Advanced Data Structures

### 3.1 Prefix Tree (Trie)
Used for fast string matching, autocomplete, and dictionary representations.

```cpp
#include <string>
#include <unordered_map>

class TrieNode {
public:
    std::unordered_map<char, TrieNode*> children;
    bool isEndOfWord;
    
    TrieNode() : isEndOfWord(false) {}
};

class Trie {
private:
    TrieNode* root;
    
public:
    Trie() {
        root = new TrieNode();
    }
    
    void insert(const std::string& word) {
        TrieNode* current = root;
        for (char c : word) {
            if (current->children.find(c) == current->children.end()) {
                current->children[c] = new TrieNode();
            }
            current = current->children[c];
        }
        current->isEndOfWord = true;
    }
    
    bool search(const std::string& word) {
        TrieNode* current = root;
        for (char c : word) {
            if (current->children.find(c) == current->children.end()) {
                return false;
            }
            current = current->children[c];
        }
        return current->isEndOfWord;
    }
    
    bool startsWith(const std::string& prefix) {
        TrieNode* current = root;
        for (char c : prefix) {
            if (current->children.find(c) == current->children.end()) {
                return false;
            }
            current = current->children[c];
        }
        return true;
    }
};
```

---

## 4. Segment Tree (Range Queries)

### 4.1 Range Sum Query with Point Updates
A segment tree allows answering range sum/min/max queries in `O(log N)` time and updating elements in `O(log N)` time.

```cpp
#include <vector>

class SegmentTree {
private:
    std::vector<int> tree;
    int n;

    void build(const std::vector<int>& arr, int node, int start, int end) {
        if (start == end) {
            tree[node] = arr[start];
        } else {
            int mid = start + (end - start) / 2;
            build(arr, 2 * node, start, mid);
            build(arr, 2 * node + 1, mid + 1, end);
            tree[node] = tree[2 * node] + tree[2 * node + 1];
        }
    }

    void update(int node, int start, int end, int idx, int val) {
        if (start == end) {
            tree[node] = val;
        } else {
            int mid = start + (end - start) / 2;
            if (start <= idx && idx <= mid) {
                update(2 * node, start, mid, idx, val);
            } else {
                update(2 * node + 1, mid + 1, end, idx, val);
            }
            tree[node] = tree[2 * node] + tree[2 * node + 1];
        }
    }

    int query(int node, int start, int end, int l, int r) {
        if (r < start || end < l) {
            return 0;
        }
        if (l <= start && end <= r) {
            return tree[node];
        }
        int mid = start + (end - start) / 2;
        int p1 = query(2 * node, start, mid, l, r);
        int p2 = query(2 * node + 1, mid + 1, end, l, r);
        return p1 + p2;
    }

public:
    SegmentTree(const std::vector<int>& arr) {
        n = arr.size();
        tree.resize(4 * n);
        build(arr, 1, 0, n - 1);
    }

    void update(int idx, int val) {
        update(1, 0, n - 1, idx, val);
    }

    int query(int l, int r) {
        return query(1, 0, n - 1, l, r);
    }
};
```

---

## 5. Bit Manipulation

### 5.1 Power Set Generation
Generate all subsets of a set using binary representation.

```cpp
#include <vector>

std::vector<std::vector<int>> subsets(std::vector<int>& nums) {
    int n = nums.size();
    int subsetCount = 1 << n; // 2^n
    std::vector<std::vector<int>> result;
    
    for (int mask = 0; mask < subsetCount; ++mask) {
        std::vector<int> currentSubset;
        for (int i = 0; i < n; ++i) {
            // Check if the i-th bit is set in the mask
            if (mask & (1 << i)) {
                currentSubset.push_back(nums[i]);
            }
        }
        result.push_back(currentSubset);
    }
    
    return result;
}
```
