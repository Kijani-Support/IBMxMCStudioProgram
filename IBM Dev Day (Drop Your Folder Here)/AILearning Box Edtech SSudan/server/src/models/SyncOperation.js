const db = require('../config/db');

class SyncOperation {
  static create({ deviceId, userId, operationType, payload, status }) {
    const stmt = db.prepare(
      'INSERT INTO sync_operations (deviceId, userId, operationType, payload, status) VALUES (?, ?, ?, ?, ?)'
    );
    const result = stmt.run(deviceId, userId, operationType, JSON.stringify(payload), status || 'PENDING');
    return db.prepare('SELECT * FROM sync_operations WHERE id = ?').get(result.lastInsertRowid);
  }

  static findByUser(userId, lastSync) {
    let query = 'SELECT * FROM sync_operations WHERE userId = ?';
    const params = [userId];
    
    if (lastSync) {
      query += ' AND createdAt > ?';
      params.push(lastSync);
    }
    
    query += ' ORDER BY createdAt DESC LIMIT 100';
    return db.prepare(query).all(...params).map(op => ({
      ...op,
      payload: JSON.parse(op.payload)
    }));
  }

  static markProcessed(id) {
    db.prepare(
      "UPDATE sync_operations SET status = 'PROCESSED', processedAt = CURRENT_TIMESTAMP WHERE id = ?"
    ).run(id);
  }

  static markFailed(id) {
    db.prepare(
      "UPDATE sync_operations SET status = 'FAILED' WHERE id = ?"
    ).run(id);
  }

  static count() {
    return db.prepare('SELECT COUNT(*) as count FROM sync_operations').get().count;
  }
}

module.exports = SyncOperation;
