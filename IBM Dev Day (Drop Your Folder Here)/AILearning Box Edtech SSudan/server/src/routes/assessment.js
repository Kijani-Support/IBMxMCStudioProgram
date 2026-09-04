const express = require('express');
const router = express.Router();
const { auth } = require('../middleware/auth');
const Assessment = require('../models/Assessment');
const { generateDiagnostic, analyzeResults, generateLearningPath, topicSkills } = require('../services/assessmentEngine');

router.get('/courses', auth, (req, res) => {
  try {
    const courses = Object.keys(topicSkills).map(title => ({
      title,
      topics: topicSkills[title].topics.map(t => ({ id: t.id, name: t.name })),
      questionCount: topicSkills[title].diagnosticQuestions.length
    }));
    res.json(courses);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch courses', error: error.message });
  }
});

router.get('/diagnostic/:courseTitle', auth, (req, res) => {
  try {
    const questions = generateDiagnostic(req.params.courseTitle);
    if (!questions) {
      return res.status(404).json({ message: 'No assessment available for this course' });
    }
    const numbered = questions.map((q, i) => ({
      id: i,
      topicId: q.topicId,
      text: q.text,
      options: q.options
    }));
    res.json({ courseTitle: req.params.courseTitle, questions: numbered });
  } catch (error) {
    res.status(500).json({ message: 'Failed to generate assessment', error: error.message });
  }
});

router.post('/diagnostic/:courseTitle/submit', auth, async (req, res) => {
  try {
    const { answers } = req.body;
    const courseTitle = req.params.courseTitle;
    const courseTopics = topicSkills[courseTitle];

    if (!courseTopics) {
      return res.status(404).json({ message: 'Course not found' });
    }

    const questions = courseTopics.diagnosticQuestions;
    let correct = 0;
    for (let i = 0; i < questions.length; i++) {
      if (answers[i] === questions[i].correct) correct++;
    }
    const score = Math.round((correct / questions.length) * 100);

    const topicResults = analyzeResults(courseTitle, answers);
    const learningPath = generateLearningPath(courseTitle, topicResults);

    const course = require('../models/Course').findAll({ published: true }).find(c => c.title === courseTitle);
    if (course) {
      Assessment.create({
        studentId: req.user.id,
        courseId: course.id,
        type: 'assessment',
        questions,
        answers,
        score
      });
    }

    res.json({
      score,
      total: questions.length,
      correct,
      courseTitle,
      topicResults,
      learningPath
    });
  } catch (error) {
    res.status(500).json({ message: 'Failed to submit assessment', error: error.message });
  }
});

router.get('/history', auth, (req, res) => {
  try {
    const assessments = Assessment.findByStudent(req.user.id);
    res.json(assessments);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch history', error: error.message });
  }
});

router.get('/learning-path/:courseTitle', auth, async (req, res) => {
  try {
    const courseTitle = req.params.courseTitle;
    const course = require('../models/Course').findAll({ published: true }).find(c => c.title === courseTitle);

    if (!course) {
      return res.status(404).json({ message: 'Course not found' });
    }

    const latest = Assessment.findLatestByStudentAndCourse(req.user.id, course.id);
    if (!latest) {
      return res.json({ hasAssessment: false, message: 'Take an assessment first' });
    }

    const topicResults = analyzeResults(courseTitle, latest.answers);
    const learningPath = generateLearningPath(courseTitle, topicResults);

    res.json({ hasAssessment: true, score: latest.score, learningPath });
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch learning path', error: error.message });
  }
});

module.exports = router;
