const db = require('../config/db');

class Enrollment {
  static create(studentId, courseId) {
    const stmt = db.prepare(
      'INSERT INTO enrollments (studentId, courseId) VALUES (?, ?)'
    );
    const result = stmt.run(studentId, courseId);
    return db.prepare('SELECT * FROM enrollments WHERE id = ?').get(result.lastInsertRowid);
  }

  static findByStudent(studentId) {
    return db.prepare(`
      SELECT e.*, c.title as courseTitle, c.subject as courseSubject, c.grade as courseGrade
      FROM enrollments e
      LEFT JOIN courses c ON e.courseId = c.id
      WHERE e.studentId = ?
    `).all(studentId);
  }

  static findUnique(studentId, courseId) {
    return db.prepare(
      'SELECT * FROM enrollments WHERE studentId = ? AND courseId = ?'
    ).get(studentId, courseId);
  }

  static getStats() {
    const total = db.prepare('SELECT COUNT(*) as count FROM enrollments').get().count;
    const active = db.prepare("SELECT COUNT(*) as count FROM enrollments WHERE status = 'ACTIVE'").get().count;
    const completed = db.prepare("SELECT COUNT(*) as count FROM enrollments WHERE status = 'COMPLETED'").get().count;
    return { total, active, completed };
  }
}

module.exports = Enrollment;
