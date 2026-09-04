const express = require('express');
const router = express.Router();
const { getProgress, updateProgress, getCourseProgress, getAllCourseProgress } = require('../controllers/progressController');
const { auth } = require('../middleware/auth');

router.get('/', auth, getProgress);
router.post('/', auth, updateProgress);
router.get('/course/:courseId', auth, getCourseProgress);
router.get('/courses', auth, getAllCourseProgress);

module.exports = router;
