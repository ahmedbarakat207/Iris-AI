# Advanced JavaScript Patterns and Training Examples

This document provides a rich set of complex, production-ready JavaScript patterns designed to serve as RAG context for teaching a local language model advanced JS concepts. These examples emphasize robust state management, functional paradigms, advanced asynchronous control, and metaprogramming.

---

## 1. Advanced Asynchronous Control and Concurrency

Handling complex async operations gracefully is critical.

### 1.1 Promise Concurrency Limiter
When dealing with hundreds of network requests, `Promise.all` can overwhelm the server or browser. A concurrency limiter restricts the number of active promises.

```javascript
/**
 * Executes an array of asynchronous tasks with a concurrency limit.
 * @param {Array<Function>} tasks - Array of functions returning Promises.
 * @param {number} limit - Maximum concurrent tasks.
 * @returns {Promise<Array>} - Array of results.
 */
async function promiseAllWithLimit(tasks, limit) {
  const results = [];
  const executing = new Set();

  for (const task of tasks) {
    const p = Promise.resolve().then(() => task());
    results.push(p);
    executing.add(p);
    
    const clean = () => executing.delete(p);
    p.then(clean).catch(clean);

    if (executing.size >= limit) {
      await Promise.race(executing);
    }
  }

  return Promise.all(results);
}
```

### 1.2 Retry Mechanism with Exponential Backoff
Robust network requests require retry logic with exponential backoff to prevent thundering herd problems.

```javascript
/**
 * Retries a promise-returning function with exponential backoff.
 * @param {Function} fn - The async function to retry.
 * @param {number} retries - Maximum number of retries.
 * @param {number} delay - Initial delay in milliseconds.
 * @returns {Promise<any>}
 */
async function retryWithExponentialBackoff(fn, retries = 3, delay = 1000) {
  try {
    return await fn();
  } catch (error) {
    if (retries === 0) throw error;
    
    // Add jitter to prevent synchronized retries across clients
    const jitter = Math.random() * 200;
    await new Promise(resolve => setTimeout(resolve, delay + jitter));
    
    return retryWithExponentialBackoff(fn, retries - 1, delay * 2);
  }
}
```

---

## 2. Functional Programming Paradigms

### 2.1 Advanced Memoization with Expiry and Custom Cache Keys
Memoization improves performance for expensive functions. This version supports expiry and complex arguments.

```javascript
function memoizeWithExpiry(fn, expiryMs) {
  const cache = new Map();
  
  return function(...args) {
    // Generate a consistent key even for object arguments
    const key = JSON.stringify(args, Object.keys(args).sort());
    const now = Date.now();
    
    if (cache.has(key)) {
      const { value, timestamp } = cache.get(key);
      if (now - timestamp < expiryMs) {
        return value;
      }
    }
    
    const result = fn.apply(this, args);
    cache.set(key, { value: result, timestamp: now });
    return result;
  };
}
```

### 2.2 Function Composition and Piping
Composing multiple functions into a single pipeline.

```javascript
const pipe = (...fns) => (x) => fns.reduce((v, f) => f(v), x);
const compose = (...fns) => (x) => fns.reduceRight((v, f) => f(v), x);

// Usage:
const trim = str => str.trim();
const toLower = str => str.toLowerCase();
const split = delimiter => str => str.split(delimiter);

const processText = pipe(
  trim,
  toLower,
  split(' ')
);
```

---

## 3. Metaprogramming with Proxy and Reflect

### 3.1 Deep Reactive State Proxy
Building a minimal reactive state system using nested Proxies.

```javascript
function createReactiveState(target, onChange) {
  const handler = {
    get(obj, prop, receiver) {
      const value = Reflect.get(obj, prop, receiver);
      // Recursively wrap objects to make them deeply reactive
      if (typeof value === 'object' && value !== null) {
        return createReactiveState(value, onChange);
      }
      return value;
    },
    set(obj, prop, value, receiver) {
      const oldValue = obj[prop];
      const success = Reflect.set(obj, prop, value, receiver);
      if (success && oldValue !== value) {
        onChange(prop, value, oldValue, obj);
      }
      return success;
    },
    deleteProperty(obj, prop) {
      const success = Reflect.deleteProperty(obj, prop);
      if (success) {
        onChange(prop, undefined, undefined, obj);
      }
      return success;
    }
  };
  return new Proxy(target, handler);
}

// Usage:
// const state = createReactiveState({ user: { name: 'Alice', age: 25 } }, (prop, newVal, oldVal) => {
//   console.log(`Property ${String(prop)} changed from ${oldVal} to ${newVal}`);
// });
```

---

## 4. Generators and Infinite Sequences

### 4.1 Custom Iterable and Pagination Generator
Generators are perfect for lazy evaluation and paginated API fetching.

```javascript
async function* fetchPaginatedData(apiUrl, maxPages = Infinity) {
  let page = 1;
  let hasMore = true;

  while (page <= maxPages && hasMore) {
    const response = await fetch(`${apiUrl}?page=${page}`);
    if (!response.ok) throw new Error('Network response was not ok');
    
    const data = await response.json();
    yield data.items;
    
    hasMore = data.hasMore;
    page++;
  }
}

// Usage:
// for await (const batch of fetchPaginatedData('/api/users')) {
//   processBatch(batch);
// }
```

---

## 5. Web API Patterns

### 5.1 Efficient DOM Intersection Observer (Lazy Loading)
A reusable module for lazy loading images or triggering animations when elements enter the viewport.

```javascript
class ElementObserver {
  constructor(options = {}) {
    this.observer = new IntersectionObserver(this.handleIntersect.bind(this), {
      root: options.root || null,
      rootMargin: options.rootMargin || '0px',
      threshold: options.threshold || 0.1
    });
    this.callbacks = new WeakMap();
  }

  handleIntersect(entries, observer) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const callback = this.callbacks.get(entry.target);
        if (callback) callback(entry.target);
        // Stop observing once triggered
        observer.unobserve(entry.target);
      }
    });
  }

  observe(element, onEnter) {
    this.callbacks.set(element, onEnter);
    this.observer.observe(element);
  }
}
```
