const Quiz = require('../models/Quiz');

exports.getQuiz = async (req, res) => {
  try {
    const quiz = Quiz.findByLessonId(req.params.lessonId);
    if (!quiz) {
      return res.status(404).json({ message: 'Quiz not found' });
    }
    res.json(quiz);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch quiz', error: error.message });
  }
};

exports.createQuiz = async (req, res) => {
  try {
    const { title, questions, passingScore } = req.body;

    const quiz = Quiz.create({
      lessonId: req.params.lessonId,
      title,
      questions,
      passingScore
    });

    res.status(201).json(quiz);
  } catch (error) {
    res.status(500).json({ message: 'Failed to create quiz', error: error.message });
  }
};

exports.submitQuiz = async (req, res) => {
  try {
    const quiz = Quiz.findById(req.params.id);
    if (!quiz) {
      return res.status(404).json({ message: 'Quiz not found' });
    }

    const { answers } = req.body;
    let correct = 0;

    quiz.questions.forEach((question, index) => {
      const selectedOption = answers[index];
      if (selectedOption !== undefined && question.options[selectedOption]?.isCorrect) {
        correct++;
      }
    });

    const score = Math.round((correct / quiz.questions.length) * 100);
    const passed = score >= quiz.passingScore;

    res.json({
      score,
      passed,
      correct,
      total: quiz.questions.length,
      passingScore: quiz.passingScore
    });
  } catch (error) {
    res.status(500).json({ message: 'Failed to submit quiz', error: error.message });
  }
};
