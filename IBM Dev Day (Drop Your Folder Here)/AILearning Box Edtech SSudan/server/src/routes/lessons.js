const express = require('express');
const router = express.Router({ mergeParams: true });
const { getLessons, getLesson, createLesson, updateLesson } = require('../controllers/lessonController');
const { auth, authorize } = require('../middleware/auth');

router.get('/', getLessons);
router.get('/:id', getLesson);
router.post('/', auth, authorize('ADMIN', 'TEACHER'), createLesson);
router.put('/:id', auth, authorize('ADMIN', 'TEACHER'), updateLesson);

module.exports = router;
