from flask import (Flask, redirect, render_template, 
                request, session, url_for, jsonify)
from models import db, User, Question, Quiz, db_add_new_data

import os
from random import shuffle


BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'db', 'db_quiz.db')


html_config = {
    'admin':True,
    'debug':False
}


app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SECRET_KEY'] = 'secretkeysecretkeysecretkey1212121'

db.init_app(app)


with app.app_context():
    db_add_new_data()


@app.route('/', methods = ['GET'])
def all_quizes():
    quizes = Quiz.query.all()
    questions = Question.query.all()
    return render_template('index.html', html_config = html_config, quizes = quizes,
                           questions = questions)


@app.route('/quiz/', methods = ['POST', 'GET'])
def view_quiz():
    if request.method == 'GET':
        session['quiz_id'] = -1
        quizes = Quiz.query.all()
        return render_template('start.html', quizes=quizes, html_config = html_config)
    session['quiz_id'] = request.form.get('quiz')
    session['question_n'] = 0
    session['question_id'] = 0
    session['right_answers'] = 0
    return redirect(url_for('view_question'))


@app.route('/question/', methods = ['POST', 'GET'])
def view_question():

    if not session['quiz_id'] or session['quiz_id'] == -1:
        return redirect(url_for('view_quiz'))

    if request.method == 'POST':        
        question = Question.query.filter_by(id=session['question_id']).one()
        if question.answer == request.form.get('ans_text'):
            session['right_answers'] += 1
        session['question_n'] += 1


    quiz = Quiz.query.filter_by(id = session['quiz_id']).one()

    if int(session['question_n']) >= len(quiz.question):
        session['quiz_id'] = -1
        return redirect(url_for('view_result'))

    else:
        question = quiz.question[session['question_n']]
        session['question_id'] = question.id
        answers = [question.answer, question.wrong1, question.wrong2, question.wrong3 ]
        shuffle(answers)

        return render_template('question.html', 
                               answers=answers, 
                               question=question, 
                               html_config=html_config)


@app.route('/result/')
def view_result():
    return render_template('result.html', 
                    right=session['right_answers'], 
                    total=session['question_n'],
                    html_config=html_config)


@app.route('/editor/', methods = ['POST', 'GET'])
def editor():
    if request.method == 'GET':
        session['quiz_id'] = -1
        quizes = Quiz.query.all()
        questions = Question.query.all()
        return render_template('editor.html', html_config = html_config, quizes = quizes, questions = questions)
    else:
        quiz = request.form.get('quiz')
        question = request.form.get('question')
        answer = request.form.get('answer')
        wrong1 = request.form.get('wrong1')
        wrong2 = request.form.get('wrong2')
        wrong3 = request.form.get('wrong3')
        if quiz != None:
            user1 = User(name='user1')
            quiz = Quiz(f'{quiz}', user1)
            db.session.add(quiz)
            db.session.commit()
            return redirect(url_for('editor'))
        if question != None:
            question = Question(f'{question}', f'{answer}', f'{wrong1}',
                                f'{wrong2}', f'{wrong3}')
            db.session.add(question )
            db.session.commit()
            return redirect(url_for('editor'))
        quizes = Quiz.query.all()
        questions = Question.query.all()
        return render_template('editor.html', html_config = html_config, quizes = quizes,
                               questions = questions)


@app.route('/quiz_editor/', methods = ['POST', 'GET'])
def quiz_editor():
    if request.method == 'POST':
        quiz_id = request.form.get('quiz_id')
        if not quiz_id:
            return redirect(url_for('editor'))

        session['quiz_id'] = quiz_id

        new_quiz = request.form.get('new_quiz')

        if new_quiz:
            quiz = Quiz.query.filter_by(id=quiz_id).first()
            if not quiz:
                return redirect(url_for('editor'))

            quiz.name = new_quiz
            db.session.commit()

        return redirect(url_for('quiz_editor'))

    if request.method == 'GET':
        quiz_id = session.get('quiz_id')

        if not quiz_id or quiz_id == "-1":
            return redirect(url_for('editor'))

        quiz = Quiz.query.filter_by(id=quiz_id).first()

        if quiz is None:
            return redirect(url_for('editor'))

        question_quiz = quiz.question
        questions = Question.query.all()
        return render_template('quiz_editor.html', html_config=html_config, quiz=quiz, question_quiz=question_quiz, questions=questions)


@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if quiz:
        db.session.delete(quiz)
        db.session.commit()
    return redirect(url_for('editor'))


@app.route('/toggle_question', methods=['POST'])
def toggle_question():
    question_id = int(request.form.get('question_id'))
    quiz_id = int(session.get('quiz_id', -1))
    if quiz_id == -1:
        return redirect(url_for('editor'))

    quiz = Quiz.query.get(quiz_id)
    question = Question.query.get(question_id)

    if quiz and question:
        if question in quiz.question:
            quiz.question.remove(question)
        else:
            quiz.question.append(question)
        db.session.commit()

    return redirect(url_for('quiz_editor'))


@app.route('/question_editor/', methods = ['POST', 'GET'])
def question_editor():
    if request.method == 'POST':
        question_id = request.form.get('question_id')
        print(question_id)
        if not question_id:
            return redirect(url_for('editor'))

        q = db.session.query(Question).get(question_id)

        q.question = request.form.get("question_new") or q.question
        q.answer = request.form.get("answer_new") or q.answer
        q.wrong1 = request.form.get("wrong1_new") or q.wrong1
        q.wrong2 = request.form.get("wrong2_new") or q.wrong2
        q.wrong3 = request.form.get("wrong3_new") or q.wrong3

        db.session.commit()

        session['question_id'] = question_id

        return redirect(url_for('question_editor'))

    if request.method == 'GET':
        question_id = session.get('question_id')
        if not question_id or question_id == "-1":
            return redirect(url_for('editor'))

        question = db.session.query(Question).get(int(question_id))
        if question is None:
            return redirect(url_for('editor'))

        return render_template('question_editor.html', html_config=html_config, question=question)


@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    question = db.session.query(Question).get(question_id)
    if question:
        db.session.delete(question)
        db.session.commit()
    return redirect(url_for('question_editor'))


app.run(debug=True)