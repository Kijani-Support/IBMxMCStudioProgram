const Progress = require('../models/Progress');
const db = require('../config/db');

exports.getProgress = async (req, res) => {
  try {
    const progress = Progress.findByStudent(req.user.id);
    res.json(progress);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch progress', error: error.message });
  }
};

exports.updateProgress = async (req, res) => {
  try {
    const { courseId, lessonId, completed, percentage, lastPosition, quizScore, deviceId } = req.body;

    const progress = Progress.upsert({
      studentId: req.user.id,
      courseId,
      lessonId,
      completed,
      percentage,
      lastPosition,
      quizScore,
      deviceId
    });

    res.json(progress);
  } catch (error) {
    res.status(500).json({ message: 'Failed to update progress', error: error.message });
  }
};

exports.getCourseProgress = async (req, res) => {
  try {
    const { courseId } = req.params;
    const studentId = req.user.id;

    const lessons = db.prepare('SELECT id, title, "order" FROM lessons WHERE courseId = ? ORDER BY "order"').all(courseId);
    const progress = db.prepare('SELECT * FROM progress WHERE studentId = ? AND courseId = ?').all(studentId, courseId);
    const course = db.prepare('SELECT id, title, subject, grade FROM courses WHERE id = ?').get(courseId);

    const totalLessons = lessons.length;
    const completedLessons = progress.filter(p => p.completed).length;
    const overallPercentage = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0;

    const quizScores = progress.filter(p => p.quizScore != null).map(p => p.quizScore);
    const avgQuizScore = quizScores.length > 0 ? Math.round(quizScores.reduce((a, b) => a + b, 0) / quizScores.length) : null;

    const lessonDetails = lessons.map(lesson => {
      const p = progress.find(pr => pr.lessonId === lesson.id);
      return {
        lessonId: lesson.id,
        title: lesson.title,
        order: lesson.order,
        completed: p ? !!p.completed : false,
        percentage: p ? p.percentage : 0,
        quizScore: p ? p.quizScore : null
      };
    });

    res.json({
      course,
      totalLessons,
      completedLessons,
      overallPercentage,
      avgQuizScore,
      lessons: lessonDetails
    });
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch course progress', error: error.message });
  }
};

exports.getAllCourseProgress = async (req, res) => {
  try {
    const studentId = req.user.id;

    const enrolledCourses = db.prepare(`
      SELECT c.id, c.title, c.subject, c.grade, c.description
      FROM courses c
      WHERE c.published = 1
    `).all();

    const courseProgress = enrolledCourses.map(course => {
      const lessons = db.prepare('SELECT id FROM lessons WHERE courseId = ?').all(course.id);
      const progress = db.prepare('SELECT * FROM progress WHERE studentId = ? AND courseId = ?').all(studentId, course.id);

      const totalLessons = lessons.length;
      const completedLessons = progress.filter(p => p.completed).length;
      const overallPercentage = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0;

      const quizScores = progress.filter(p => p.quizScore != null).map(p => p.quizScore);
      const avgQuizScore = quizScores.length > 0 ? Math.round(quizScores.reduce((a, b) => a + b, 0) / quizScores.length) : null;

      const lastActivity = progress.length > 0
        ? progress.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))[0].updatedAt
        : null;

      return {
        courseId: course.id,
        title: course.title,
        subject: course.subject,
        grade: course.grade,
        totalLessons,
        completedLessons,
        overallPercentage,
        avgQuizScore,
        lastActivity
      };
    });

    res.json(courseProgress);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch course progress', error: error.message });
  }
};
