# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- While making UML, I will come up with classes and tools the user would be able to use with PawPal+.
- User: has a name, time, preference variables.
- Pet: has a name, type, age, maybe certain conditions?
- Planner: Will generate a plan for the user
- Task: A subclass? of Planner that will store the task entered by the user. Has name, duration, priority, frequency, due date variables.
- Constraint: not sure how it would work yet, but it would have a time variable.

**b. Design changes**

- The design of PawPal changed a lot after working with the Agent. When I compared the current design with pawpal_uml.md, I noticed that the current design is much richer and has a lot of classes and their methods. Class Task, for example, now tracks Task's status and scheduled time. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- There are several constraints I added to the program. `due today`, `priority`, `time available`, `preferences`. I also listed them down in order which matters the most. `due today` matters the most because it's a task that must be completed today, regardless of priority and preferences.

**b. Tradeoffs**

- One tradeoff my scheduler makes is that it puts simplicity over realism. For example, some tasks may overlap with each other without being resolved. This tradeoff makes the code cleaner by using easier logic.

---

## 3. AI Collaboration

**a. How you used AI**

- I used AI for the vast majority of this project because my Python skills are not the best. I liked asking it logical questions and seeing how it would respond. Codex and Copilot helped me with fast coding and finding logical errors. In return, I tested the UI and found some other features I would've wanted to implement.

**b. Judgment and verification**

- When creating a UML, I originally asked GPT to write something simple. However, it did not understand the assignment, and gave me a UML that I could barely even read. Too many classes and functions. Also, when generating a skeleton, the AI basically gave me a ready code of the entire PawPal instead of structure. I had to reject it.

---

## 4. Testing and Verification

**a. What you tested**

- In the test file, I tested if the task status was correct, if Scheduler follows task priority and sorts it by time.

**b. Confidence**

- I am confident that my program runs without mistakes because it passed all the tests. 

---

## 5. Reflection

**a. What went well**

- I feel like I am satisfied with the Scheduler the most. It feels neat to me.

**b. What you would improve**

- I feel like entering each task and assigning the time would be annoying for the user. It might be simplified somehow.

**c. Key takeaway**

- One takeaway I have is that AI needs CONTEXT. It's like a hungry child that needs to be fed. UML is a good source of food when writing a code. Based on a UML, AI would be able to implement your ideas very easily.
