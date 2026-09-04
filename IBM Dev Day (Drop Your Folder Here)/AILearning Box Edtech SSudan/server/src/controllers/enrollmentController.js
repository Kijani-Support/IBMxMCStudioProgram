const Enrollment = require('../models/Enrollment');

exports.enroll = async (req, res) => {
  try {
    const { courseId } = req.body;

    const existing = Enrollment.findUnique(req.user.id, courseId);
    if (existing) {
      return res.status(400).json({ message: 'Already enrolled' });
    }

    const enrollment = Enrollment.create(req.user.id, courseId);
    res.status(201).json(enrollment);
  } catch (error) {
    res.status(500).json({ message: 'Enrollment failed', error: error.message });
  }
};

exports.getEnrollments = async (req, res) => {
  try {
    const enrollments = Enrollment.findByStudent(req.user.id);
    res.json(enrollments);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch enrollments', error: error.message });
  }
};

exports.getEnrollmentStats = async (req, res) => {
  try {
    const stats = Enrollment.getStats();
    res.json(stats);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch stats', error: error.message });
  }
};
