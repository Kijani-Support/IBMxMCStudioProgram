const express = require('express');
const router = express.Router();
const { getStudentReport, getAllStudentsReport } = require('../controllers/reportController');
const { auth, authorize } = require('../middleware/auth');

router.get('/student/:studentId', auth, authorize('TEACHER', 'ADMIN'), getStudentReport);
router.get('/all', auth, authorize('TEACHER', 'ADMIN'), getAllStudentsReport);

module.exports = router;
