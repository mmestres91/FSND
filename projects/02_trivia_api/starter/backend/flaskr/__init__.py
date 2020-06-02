import os, jsons
from flask import Flask, request, abort, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r"/api/*": {"origins": "*"}})
  
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control_Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control_Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response


  @app.route('/categories', methods=['GET'])
  def get_category():
    result = Category.query.all()
    categories = {}
    for category in result:
      categories.update({category.id: category.type})
    return jsonify({
      'success': True,
      'categories': categories
      })

  

  @app.route('/questions', methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10
    questions = Question.query.all()
    result = Category.query.all()
    categories = {}
    for category in result:
      categories.update({category.id: category.type})
    formatted_questions = [question.format() for question in questions]

    return jsonify({
      'success': True,
      'questions': formatted_questions[start:end],
      'total_questions': len(questions),
      'categories': categories
    })


  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_questions(question_id):
    try:
      question = Question.query.get(question_id)
      Question.delete(question)
    except Exception:
      db.session.rollback()
    finally:
      db.session.close()
    return jsonify({
      "sucess": True
    })
  

  @app.route('/questions/create', methods=['POST'])
  def add_question():
    try:
      question = request.get_json()['question']
      answer = request.get_json()['answer']
      difficulty = request.get_json()['difficulty']
      category = request.get_json()['category']
      newquestion = Question(question=question, answer=answer, category=category, difficulty=difficulty)
      newquestion.insert()
    except Exception:
      db.session.rollback()
    finally:
      db.session.close()
    return jsonify({
      "sucess": True
    })
 

  @app.route('/search/questions',  methods=['POST'])
  def search_question():
    search = request.get_json()['searchTerm']
    question_query = Question.query.filter(Question.question.ilike('%{}%'.format(search)))
    formatted_questions = [question.format() for question in question_query]
    return jsonify({
      "success": True,
      "questions": formatted_questions,
      "total_questions": len(formatted_questions)
    })


  @app.route('/categories/<category_id>/questions', methods=['GET'])
  def getbycategory(category_id):
    filtered_category = Question.query.filter_by(category=category_id)
    formatted_category = [category.format() for category in filtered_category]
    return jsonify({
      "success": True,
      "questions": formatted_category,
      "total_questions": len(formatted_category)
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def quiz():
    category = request.get_json()['quiz_category']
    filtered = Question.query.filter_by(category=category['id'])
    formatted_category = [category.format() for category in filtered]
    return jsonify({
      "success": True,
      "question": formatted_category
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    