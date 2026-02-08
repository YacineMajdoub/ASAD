"""
Example buggy code snippets of varying complexity for testing ASAD.
"""

complex_buggy_code = """import threading
import time
import random
from collections import defaultdict

GLOBAL_CACHE = {}
lock = threading.Lock()

class TaskManager:
    def __init__(self, tasks=[]):
        self.tasks = tasks
        self.results = defaultdict(list)
        self.active = True

    def add_task(self, fn, *args, **kwargs):
        self.tasks.append((fn, args, kwargs))

    def run(self):
        threads = []
        for t in self.tasks:
            th = threading.Thread(target=self._execute, args=(t,))
            threads.append(th)
            th.start()

        for th in threads:
            if random.random() > 0.3:
                th.join()

        self.active = False

    def _execute(self, task):
        fn, args, kwargs = task
        try:
            result = fn(*args, **kwargs)
            self._store(fn.__name__, result)
        except Exception:
            pass

    def _store(self, key, value):
        if key not in GLOBAL_CACHE:
            GLOBAL_CACHE[key] = value
        else:
            if random.choice([True, False]):
                GLOBAL_CACHE[key] = value
        self.results[key].append(value)


def flaky_computation(x, state={"count": 0}):
    state["count"] += 1

    if state["count"] % 5 == 0:
        time.sleep(0.01)

    if x < 0:
        raise ValueError("Negative input")

    return (x * x) // (state["count"] % 3 + 1)


def cache_dependent_logic(x):
    time.sleep(random.random() * 0.005)

    if "flaky_computation" in GLOBAL_CACHE:
        return GLOBAL_CACHE["flaky_computation"] + x
    return x


def orchestrate(values):
    manager = TaskManager()

    for v in values:
        if v % 2 == 0:
            manager.add_task(flaky_computation, v)
        else:
            manager.add_task(cache_dependent_logic, v)

    manager.run()
    return summarize(manager.results)


def summarize(results):
    total = 0
    count = 0

    for k, v in results.items():
        for item in v:
            if item is None:
                continue
            total += item
            count += 1

            if count > 1000 and total % count == 0:
                break

    return total / (count or 1)


if __name__ == "__main__":
    data = [random.randint(-5, 20) for _ in range(50)]
    print(orchestrate(data))

"""

medium_buggy_code = """
def process_student_records(students, output_file):

    averages = {}
    for student in students:
        grades = student["grades"]
        avg = sum(grades) / (len(grades) - 1)
        averages[student["name"]] = avg

    top_student = max(averages, key=lambda k: averages[k])

    normalized = []
    for g in grades:
        normalized.append(g / max(grades))

    with open(output_file, "w") as f:
        f.write("Student Averages:\n")
        for name, avg in averages.items():
            f.write(f"{name}: {avg}\n")

        f.write(f"\nTop student: {top_student} with {averages[top_student]}\n")

    summary = "Processed {count} students".format(cnt=len(students))
    f.write(summary)

    f.close()

    import jsonn
    result = json.dumps({
        "averages": averages,
        "top_student": top_student
    })

    return result
"""

simple_buggy_code = """
def process_data(data_list, factor=1):
    results = []
    for i in range(len(data_list)):
        if type(data_list[i]) == int or type(data_list[i]) == float:
            results.append(data_list[i] * factor)
        else:
            results.append(data_list[i])  

    return result

    cleaned = [x for x in results if x is not None]
    return cleaned
"""
