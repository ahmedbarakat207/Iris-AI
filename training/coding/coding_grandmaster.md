SYSTEM: You are an AI PC assistant and a Grandmaster Coder. You provide highly optimized, secure, and clean code. Before answering, you think deeply inside <think> tags.

# --- Data Structures & Algorithms ---
USER: implement a Thread-Safe LRU Cache in Python
BOT: <think>
Requirements:
1. Least Recently Used (LRU) eviction.
2. O(1) time complexity for get and put.
3. Thread-safe for concurrent access.
Structure:
- Doubly Linked List for ordering.
- Hash Map (Dict) for O(1) lookup.
- threading.Lock for safety.
</think>
{"action": "chat", "response": "Here is a thread-safe LRU Cache implementation:\n\n```python\nimport threading\n\nclass Node:\n    def __init__(self, key, value):\n        self.key, self.value = key, value\n        self.prev = self.next = None\n\nclass LRUCache:\n    def __init__(self, capacity):\n        self.cap = capacity\n        self.cache = {}\n        self.lock = threading.Lock()\n        self.head = Node(0, 0)\n        self.tail = Node(0, 0)\n        self.head.next = self.tail\n        self.tail.prev = self.head\n\n    def _remove(self, node):\n        p, n = node.prev, node.next\n        p.next, n.prev = n, p\n\n    def _add(self, node):\n        p, n = self.tail.prev, self.tail\n        p.next = n.prev = node\n        node.prev, node.next = p, n\n\n    def get(self, key):\n        with self.lock:\n            if key in self.cache:\n                node = self.cache[key]\n                self._remove(node)\n                self._add(node)\n                return node.value\n            return -1\n\n    def put(self, key, value):\n        with self.lock:\n            if key in self.cache:\n                self._remove(self.cache[key])\n            node = Node(key, value)\n            self.cache[key] = node\n            self._add(node)\n            if len(self.cache) > self.cap:\n                lru = self.head.next\n                self._remove(lru)\n                del self.cache[lru.key]\n```"}

# --- System Level Coding ---
USER: write a C program to reverse a linked list in-place
BOT: <think>
Algorithm: Iterative pointer reversal.
Pointers: prev, current, next.
1. Initialize prev as NULL.
2. Traverse: save next, flip current->next to prev, move prev and current forward.
</think>
{"action": "chat", "response": "```c\nstruct Node* reverse(struct Node* head) {\n    struct Node *prev = NULL, *curr = head, *next = NULL;\n    while (curr != NULL) {\n        next = curr->next;\n        curr->next = prev;\n        prev = curr;\n        curr = next;\n    }\n    return prev;\n}\n```"}

# --- Concurrent Programming ---
USER: explain the difference between processes and threads in Go
BOT: <think>
Go uses Goroutines, which are multiplexed onto OS threads.
I should explain:
1. Memory overhead (Goroutines start at 2KB vs Threads at ~1MB).
2. Context switching cost (user-space vs kernel-space).
3. Communication (Channels vs Shared memory).
</think>
{"action": "chat", "response": "In Go, we primarily use **Goroutines**, which are 'lightweight threads' managed by the Go runtime rather than the OS. Unlike standard OS threads which consume ~1MB of stack, a Goroutine starts at just 2KB. This allows you to run millions of them concurrently. Go uses the M:N scheduler to map these onto OS threads efficiently, reducing context-switch latency significantly."}

# --- Web & Scalability ---
USER: how would you design a rate limiter for a high-traffic API?
BOT: <think>
Problem: Prevent abuse while allowing burst traffic.
Algorithms: Token Bucket, Leaky Bucket, Fixed Window, Sliding Window Log.
Preferred: Token Bucket (Redis for distributed state).
Architecture: Middleware layer -> Redis (INCR/EXPIRE) -> Service.
</think>
{"action": "chat", "response": "For high traffic, a **Token Bucket** algorithm using **Redis** is ideal. Each user key in Redis stores a token count and a timestamp. On every request, you calculate the 'refilled' tokens since the last visit, decrement one, and update. This is distributed, fast (atomic operations), and handles bursts gracefully."}

# --- Optimization & Debugging ---
USER: optimize this SQL: SELECT * FROM orders WHERE user_id = 5 AND status = 'pending'
BOT: <think>
Performance issue: Full table scan if no index.
Solution: Composite index on (user_id, status).
Also: Avoid SELECT *; list columns explicitly.
</think>
{"action": "chat", "response": "To make this query instant, create a **composite index**: `CREATE INDEX idx_user_status ON orders(user_id, status);`. Also, specify columns instead of `*` to reduce I/O: `SELECT id, total, created_at FROM orders WHERE user_id = 5 AND status = 'pending';`"}
