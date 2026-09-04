const Course = require('../models/Course');
const Lesson = require('../models/Lesson');
const Quiz = require('../models/Quiz');

exports.getCourses = async (req, res) => {
  try {
    const { grade, subject, published } = req.query;
    const filters = {};
    
    if (grade) filters.grade = grade;
    if (subject) filters.subject = subject;
    if (published !== undefined) filters.published = published === 'true';

    const courses = Course.findAll(filters);
    res.json(courses);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch courses', error: error.message });
  }
};

exports.getCourse = async (req, res) => {
  try {
    const course = Course.findById(req.params.id);
    
    if (!course) {
      return res.status(404).json({ message: 'Course not found' });
    }

    const lessons = Lesson.findByCourseId(course.id);
    const lessonsWithQuiz = lessons.map(lesson => {
      const quiz = Quiz.findByLessonId(lesson.id);
      return { ...lesson, quiz };
    });
    
    res.json({ ...course, lessons: lessonsWithQuiz });
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch course', error: error.message });
  }
};

exports.createCourse = async (req, res) => {
  try {
    const { title, description, grade, subject, thumbnail } = req.body;

    const course = Course.create({
      title,
      description,
      grade,
      subject,
      thumbnail,
      createdBy: req.user.id
    });

    res.status(201).json(course);
  } catch (error) {
    res.status(500).json({ message: 'Failed to create course', error: error.message });
  }
};

exports.updateCourse = async (req, res) => {
  try {
    const course = Course.findById(req.params.id);
    
    if (!course) {
      return res.status(404).json({ message: 'Course not found' });
    }

    if (course.createdBy !== req.user.id && req.user.role !== 'ADMIN') {
      return res.status(403).json({ message: 'Not authorized' });
    }

    const updated = Course.update(req.params.id, req.body);
    res.json(updated);
  } catch (error) {
    res.status(500).json({ message: 'Failed to update course', error: error.message });
  }
};

exports.deleteCourse = async (req, res) => {
  try {
    const course = Course.findById(req.params.id);
    
    if (!course) {
      return res.status(404).json({ message: 'Course not found' });
    }

    Course.delete(req.params.id);
    res.json({ message: 'Course deleted' });
  } catch (error) {
    res.status(500).json({ message: 'Failed to delete course', error: error.message });
  }
};
