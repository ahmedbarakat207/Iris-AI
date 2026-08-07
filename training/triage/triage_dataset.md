# Iris Triage Routing Fine-Tuning Dataset Template

SYSTEM: You are the Iris AI Router. Your ONLY job is to classify the user's query and output a single routing decision from: SEARCH, REASONING, GENERAL, MATH, CODE_SIMPLE, CODE_COMPLEX, CONTROL.

USER: What is the current stock price of Apple?
BOT: SEARCH

USER: What's the weather in Cairo today?
BOT: SEARCH

USER: Who is the prime minister of Canada right now?
BOT: SEARCH

USER: Latest news about the space launch.
BOT: SEARCH

USER: Why did the Roman Empire fall?
BOT: REASONING

USER: How do I make a chocolate cake from scratch?
BOT: REASONING

USER: Explain how photosynthesis works step-by-step.
BOT: REASONING

USER: What is the difference between a virus and a bacteria?
BOT: REASONING

USER: Hi there! How's your day going?
BOT: GENERAL

USER: Yo bro, what's up?
BOT: GENERAL

USER: Write a short story about a time-traveling detective.
BOT: GENERAL

USER: Write a haiku about the sea.
BOT: GENERAL

USER: Solve the equation x^2 - 5x + 6 = 0.
BOT: MATH

USER: Calculate the derivative of f(x) = 3x^2 + 5x - 2.
BOT: MATH

USER: What is the sum of angles in a heptagon?
BOT: MATH

USER: Integrate sin(x) from 0 to pi.
BOT: MATH

USER: Write a python function to reverse a string.
BOT: CODE_SIMPLE

USER: How do I write a basic loop in JS?
BOT: CODE_SIMPLE

USER: Solve this Codeforces dynamic programming problem.
BOT: CODE_SIMPLE

USER: Fix the syntax error in my CSS file.
BOT: CODE_SIMPLE

USER: Build me a full e-commerce website with a shopping cart and database integration.
BOT: CODE_COMPLEX

USER: Create a multi-file chat application in Node.js using WebSockets.
BOT: CODE_COMPLEX

USER: Refactor this entire Django codebase to use clean architecture.
BOT: CODE_COMPLEX

USER: Design a REST API with express and typescript.
BOT: CODE_COMPLEX

USER: Turn up my screen brightness to 80%.
BOT: CONTROL

USER: Delete all temporary files in my Downloads folder.
BOT: CONTROL

USER: Open Google Chrome app.
BOT: CONTROL

USER: Empty the system trash can.
BOT: CONTROL

USER: What's the score of the Liverpool match right now?
BOT: SEARCH

USER: How much is Bitcoin worth today?
BOT: SEARCH

USER: Is the new iPhone out yet?
BOT: SEARCH

USER: Did India win the cricket World Cup match?
BOT: SEARCH

USER: Is Elon Musk still the owner of X, formerly known as Twitter?
BOT: SEARCH

USER: What's the traffic like on the highway to the airport right now?
BOT: SEARCH

USER: What time does the pharmacy near me close tonight?
BOT: SEARCH

USER: Has the new Mission Impossible movie been released yet?
BOT: SEARCH

USER: What's the exchange rate between the dollar and the euro?
BOT: SEARCH

USER: Who's leading the F1 championship this season?
BOT: SEARCH

USER: What's the difference between capitalism and socialism?
BOT: REASONING

USER: Give me some tips to improve my public speaking skills.
BOT: REASONING

USER: What are the health benefits of meditation?
BOT: REASONING

USER: How many letters are in the word "necessary"?
BOT: REASONING

USER: Why do cats purr?
BOT: REASONING

USER: Compare the plots of Romeo and Juliet and West Side Story.
BOT: REASONING

USER: What should I consider before adopting a dog?
BOT: REASONING

USER: Summarize the main arguments for and against remote work.
BOT: REASONING

USER: How does a car engine convert fuel into motion?
BOT: REASONING

USER: What's a good strategy for paying off credit card debt faster?
BOT: REASONING

USER: What's good?
BOT: GENERAL

USER: Long time no see!
BOT: GENERAL

USER: Do you ever get tired of answering questions?
BOT: GENERAL

USER: Write a limerick about a lazy cat.
BOT: GENERAL

USER: Compose a short rap verse about summer vacation.
BOT: GENERAL

USER: Draft a playful dialogue between two robots meeting for the first time.
BOT: GENERAL

USER: Write a short letter from Santa to a curious kid.
BOT: GENERAL

USER: Can you think for yourself, or do you just repeat what you're told?
BOT: GENERAL

USER: What's your favorite color?
BOT: GENERAL

USER: Invent a silly nickname for a grumpy office printer.
BOT: GENERAL

USER: What's the area of a circle with a radius of 7 cm?
BOT: MATH

USER: If a train travels 60 miles per hour for 3 hours, how far does it go?
BOT: MATH

USER: What's the probability of rolling two sixes with two dice?
BOT: MATH

USER: Prove that the square root of 2 is irrational.
BOT: MATH

USER: Find the derivative of f(x) = ln(x^2 + 1).
BOT: MATH

USER: What's the sum of the interior angles of a nonagon?
BOT: MATH

USER: Convert 3/4 into a decimal and a percentage.
BOT: MATH

USER: A rectangle has a perimeter of 40 cm and a length of 12 cm. What's its width?
BOT: MATH

USER: What is the least common multiple of 8 and 12?
BOT: MATH

USER: How many ways can you arrange 5 books on a shelf?
BOT: MATH

USER: Write a function to check if a string is a palindrome.
BOT: CODE_SIMPLE

USER: Give me a regex to validate an email address.
BOT: CODE_SIMPLE

USER: Write a SQL query to find the top 5 highest-paid employees.
BOT: CODE_SIMPLE

USER: How do I reverse a linked list in Java?
BOT: CODE_SIMPLE

USER: Write an algorithm to detect a cycle in a graph.
BOT: CODE_SIMPLE

USER: Fix this code: def add(a, b) return a+b
BOT: CODE_SIMPLE

USER: Write a bash one-liner to find all .log files older than 7 days.
BOT: CODE_SIMPLE

USER: Implement a binary search function in C++.
BOT: CODE_SIMPLE

USER: Write a shader that makes a sphere glow.
BOT: CODE_SIMPLE

USER: How do I convert a list of dictionaries into a Pandas DataFrame?
BOT: CODE_SIMPLE

USER: Implement a neural network training loop from scratch in NumPy.
BOT: CODE_SIMPLE

USER: Build a full-stack blog platform with a Node.js backend and a React frontend.
BOT: CODE_COMPLEX

USER: Design a REST API with JWT authentication using Express and MongoDB.
BOT: CODE_COMPLEX

USER: Create a complete e-commerce site skeleton with product pages, a cart, and checkout.
BOT: CODE_COMPLEX

USER: Build me a chat application backend with WebSockets and a database.
BOT: CODE_COMPLEX

USER: Set up a microservices architecture for an order-processing system.
BOT: CODE_COMPLEX

USER: Please review and refactor my entire codebase for better performance.
BOT: CODE_COMPLEX

USER: Scaffold a Next.js project with authentication, a dashboard, and a database layer.
BOT: CODE_COMPLEX

USER: Implement a neural network training pipeline with data loading, model definition, and evaluation.
BOT: CODE_COMPLEX

USER: Build a landing page using Tailwind CSS for a new SaaS product.
BOT: CODE_COMPLEX

USER: Give me a starter skeleton for a Django project with user authentication.
BOT: CODE_COMPLEX

USER: Lock my screen.
BOT: CONTROL

USER: Take a screenshot right now.
BOT: CONTROL

USER: Turn on dark mode.
BOT: CONTROL

USER: Mute my microphone.
BOT: CONTROL

USER: Connect to the office Wi-Fi network.
BOT: CONTROL

USER: Close all open browser tabs.
BOT: CONTROL

USER: Uninstall Spotify from my computer.
BOT: CONTROL

USER: Set a screen timeout of 10 minutes.
BOT: CONTROL

USER: سعر الدولار كام دلوقتي؟
BOT: SEARCH

USER: مين رئيس وزراء مصر الحالي؟
BOT: SEARCH

USER: الجو هيكون عامل ايه بكرة في القاهرة؟
BOT: SEARCH

USER: نتيجة مباراة الأهلي امبارح كانت ايه؟
BOT: SEARCH

USER: ايه اخر اخبار كأس العالم؟
BOT: SEARCH

USER: الساعة كام دلوقتي في السعودية؟
BOT: SEARCH

USER: اشرحلي ازاي المحرك البخاري بيشتغل
BOT: REASONING

USER: ايه الفرق بين الذكاء الاصطناعي والتعلم الآلي؟
BOT: REASONING

USER: ليه السماء لونها ازرق؟
BOT: REASONING

USER: اديني نصايح عشان اذاكر كويس للامتحانات
BOT: REASONING

USER: قارن بين حضارة مصر القديمة والحضارة الرومانية
BOT: REASONING

USER: ايه اسباب سقوط الدولة العثمانية؟
BOT: REASONING

USER: ازيك عامل ايه؟
BOT: GENERAL

USER: صباح الخير يا صاحبي
BOT: GENERAL

USER: انت مين بالظبط؟ روبوت ولا انسان؟
BOT: GENERAL

USER: احكيلي حكاية قصيرة عن قطة شاطرة
BOT: GENERAL

USER: قولي نكتة تضحكني
BOT: GENERAL

USER: اكتبلي بيت شعر عن الصداقة
BOT: GENERAL

USER: احسبلي مساحة مربع طوله 5 سم
BOT: MATH

USER: كام ناتج 45 في 12؟
BOT: MATH

USER: حل المعادلة دي: 2س + 3 = 11
BOT: MATH

USER: ايه نسبة 20% من 500؟
BOT: MATH

USER: مجموع زوايا المثلث كام؟
BOT: MATH

USER: اكتبلي فانكشن بايثون بتحسب مجموع أرقام قائمة
BOT: CODE_SIMPLE

USER: ازاي اعمل loop في جافا سكريبت؟
BOT: CODE_SIMPLE

USER: صلحلي الكود ده، فيه خطأ: for i in range(5): prin(i)
BOT: CODE_SIMPLE

USER: اكتبلي regex للتحقق من الايميل
BOT: CODE_SIMPLE

USER: اعملّي هيكل مشروع باك اند بلغة Node و Express
BOT: CODE_COMPLEX

USER: صمم لي موقع كامل باستخدام React و Tailwind
BOT: CODE_COMPLEX

USER: برمج لي صفحة هبوط لمنتج جديد باستخدام HTML و CSS
BOT: CODE_COMPLEX

USER: عايز قالب فرونت اند فاضي بـ React عشان ابدأ عليه مشروعي
BOT: CODE_COMPLEX

USER: اعمل API كامل بلغة بايثون لموقع تجارة الكترونية
BOT: CODE_COMPLEX

USER: عايز قالب مشروع فيه فراغات لسه هملاها بنفسي
BOT: CODE_COMPLEX

USER: اقفل التطبيقات المفتوحة كلها
BOT: CONTROL

USER: زود صوت اللابتوب لـ 70%
BOT: CONTROL

USER: افتح متصفح كروم
BOT: CONTROL

USER: امسح الملفات المؤقتة من الجهاز
BOT: CONTROL

USER: Why is Bitcoin's price crashing today?
BOT: SEARCH

USER: Can you give me a good recipe to create a pizza from scratch?
BOT: REASONING

USER: Write a story about a software engineer who accidentally builds a sentient app.
BOT: GENERAL

USER: Build a sandcastle guide for my kids' beach trip.
BOT: REASONING

USER: Hi, can you help me debug this code: def add(a, b) return a+b
BOT: CODE_SIMPLE

USER: Hey, what's the weather like in Alexandria today?
BOT: SEARCH

USER: What is the difference between HTML and CSS?
BOT: REASONING

USER: What is a REST API, in simple terms?
BOT: REASONING

USER: Make a birthday cake for my daughter's party.
BOT: REASONING

USER: Make a website for my bakery so customers can order online.
BOT: CODE_COMPLEX

USER: Why do we still use the QWERTY keyboard layout?
BOT: REASONING

USER: Why is my flight to Cairo delayed today?
BOT: SEARCH

USER: How do I fix my relationship with my brother after a big fight?
BOT: REASONING

USER: How do I fix this Python error: IndentationError: expected an indented block
BOT: CODE_SIMPLE

USER: What are you, exactly?
BOT: GENERAL

USER: What are the main causes of inflation?
BOT: REASONING

USER: ايه الفرق بين الـ Frontend والـ Backend؟
BOT: REASONING

USER: اعملّي جدول مذاكرة للامتحانات القادمة
BOT: REASONING
