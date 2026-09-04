const db = require('../config/db');

class Quiz {
  static findById(id) {
    const quiz = db.prepare('SELECT * FROM quizzes WHERE id = ?').get(id);
    if (quiz) {
      quiz.questions = JSON.parse(quiz.questions || '[]');
    }
    return quiz;
  }

  static findByLessonId(lessonId) {
    const quiz = db.prepare('SELECT * FROM quizzes WHERE lessonId = ?').get(lessonId);
    if (quiz) {
      quiz.questions = JSON.parse(quiz.questions || '[]');
    }
    return quiz;
  }

  static create({ lessonId, title, questions, passingScore }) {
    const stmt = db.prepare(
      'INSERT INTO quizzes (lessonId, title, questions, passingScore) VALUES (?, ?, ?, ?)'
    );
    const result = stmt.run(lessonId, title, JSON.stringify(questions), passingScore || 60);
    return this.findById(result.lastInsertRowid);
  }

  static count() {
    return db.prepare('SELECT COUNT(*) as count FROM quizzes').get().count;
  }
}

module.exports = Quiz;
