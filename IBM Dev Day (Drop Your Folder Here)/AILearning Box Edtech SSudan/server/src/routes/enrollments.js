const express = require('express');
const router = express.Router();
const { enroll, getEnrollments, getEnrollmentStats } = require('../controllers/enrollmentController');
const { auth } = require('../middleware/auth');

router.post('/', auth, enroll);
router.get('/', auth, getEnrollments);
router.get('/stats', auth, getEnrollmentStats);

module.exports = router;
