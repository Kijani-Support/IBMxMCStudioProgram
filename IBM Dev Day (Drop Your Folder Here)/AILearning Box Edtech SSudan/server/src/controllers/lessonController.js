const Lesson = require('../models/Lesson');
const Quiz = require('../models/Quiz');

exports.getLessons = async (req, res) => {
  try {
    const lessons = Lesson.findByCourseId(req.params.courseId);
    res.json(lessons);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch lessons', error: error.message });
  }
};

exports.getLesson = async (req, res) => {
  try {
    const lesson = Lesson.findById(req.params.id);
    if (!lesson) {
      return res.status(404).json({ message: 'Lesson not found' });
    }
    const quiz = Quiz.findByLessonId(lesson.id);
    res.json({ ...lesson, quiz });
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch lesson', error: error.message });
  }
};

exports.createLesson = async (req, res) => {
  try {
    const { title, description, content, video, audio, documents, order, duration } = req.body;

    const lesson = Lesson.create({
      courseId: req.params.courseId,
      title,
      description,
      content,
      video,
      audio,
      documents,
      order,
      duration
    });

    res.status(201).json(lesson);
  } catch (error) {
    res.status(500).json({ message: 'Failed to create lesson', error: error.message });
  }
};

exports.updateLesson = async (req, res) => {
  try {
    const lesson = Lesson.findById(req.params.id);
    if (!lesson) {
      return res.status(404).json({ message: 'Lesson not found' });
    }

    const updated = Lesson.update(req.params.id, req.body);
    res.json(updated);
  } catch (error) {
    res.status(500).json({ message: 'Failed to update lesson', error: error.message });
  }
};
