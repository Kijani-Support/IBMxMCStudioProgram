const db = require('../config/db');

class Course {
  static findById(id) {
    return db.prepare(`
      SELECT c.*, u.name as creatorName 
      FROM courses c 
      LEFT JOIN users u ON c.createdBy = u.id 
      WHERE c.id = ?
    `).get(id);
  }

  static findAll(filters = {}) {
    let query = `
      SELECT c.*, u.name as creatorName 
      FROM courses c 
      LEFT JOIN users u ON c.createdBy = u.id 
      WHERE 1=1
    `;
    const params = [];

    if (filters.grade) {
      query += ' AND c.grade = ?';
      params.push(filters.grade);
    }
    if (filters.subject) {
      query += ' AND c.subject = ?';
      params.push(filters.subject);
    }
    if (filters.published !== undefined) {
      query += ' AND c.published = ?';
      params.push(filters.published ? 1 : 0);
    }

    query += ' ORDER BY c.createdAt DESC';
    return db.prepare(query).all(...params);
  }

  static create({ title, description, grade, subject, thumbnail, createdBy }) {
    const stmt = db.prepare(
      'INSERT INTO courses (title, description, grade, subject, thumbnail, createdBy) VALUES (?, ?, ?, ?, ?, ?)'
    );
    const result = stmt.run(title, description, grade, subject, thumbnail || null, createdBy);
    return this.findById(result.lastInsertRowid);
  }

  static update(id, data) {
    const fields = [];
    const params = [];
    
    for (const [key, value] of Object.entries(data)) {
      if (key !== 'id' && key !== 'createdAt') {
        fields.push(`${key} = ?`);
        params.push(value);
      }
    }
    
    fields.push('version = version + 1');
    fields.push('updatedAt = CURRENT_TIMESTAMP');
    params.push(id);

    db.prepare(`UPDATE courses SET ${fields.join(', ')} WHERE id = ?`).run(...params);
    return this.findById(id);
  }

  static delete(id) {
    db.prepare('DELETE FROM courses WHERE id = ?').run(id);
  }

  static count() {
    return db.prepare('SELECT COUNT(*) as count FROM courses').get().count;
  }
}

module.exports = Course;
