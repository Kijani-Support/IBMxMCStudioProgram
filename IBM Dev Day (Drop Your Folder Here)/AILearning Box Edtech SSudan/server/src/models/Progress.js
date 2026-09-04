const db = require('../config/db');

class Progress {
  static findByStudent(studentId) {
    return db.prepare(`
      SELECT p.*, c.title as courseTitle, c.subject as courseSubject, c.grade as courseGrade,
             l.title as lessonTitle
      FROM progress p
      LEFT JOIN courses c ON p.courseId = c.id
      LEFT JOIN lessons l ON p.lessonId = l.id
      WHERE p.studentId = ?
    `).all(studentId);
  }

  static findUnique(studentId, courseId, lessonId) {
    return db.prepare(
      'SELECT * FROM progress WHERE studentId = ? AND courseId = ? AND lessonId = ?'
    ).get(studentId, courseId, lessonId);
  }

  static upsert({ studentId, courseId, lessonId, completed, percentage, lastPosition, quizScore, deviceId }) {
    const existing = this.findUnique(studentId, courseId, lessonId);
    
    if (existing) {
      db.prepare(`
        UPDATE progress 
        SET completed = COALESCE(?, completed),
            percentage = COALESCE(?, percentage),
            lastPosition = COALESCE(?, lastPosition),
            quizScore = COALESCE(?, quizScore),
            deviceId = COALESCE(?, deviceId),
            updatedAt = CURRENT_TIMESTAMP
        WHERE id = ?
      `).run(
        completed !== undefined ? (completed ? 1 : 0) : null,
        percentage !== undefined ? percentage : null,
        lastPosition !== undefined ? lastPosition : null,
        quizScore !== undefined ? quizScore : null,
        deviceId || null,
        existing.id
      );
      return db.prepare('SELECT * FROM progress WHERE id = ?').get(existing.id);
    } else {
      const stmt = db.prepare(
        'INSERT INTO progress (studentId, courseId, lessonId, completed, percentage, lastPosition, quizScore, deviceId) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
      );
      const result = stmt.run(
        studentId, courseId, lessonId || null,
        completed ? 1 : 0, percentage || 0, lastPosition || 0,
        quizScore || null, deviceId || null
      );
      return db.prepare('SELECT * FROM progress WHERE id = ?').get(result.lastInsertRowid);
    }
  }

  static count() {
    return db.prepare('SELECT COUNT(*) as count FROM progress').get().count;
  }
}

module.exports = Progress;
