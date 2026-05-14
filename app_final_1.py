from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import random
import re
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = 'cd6DiJZnwzNaSq9xq3MKqwbMXQoYcFtL'

def init_db():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      password TEXT NOT NULL,
                      class_name INTEGER NOT NULL CHECK (class_name IN (1, 2, 3, 4)))''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Ошибка инициализации БД: {e}")

def generate_arithmetic_task_1_2():
    operation = random.choice(['+', '-'])
    num1 = random.randint(1, 20)

    if operation == '-':
        num2 = random.randint(1, num1)
        answer = num1 - num2
    else:
        num2 = random.randint(1, 20)
        answer = num1 + num2

    task = f'{num1} {operation} {num2}'
    return task, answer

def generate_arithmetic_task_3():
    operation = random.choice(['+', '-', '*', '/'])
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 10)

    if operation == '-':
        num1, num2 = max(num1, num2), min(num1, num2)
        answer = num1 - num2
    elif operation == '/':
        if num2 == 0:
            num2 = 1
        num1 = num1 * num2
        answer = num1 // num2
    elif operation == '+':
        answer = num1 + num2
    else:  # *
        answer = num1 * num2

    task = f'{num1} {operation} {num2}'
    return task, answer

def generate_equation():
    a = random.randint(1, 10)
    b = random.randint(1, 20)

    if random.choice([True, False]):
        while b % a != 0:
            b = random.randint(1, 20)
        answer = b // a
        task = f"{a} × x = {b}"
    else:
        answer = b - a
        task = f"x + {a} = {b}"

    return task, answer

def generate_complex_task_4():
    max_attempts = 10
    for _ in range(max_attempts):
        try:
            num1 = random.randint(2, 20)
            num2 = random.randint(1, 15)
            num3 = random.randint(1, 12)
            num4 = random.randint(1, 10)
            num5 = random.randint(1, 8)

            op1 = random.choice(['+', '-'])
            op2 = random.choice(['*', '/'])
            op3 = random.choice(['+', '-'])
            op4 = random.choice(['*', '/'])

            variant = random.choice([1, 2, 3])

            if variant == 1:
                part1 = num1 + num2 if op1 == '+' else num1 - num2
                if op2 == '/' and num3 == 0:
                    num3 = 1
                part2 = part1 * num3 if op2 == '*' else part1 / num3
                if op4 == '/' and num5 == 0:
                    num5 = 1
                part3 = num4 / num5 if op4 == '/' else num4 * num5
                answer = part2 - part3 if op3 == '-' else part2 + part3
                task = f"({num1} {op1} {num2}) {op2} {num3} {op3} {num4} {op4} {num5}"

            elif variant == 2:
                if op2 == '/' and num3 == 0:
                    num3 = 1
                part1 = num2 * num3 if op2 == '*' else num2 / num3
                part2 = num1 + part1 if op1 == '+' else num1 - part1
                if op4 == '/' and num5 == 0:
                    num5 = 1
                part3 = num4 / num5 if op4 == '/' else num4 * num5
                answer = part2 - part3 if op3 == '-' else part2 + part3
                task = f"{num1} {op1} ({num2} {op2} {num3}) {op3} {num4} {op4} {num5}"
            else:
                part1 = num1 + num2 if op1 == '+' else num1 - num2
                part2 = num3 - num4 if op3 == '-' else num3 + num4
                if part2 == 0 and op2 == '/':
                    continue
                part3 = part1 * part2 if op2 == '*' else part1 / part2
                if op4 == '/' and num5 == 0:
                    num5 = 1
                answer = part3 / num5 if op4 == '/' else part3 * num5
                task = f"({num1} {op1} {num2}) {op2} ({num3} {op3} {num4}) {op4} {num5}"

            answer = round(float(answer), 2)

            if -1000 <= answer <= 1000:
                return task, answer
        except ZeroDivisionError:
            continue

    return "2 + 2", 4

def generate_equation_advanced():
    a = random.randint(2, 10)
    b = random.randint(1, 30)
    c = random.randint(b + 1, 50)

    while (c - b) % a != 0:
        c = random.randint(b + 1, 50)

    answer = (c - b) // a
    task = f"{a} × x + {b} = {c}"

    # Альтернативная версия уравнения
    if random.choice([True, False]):
        b2 = random.randint(1, 30)
        c2 = random.randint(1, 50)
        if (c2 + b2) % a == 0:
            answer = (c2 + b2) // a
            task = f"{a} × x - {b2} = {c2}"

    return task, answer

def get_tasks_for_class(class_name):
    tasks = []

    if class_name in [1, 2]:
        for i in range(5):
            task, answer = generate_arithmetic_task_1_2()
            tasks.append({
                'type': 'arithmetic',
                'task': task,
                'answer': answer,
                'number': i + 1
            })

    elif class_name == 3:
        for i in range(3):
            task, answer = generate_arithmetic_task_3()
            tasks.append({
                'type': 'arithmetic',
                'task': task,
                'answer': answer,
                'number': i + 1
            })
        for i in range(2):
            task, answer = generate_equation()
            tasks.append({
                'type': 'equation',
                'task': task,
                'answer': answer,
                'number': i + 4
            })

    elif class_name == 4:
        x = random.randint(1, 15)
        y = random.randint(1, 15)
        eq1_a = random.randint(1, 5)
        eq1_b = random.randint(1, 5)
        eq1_c = eq1_a * x + eq1_b * y

        eq2_a = random.randint(1, 5)
        eq2_b = random.randint(1, 5)
        eq2_c = eq2_a * x + eq2_b * y

        system_task = f"""Найди сумму x + y в системе уравнений:<br>
        {eq1_a}x + {eq1_b}y = {eq1_c}<br>
        {eq2_a}x + {eq2_b}y = {eq2_c}"""

        tasks.append({
            'type': 'system',
            'task': system_task,
            'answer': x + y,
            'number': 1
        })

        for i in range(2):
            task, answer = generate_complex_task_4()
            tasks.append({
                'type': 'complex',
                'task': task,
                'answer': answer,
                'number': i + 2
            })

    return tasks


@app.route('/', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    class_name = session.get('class_name')

    if 'current_tasks' not in session or session.get('regenerated', False):
        session['current_tasks'] = get_tasks_for_class(class_name)
        session['current_task_index'] = 0
        session['user_answers'] = {}
        session['regenerated'] = False
        session['score'] = session.get('score', 0)

    tasks = session['current_tasks']
    current_index = session['current_task_index']

    if current_index >= len(tasks):
        user_answers = session.get('user_answers', {})
        correct_count = 0
        results = []

        for i, task in enumerate(tasks):
            user_answer = user_answers.get(str(i))
            is_correct = False
            if user_answer is not None:
                try:
                    if abs(float(user_answer) - float(task['answer'])) < 0.01:
                        is_correct = True
                        correct_count += 1
                except:
                    pass

            results.append({
                'number': task['number'],
                'task': task['task'],
                'correct_answer': task['answer'],
                'user_answer': user_answer,
                'is_correct': is_correct,
                'type': task['type']
            })

        session['score'] = session.get('score', 0) + correct_count * 10
        session.modified = True

        return render_template('results.html',
                               username=session['username'],
                               class_name=class_name,
                               results=results,
                               total=len(tasks),
                               correct=correct_count,
                               score=session['score'])

    current_task = tasks[current_index]
    result = None

    if request.method == 'POST':
        try:
            user_answer = float(request.form.get('answer', 0))
            correct_answer = float(current_task['answer'])

            if 'user_answers' not in session:
                session['user_answers'] = {}
            session['user_answers'][str(current_index)] = user_answer

            if abs(user_answer - correct_answer) < 0.01:
                result = f"✅ Правильно! +10 очков"
                session['current_task_index'] = current_index + 1
                session.modified = True
                return redirect(url_for('home'))
            else:
                result = f"❌ Неправильно. Правильный ответ: {correct_answer}"
        except (ValueError, TypeError):
            result = "⚠️ Ошибка: введите числовой ответ"

    progress = (current_index / len(tasks)) * 100

    return render_template('home.html',
                           username=session['username'],
                           class_name=class_name,
                           current_task=current_task,
                           task_number=current_index + 1,
                           total_tasks=len(tasks),
                           progress=progress,
                           result=result,
                           score=session.get('score', 0))


@app.route('/restart')
def restart():
    if 'username' in session:
        session.pop('current_tasks', None)
        session.pop('current_task_index', None)
        session.pop('user_answers', None)
        session['regenerated'] = True
        flash('Тест перезапущен!', 'info')
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and sha256_crypt.verify(password, user[2]):
            session.clear()
            session['username'] = username
            session['class_name'] = user[3]
            session['score'] = 0
            session['regenerated'] = True
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        class_name = request.form['class_name']

        if class_name not in ['1', '2', '3', '4']:
            flash('Выберите корректный класс обучения (1, 2, 3 или 4)', 'error')
            return render_template('register.html')

        hashed_password = sha256_crypt.hash(password)

        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, class_name) VALUES (?, ?, ?)",
                      (username, hashed_password, class_name))
            conn.commit()
            conn.close()
            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Пользователь с таким именем уже существует', 'error')

    return render_template('register_1.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='localhost', port=7000)