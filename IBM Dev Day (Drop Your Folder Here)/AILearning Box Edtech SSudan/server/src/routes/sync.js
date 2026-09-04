const express = require('express');
const router = express.Router();
const { sync, getChanges } = require('../controllers/syncController');
const { auth } = require('../middleware/auth');

router.post('/', auth, sync);
router.get('/changes', auth, getChanges);

module.exports = router;
