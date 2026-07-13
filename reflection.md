# PawPal+ Project Reflection

## 1. System Design
1. User enters basic owner + pet info
2. User add/edit tasks (duration + priority at minimum)
3. Generate a daily schedule/plan based on constraints and priorities

**a. Initial design**

- Briefly describe your initial UML design.
    - Created 4 classes. Owner, Pet, Task, Scheduler.
    - Owner has 1 --> many pets
    - Pet has 1 --> many Tasks
    - Owner uses Scheduler that schedules the pool of Tasks.

- What classes did you include, and what responsibilities did you assign to each?
    1. Owner: stores user info and constrains; owns pets
    2. Pet: represents an animal and holds a list of care tasks
    3. Task: a single activity that contains priority and duration score and whether theres enough time.
    4. Scheduler: an engine that sorts, filters, and schedules tasks into a daily plan and explains its choices.

**b. Design changes**

- Did your design change during implementation?
    - Yes my design changed
- If yes, describe at least one change and why you made it.
    1. added a Plan/ScheduleEntry output because returning a list couldn;t hold when each task runs.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    - time available, priority, duration, and each task's preferred time.
    - frequency (daily/weekly) decides which tasks come back.
- How did you decide which constraints mattered most?
    - priority and time budget mattered most since a busy owner needs the
      important stuff done and it has to fit the minutes they have. time is
      mostly used for sorting and conflict checks.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    - `generate_plan()` schedules tasks back-to-back from a single start time in
      priority order, rather than honoring each task's preferred `time`. Conflict
      detection is handled separately (`detect_conflicts()` only *warns* about
      overlapping preferred times — it does not resolve them by shifting or
      dropping a task).
- Why is that tradeoff reasonable for this scenario?
    - A busy pet owner mainly needs a realistic, prioritized to-do order that fits
      the time they have that day. Packing tasks sequentially guarantees no two
      tasks are booked at once and keeps the algorithm simple and predictable.
      Surfacing conflicts as non-fatal warnings (instead of auto-rearranging)
      keeps the owner in control and avoids the program crashing or making a
      confusing "smart" decision on their behalf.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
    - used it for pretty much every phase: brainstorming the 4 classes, making
      the mermaid UML, class stubs, the scheduling logic, tests, and debugging
      stuff like venv activation and pytest import errors.
- What kinds of prompts or questions were most helpful?
    - specific ones tied to one file or one behavior worked best. like "sort
      tasks by their time" or "why is this test failing, my test or my logic?".
      way better than vague "make it better" prompts.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
    - it wanted to put the pet filter on the Scheduler but i kept it on Owner.
      the Scheduler flattens all the tasks into one list and loses which pet is
      which, so filtering by pet only makes sense on Owner. kept it cleaner.
- How did you evaluate or verify what the AI suggested?
    - ran main.py and pytest after every change and checked the output matched
      what i expected (like the conflicting task actually shifting).

**c. AI strategy**

- Which AI coding assistant features were most effective for building your scheduler?
    - editing multiple files at once and running the code/tests right after, so
      i could actually see a feature work end to end instead of just trusting
      the diff. going step by step kept each change small.
- Give one example of an AI suggestion you rejected or modified to keep your system design clean.
    - moving the pet filter to Owner (see 3b). i also had it shift conflicting
      tasks instead of dropping them, since dropping a care task silently is
      worse than just rescheduling it.
- How did using separate chat sessions for different phases help you stay organized?
    - keeping planning in its own session away from the code kept each chat
      focused so the answers stayed on topic and i didn't mix up planning notes
      with actual code changes.
- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.
    - the AI is fast at writing code but the design calls (where a method goes,
      which tradeoff to take, if a suggestion is actually cleaner) are on me. my
      job was setting direction, verifying every change by running it, and
      pushing back when something added complexity.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
    - completion flips status, adding a task bumps the pet's count, sort_by_time
      returns things in order, completing a daily task makes the next day's
      copy, and detect_conflicts flags two tasks at the same time. 5 tests.
- Why were these tests important?
    - they cover the core logic (sorting, recurrence dates, conflicts) which is
      the stuff most likely to break quietly and hardest to check by hand.

**b. Confidence**

- How confident are you that your scheduler works correctly?
    - pretty confident, about 4/5. all 5 tests pass and the CLI demo works for
      sorting, filtering, conflicts and recurrence.
- What edge cases would you test next if you had more time?
    - a pet with no tasks, 0 minute budget, bad time strings like "25:99",
      tasks that touch but don't overlap, and resolve_conflicts output.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    - the conflict handling and recurring tasks. it doesn't just warn about
      overlaps, it shifts them, and finishing a recurring task auto-makes the
      next one.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    - i'd merge generate_plan and resolve_conflicts into one planner so there's
      only one source of truth for the schedule, and add the edge case tests.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    - splitting responsibilities across classes (data vs engine) made it easy to
      add stuff, and staying the lead architect (owning the design and running
      every change to verify it) matters more than how fast the code gets made.
