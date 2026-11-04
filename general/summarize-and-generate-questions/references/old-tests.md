# Old tests and LMS quizzes

## Old tests from the same lecture steer the question set

When old tests, exams, mock exams or quizzes **from the same lecture** exist
(same course, ideally same lecturer – ask which ones count, never assume),
the questions follow them: they show what this lecturer actually asks, which
beats every default.

1. **Transcribe every old test completely** (task text, points, sub-tasks,
   given solutions or marks) into `<work>/text/`, photos and scans too.
2. **Analyse** into `<work>/text/exam_analysis.md`: topics (frequency,
   points), task types (calculate, convert, define, explain, prove, read or
   write code, draw, MC), phrasing, tasks that recur across tests, difficulty,
   length and structure (tasks, sub-questions, points, time).
3. **Weight the set like the tests:** topic shares follow points/frequency;
   most questions use the tests' task types and phrasing. Every recurring task
   gets several variants with new, computed values. Topics never asked still
   get questions, but fewer – unless marked exam-relevant (★).
4. **Mock exams copy the real structure:** same number of tasks, sub-question
   types, point split and order. Include the original tasks as their own
   block; recompute their solutions, or solve missing ones (marked as Claude's,
   checked).
5. **Summary:** flag the sections old tests asked about (e.g. „in old test
   2024, task 3“ in the material's language) so the user learns those first.
6. **Reply:** which tests were used, the topic/type weights taken from them,
   and where the set deviates and why.

## Practice quizzes in a login-gated LMS (ilias, Moodle)

When sample questions sit behind a login and the page is open in the user's
browser, read it as text instead of screenshots (exact and cheap).

- Safari: the user enables Settings > Advanced > "Show features for web
  developers", then Develop > "Allow JavaScript from Apple Events". Then
  `osascript -e 'tell application "Safari" to do JavaScript "document.body.innerText" in tab N of window 1'`
  (list tabs with `get {name, URL} of every tab of every window`). Chrome with
  the Claude-in-Chrome extension works too.
- Only read. Open extra pages in a **new tab** and close it afterwards. Never
  click "Finish/Submit test". Starting a new test pass is an action in the
  user's account – ask first.
- ilias: a finished pass's "Detailed Results" lists questions and types
  (Kprim, Single Answer, Formula, Matching, Cloze); unstarted tests need
  "Start Test", then each question is at
  `…&cmd=showQuestion&sequence=N&active_id=…`.
- Transcribe everything into `<work>/text/<lms>_quizzes.md` (mark solutions you
  derived as Claude's) and treat them like old tests. Remind the user they can
  switch the Safari setting off again.
