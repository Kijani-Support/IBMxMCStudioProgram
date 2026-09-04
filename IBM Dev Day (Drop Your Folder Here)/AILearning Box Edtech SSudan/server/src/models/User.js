const db = require('../config/db');
const jwt = require('jsonwebtoken');

class User {
  static findById(id) {
    return db.prepare('SELECT id, name, email, role, grade, school, learnerId, createdAt, updatedAt FROM users WHERE id = ?').get(id);
  }

  static findByIdWithPassword(id) {
    return db.prepare('SELECT * FROM users WHERE id = ?').get(id);
  }

  static findByEmail(email) {
    return db.prepare('SELECT * FROM users WHERE email = ?').get(email);
  }

  static create({ name, email, password, role, grade, school }) {
    const stmt = db.prepare('INSERT INTO users (name, email, password, role, grade, school) VALUES (?, ?, ?, ?, ?, ?)');
    const result = stmt.run(name, email, password, role || 'STUDENT', grade || null, school || null);
    return this.findById(result.lastInsertRowid);
  }

  static generateToken(userId) {
    return jwt.sign({ id: userId }, process.env.JWT_SECRET, { expiresIn: '30d' });
  }

  static toJSON(user) {
    if (!user) return null;
    const { password, ...rest } = user;
    return rest;
  }
}

module.exports = User;
