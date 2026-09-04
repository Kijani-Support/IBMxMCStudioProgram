const express = require('express');
const router = express.Router();
const { getCourses, getCourse, createCourse, updateCourse, deleteCourse } = require('../controllers/courseController');
const { auth, authorize } = require('../middleware/auth');

router.get('/', getCourses);
router.get('/:id', getCourse);
router.post('/', auth, authorize('ADMIN', 'TEACHER'), createCourse);
router.put('/:id', auth, authorize('ADMIN', 'TEACHER'), updateCourse);
router.delete('/:id', auth, authorize('ADMIN'), deleteCourse);

module.exports = router;
