const db = require('../config/db');

class Lesson {
  static findById(id) {
    const lesson = db.prepare('SELECT * FROM lessons WHERE id = ?').get(id);
    if (lesson) {
      lesson.documents = JSON.parse(lesson.documents || '[]');
    }
    return lesson;
  }

  static findByCourseId(courseId) {
    const lessons = db.prepare('SELECT * FROM lessons WHERE courseId = ? ORDER BY "order"').all(courseId);
    return lessons.map(l => ({
      ...l,
      documents: JSON.parse(l.documents || '[]')
    }));
  }

  static create({ courseId, title, description, content, video, audio, documents, order, duration }) {
    const stmt = db.prepare(
      'INSERT INTO lessons (courseId, title, description, content, video, audio, documents, "order", duration) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
    );
    const result = stmt.run(
      courseId, title, description || null, content, 
      video || null, audio || null, 
      JSON.stringify(documents || []), order, duration || 0
    );
    return this.findById(result.lastInsertRowid);
  }

  static update(id, data) {
    const fields = [];
    const params = [];
    
    for (const [key, value] of Object.entries(data)) {
      if (key !== 'id' && key !== 'createdAt') {
        if (key === 'documents') {
          fields.push(`${key} = ?`);
          params.push(JSON.stringify(value));
        } else {
          fields.push(`${key} = ?`);
          params.push(value);
        }
      }
    }
    
    fields.push('updatedAt = CURRENT_TIMESTAMP');
    params.push(id);

    db.prepare(`UPDATE lessons SET ${fields.join(', ')} WHERE id = ?`).run(...params);
    return this.findById(id);
  }

  static count() {
    return db.prepare('SELECT COUNT(*) as count FROM lessons').get().count;
  }
}

module.exports = Lesson;
