const db = require('../config/db');

exports.getStudentReport = async (req, res) => {
  try {
    const { studentId } = req.params;

    const student = db.prepare('SELECT id, name, email, grade, school FROM users WHERE id = ?').get(studentId);
    if (!student) return res.status(404).json({ message: 'Student not found' });

    const courses = db.prepare('SELECT id, title, subject, grade FROM courses WHERE published = 1').all();

    const courseReports = courses.map(course => {
      const lessons = db.prepare('SELECT id, title, "order", duration FROM lessons WHERE courseId = ? ORDER BY "order"').all(course.id);
      const progress = db.prepare('SELECT * FROM progress WHERE studentId = ? AND courseId = ?').all(studentId, course.id);

      const totalLessons = lessons.length;
      const completedLessons = progress.filter(p => p.completed).length;
      const overallPercentage = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0;

      const quizScores = progress.filter(p => p.quizScore != null);
      const avgQuizScore = quizScores.length > 0
        ? Math.round(quizScores.reduce((a, p) => a + p.quizScore, 0) / quizScores.length)
        : null;

      const weakTopics = lessons.filter(lesson => {
        const p = progress.find(pr => pr.lessonId === lesson.id);
        return p && p.quizScore != null && p.quizScore < 60;
      });

      const strongTopics = lessons.filter(lesson => {
        const p = progress.find(pr => pr.lessonId === lesson.id);
        return p && p.quizScore != null && p.quizScore >= 80;
      });

      const lessonDetails = lessons.map(lesson => {
        const p = progress.find(pr => pr.lessonId === lesson.id);
        return {
          lessonId: lesson.id,
          title: lesson.title,
          order: lesson.order,
          duration: lesson.duration,
          completed: p ? !!p.completed : false,
          percentage: p ? p.percentage : 0,
          quizScore: p ? p.quizScore : null,
          attempts: p ? (p.attempts || 1) : 0,
          lastActivity: p ? p.updatedAt : null
        };
      });

      const recommendations = [];
      if (weakTopics.length > 0) {
        recommendations.push(`Needs review: ${weakTopics.map(t => t.title).join(', ')}`);
      }
      if (completedLessons === totalLessons && totalLessons > 0) {
        recommendations.push('Course completed — ready for advanced material');
      } else if (completedLessons === 0) {
        recommendations.push('Has not started this course — encourage engagement');
      }
      if (avgQuizScore != null && avgQuizScore < 60) {
        recommendations.push('Low quiz scores — consider one-on-one tutoring');
      } else if (avgQuizScore != null && avgQuizScore >= 80) {
        recommendations.push('Strong performance — consider enrichment activities');
      }

      return {
        courseId: course.id,
        title: course.title,
        subject: course.subject,
        grade: course.grade,
        totalLessons,
        completedLessons,
        overallPercentage,
        avgQuizScore,
        weakTopics: weakTopics.map(t => t.title),
        strongTopics: strongTopics.map(t => t.title),
        lessons: lessonDetails,
        recommendations
      };
    });

    const totalCompleted = courseReports.reduce((a, c) => a + c.completedLessons, 0);
    const totalLessons = courseReports.reduce((a, c) => a + c.totalLessons, 0);
    const allQuizScores = courseReports.filter(c => c.avgQuizScore != null).map(c => c.avgQuizScore);
    const overallAvg = allQuizScores.length > 0 ? Math.round(allQuizScores.reduce((a, b) => a + b, 0) / allQuizScores.length) : null;

    const allWeak = courseReports.flatMap(c => c.weakTopics);
    const allStrong = courseReports.flatMap(c => c.strongTopics);

    const overallRecommendations = [];
    if (allWeak.length > 0) overallRecommendations.push(`Focus areas: ${allWeak.join(', ')}`);
    if (allStrong.length > 0) overallRecommendations.push(`Strengths: ${allStrong.join(', ')}`);
    if (totalCompleted === totalLessons && totalLessons > 0) overallRecommendations.push('All courses completed — ready for next level');
    if (overallAvg !== null && overallAvg < 60) overallRecommendations.push('Overall performance is below passing — immediate intervention recommended');
    if (overallAvg !== null && overallAvg >= 80) overallRecommendations.push('Excellent performance across courses');

    res.json({
      student,
      summary: {
        totalCourses: courseReports.length,
        totalLessons,
        completedLessons: totalCompleted,
        overallPercentage: totalLessons > 0 ? Math.round((totalCompleted / totalLessons) * 100) : 0,
        overallAvgQuizScore: overallAvg,
        weakAreas: allWeak,
        strongAreas: allStrong
      },
      courses: courseReports,
      overallRecommendations
    });
  } catch (error) {
    res.status(500).json({ message: 'Failed to generate student report', error: error.message });
  }
};

exports.getAllStudentsReport = async (req, res) => {
  try {
    const students = db.prepare("SELECT id, name, email, grade, school FROM users WHERE role = 'STUDENT'").all();

    const reports = students.map(student => {
      const courses = db.prepare('SELECT id, title, subject FROM courses WHERE published = 1').all();

      const courseData = courses.map(course => {
        const lessons = db.prepare('SELECT id FROM lessons WHERE courseId = ?').all(course.id);
        const progress = db.prepare('SELECT * FROM progress WHERE studentId = ? AND courseId = ?').all(student.id, course.id);

        const totalLessons = lessons.length;
        const completedLessons = progress.filter(p => p.completed).length;
        const overallPercentage = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0;

        const quizScores = progress.filter(p => p.quizScore != null).map(p => p.quizScore);
        const avgQuizScore = quizScores.length > 0 ? Math.round(quizScores.reduce((a, b) => a + b, 0) / quizScores.length) : null;

        return {
          courseId: course.id,
          title: course.title,
          subject: course.subject,
          totalLessons,
          completedLessons,
          overallPercentage,
          avgQuizScore
        };
      });

      const totalCompleted = courseData.reduce((a, c) => a + c.completedLessons, 0);
      const totalLessons = courseData.reduce((a, c) => a + c.totalLessons, 0);
      const quizAvgs = courseData.filter(c => c.avgQuizScore != null).map(c => c.avgQuizScore);
      const overallAvg = quizAvgs.length > 0 ? Math.round(quizAvgs.reduce((a, b) => a + b, 0) / quizAvgs.length) : null;

      return {
        student,
        overallPercentage: totalLessons > 0 ? Math.round((totalCompleted / totalLessons) * 100) : 0,
        overallAvgQuizScore: overallAvg,
        courses: courseData
      };
    });

    res.json(reports);
  } catch (error) {
    res.status(500).json({ message: 'Failed to generate reports', error: error.message });
  }
};
