const SyncOperation = require('../models/SyncOperation');
const Progress = require('../models/Progress');

exports.sync = async (req, res) => {
  try {
    const { deviceId, lastSync, operations } = req.body;

    let synced = 0;
    let failed = 0;

    for (const op of operations) {
      try {
        if (op.type === 'LESSON_PROGRESS') {
          Progress.upsert({
            studentId: req.user.id,
            courseId: op.courseId,
            lessonId: op.lessonId,
            completed: op.completed,
            percentage: op.percentage,
            lastPosition: op.lastPosition,
            quizScore: op.quizScore,
            deviceId
          });
          synced++;
        } else if (op.type === 'QUIZ_RESULT') {
          Progress.upsert({
            studentId: req.user.id,
            courseId: op.courseId,
            lessonId: op.lessonId,
            quizScore: op.score,
            completed: true,
            percentage: 100,
            deviceId
          });
          synced++;
        }

        SyncOperation.create({
          deviceId,
          userId: req.user.id,
          operationType: op.type,
          payload: op,
          status: 'PROCESSED'
        });
      } catch (error) {
        failed++;
        SyncOperation.create({
          deviceId,
          userId: req.user.id,
          operationType: op.type,
          payload: op,
          status: 'FAILED'
        });
      }
    }

    res.json({
      success: true,
      synced,
      failed,
      serverTime: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ message: 'Sync failed', error: error.message });
  }
};

exports.getChanges = async (req, res) => {
  try {
    const { lastSync } = req.query;
    const changes = SyncOperation.findByUser(req.user.id, lastSync);
    res.json(changes);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch changes', error: error.message });
  }
};
