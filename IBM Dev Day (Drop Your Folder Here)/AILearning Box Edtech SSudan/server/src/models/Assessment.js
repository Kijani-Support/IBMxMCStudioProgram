const db = require('../config/db');

class Assessment {
  static create({ studentId, courseId, type, questions, answers, score }) {
    const stmt = db.prepare(
      'INSERT INTO assessments (studentId, courseId, type, questions, answers, score) VALUES (?, ?, ?, ?, ?, ?)'
    );
    const result = stmt.run(studentId, courseId, type || 'diagnostic', JSON.stringify(questions), JSON.stringify(answers || {}), score || 0);
    return db.prepare('SELECT * FROM assessments WHERE id = ?').get(result.lastInsertRowid);
  }

  static findByStudent(studentId) {
    return db.prepare(`
      SELECT a.*, c.title as courseTitle, c.subject as courseSubject
      FROM assessments a
      LEFT JOIN courses c ON a.courseId = c.id
      WHERE a.studentId = ?
      ORDER BY a.createdAt DESC
    `).all(studentId).map(a => ({
      ...a,
      questions: JSON.parse(a.questions),
      answers: JSON.parse(a.answers)
    }));
  }

  static findLatestByStudentAndCourse(studentId, courseId) {
    const a = db.prepare(
      'SELECT * FROM assessments WHERE studentId = ? AND courseId = ? ORDER BY createdAt DESC LIMIT 1'
    ).get(studentId, courseId);
    if (a) {
      a.questions = JSON.parse(a.questions);
      a.answers = JSON.parse(a.answers);
    }
    return a;
  }

  static count() {
    return db.prepare('SELECT COUNT(*) as count FROM assessments').get().count;
  }
}

module.exports = Assessment;
