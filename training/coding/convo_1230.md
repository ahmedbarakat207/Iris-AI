# الرمز التعريفي للمحادثة: Convo_1230

User:
How do I write a simple if-else statement in Python?

---

Bot
A simple if-else statement in Python checks a condition and runs one block of code if the condition is true, or another block if it's false. The basic syntax is:

```python
if condition:
    # code to run if condition is true
else:
    # code to run if condition is false
```

Here's a straightforward example:

```python
x = 5
if x > 10:
    print("x is greater than 10")
else:
    print("x is not greater than 10")
```

In this case, since x is 5 (which isn't greater than 10), it will print "x is not greater than 10". Remember to indent the code blocks consistently—Python uses indentation to define where each block starts and ends. If you're new to this, start with small examples and test them in a Python environment like IDLE or an online interpreter. Let me know if you need help with a specific scenario!

---

User:
Wait, what if I have more than two options? Like, if x is greater than 10, less than 10, or equal?

---

Bot
That's a great follow-up! When you have more than two possible outcomes, you can extend the if-else structure using `elif` (short for "else if"). This allows you to check multiple conditions in sequence, and it stops at the first true condition. If none are true, it falls back to the `else` block. Here's how it works step by step:

### Key Points
- **Structure**: Start with `if` for the first condition, add `elif` for each additional condition, and end with `else` for anything that doesn't match.
- **Order matters**: Check conditions in the order that makes logical sense, as only the first true one will execute.
- **Indentation**: Keep consistent indentation (usually 4 spaces) for each code block.
- **Common pitfall**: Don't forget the colon (`:`) after each condition, and ensure your comparisons are accurate (e.g., using `==` for equality).

### Basic Syntax
```python
if condition1:
    # code for condition1
elif condition2:
    # code for condition2
elif condition3:
    # code for condition3
else:
    # code if none of the above are true
```

### Example Based on Your Scenario
Let's adapt your example where we check if `x` is greater than 10, less than 10, or exactly equal to 10:

```python
x = 10  # You can change this value to test

if x > 10:
    print("x is greater than 10")
elif x < 10:
    print("x is less than 10")
else:
    print("x is equal to 10")
```

- If `x` is 15, it prints "x is greater than 10".
- If `x` is 5, it prints "x is less than 10".
- If `x` is 10, it prints "x is equal to 10".

This handles exactly three cases, but you can add more `elif` statements as needed for additional options.

Does that make sense so far? Can you think of a similar example in your own code where you'd use if-elif-else? To practice, try writing a short script that checks a variable for multiple ranges (like age groups: child, teen, adult) and prints a message for each. Test it with different values, and let me know if you run into any issues!

---

