const express = require('express');
const router = express.Router();
const { getQuiz, createQuiz, submitQuiz } = require('../controllers/quizController');
const { auth, authorize } = require('../middleware/auth');

router.get('/lesson/:lessonId', getQuiz);
router.post('/lesson/:lessonId', auth, authorize('ADMIN', 'TEACHER'), createQuiz);
router.post('/:id/submit', auth, submitQuiz);

module.exports = router;
