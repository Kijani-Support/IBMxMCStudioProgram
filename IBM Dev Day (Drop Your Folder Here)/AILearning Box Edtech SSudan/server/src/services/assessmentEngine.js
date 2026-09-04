const db = require('../config/db');

const topicSkills = {
  'Mathematics - Fractions': {
    courseId: null,
    topics: [
      { id: 'frac_basic', name: 'What is a Fraction', lessonOrder: 1, weight: 1 },
      { id: 'frac_equiv', name: 'Equivalent Fractions', lessonOrder: 2, weight: 2 },
      { id: 'frac_compare', name: 'Comparing Fractions', lessonOrder: 3, weight: 2 },
      { id: 'frac_add', name: 'Adding Fractions', lessonOrder: 4, weight: 3 },
      { id: 'frac_sub', name: 'Subtracting Fractions', lessonOrder: 5, weight: 3 },
      { id: 'frac_mul', name: 'Multiplying Fractions', lessonOrder: 6, weight: 3 },
      { id: 'frac_div', name: 'Dividing Fractions', lessonOrder: 7, weight: 3 }
    ],
    diagnosticQuestions: [
      { topicId: 'frac_basic', text: 'What is the top number of a fraction called?', options: ['Denominator', 'Numerator', 'Divisor', 'Quotient'], correct: 1 },
      { topicId: 'frac_basic', text: 'What does 3/4 represent?', options: ['3 divided by 4', '3 parts out of 4 equal parts', '4 parts out of 3', '3 wholes'], correct: 1 },
      { topicId: 'frac_equiv', text: 'Which fraction equals 1/2?', options: ['1/4', '2/3', '2/4', '3/4'], correct: 2 },
      { topicId: 'frac_equiv', text: 'To find equivalent fractions, you:', options: ['Add same to top and bottom', 'Multiply top and bottom by same number', 'Subtract from both', 'Divide only bottom'], correct: 1 },
      { topicId: 'frac_compare', text: 'Which is larger: 2/3 or 3/5?', options: ['2/3', '3/5', 'They are equal', 'Cannot tell'], correct: 0 },
      { topicId: 'frac_add', text: 'What is 1/4 + 2/4?', options: ['3/8', '3/4', '2/8', '1/2'], correct: 1 },
      { topicId: 'frac_add', text: 'What is 1/3 + 1/6?', options: ['1/2', '2/9', '2/6', '1/18'], correct: 0 },
      { topicId: 'frac_sub', text: 'What is 5/8 - 3/8?', options: ['2/16', '2/8', '2/4', '8/2'], correct: 1 },
      { topicId: 'frac_mul', text: 'What is 1/2 x 3/4?', options: ['3/8', '4/6', '3/4', '1/2'], correct: 0 },
      { topicId: 'frac_div', text: 'What is 1/2 / 1/4?', options: ['1/8', '1/2', '2', '4'], correct: 2 }
    ]
  },
  'Mathematics - Decimals': {
    topics: [
      { id: 'dec_basic', name: 'What are Decimals', lessonOrder: 1, weight: 1 },
      { id: 'dec_compare', name: 'Comparing Decimals', lessonOrder: 2, weight: 2 },
      { id: 'dec_ops', name: 'Adding and Subtracting Decimals', lessonOrder: 3, weight: 3 }
    ],
    diagnosticQuestions: [
      { topicId: 'dec_basic', text: 'What is 0.5 as a fraction?', options: ['1/5', '1/2', '5/100', '1/10'], correct: 1 },
      { topicId: 'dec_basic', text: 'In 3.456, which digit is in the tenths place?', options: ['3', '4', '5', '6'], correct: 1 },
      { topicId: 'dec_compare', text: 'Which is larger: 0.5 or 0.25?', options: ['0.25', '0.5', 'They are equal', 'Cannot tell'], correct: 1 },
      { topicId: 'dec_compare', text: '0.30 is the same as:', options: ['0.3', '0.03', '3.0', '30'], correct: 0 },
      { topicId: 'dec_ops', text: 'What is 3.45 + 2.3?', options: ['5.75', '5.78', '57.5', '5.85'], correct: 0 }
    ]
  },
  'Mathematics - Geometry': {
    topics: [
      { id: 'geo_2d', name: '2D Shapes', lessonOrder: 1, weight: 1 },
      { id: 'geo_3d', name: '3D Shapes', lessonOrder: 2, weight: 1 },
      { id: 'geo_area', name: 'Perimeter and Area', lessonOrder: 3, weight: 2 }
    ],
    diagnosticQuestions: [
      { topicId: 'geo_2d', text: 'How many sides does a triangle have?', options: ['2', '3', '4', '5'], correct: 1 },
      { topicId: 'geo_2d', text: 'A square has how many right angles?', options: ['2', '3', '4', '0'], correct: 2 },
      { topicId: 'geo_3d', text: 'A cube has how many faces?', options: ['4', '6', '8', '12'], correct: 1 },
      { topicId: 'geo_area', text: 'Perimeter of a rectangle with length 5 and width 3?', options: ['8', '15', '16', '10'], correct: 2 },
      { topicId: 'geo_area', text: 'Area of a square with side 4?', options: ['8', '12', '16', '4'], correct: 2 }
    ]
  },
  'Science - Plants': {
    topics: [
      { id: 'plant_parts', name: 'Parts of a Plant', lessonOrder: 1, weight: 1 },
      { id: 'plant_photo', name: 'Photosynthesis', lessonOrder: 2, weight: 2 },
      { id: 'plant_life', name: 'Plant Life Cycles', lessonOrder: 3, weight: 2 }
    ],
    diagnosticQuestions: [
      { topicId: 'plant_parts', text: 'Which part absorbs water from soil?', options: ['Leaves', 'Stem', 'Roots', 'Flowers'], correct: 2 },
      { topicId: 'plant_parts', text: 'What is the main function of leaves?', options: ['Absorb water', 'Support plant', 'Make food', 'Produce seeds'], correct: 2 },
      { topicId: 'plant_parts', text: 'Which part produces seeds?', options: ['Roots', 'Stem', 'Leaves', 'Flowers'], correct: 3 },
      { topicId: 'plant_photo', text: 'What does a plant need for photosynthesis?', options: ['Only water', 'Sunlight, water, CO2', 'Only sunlight', 'Soil and oxygen'], correct: 1 },
      { topicId: 'plant_photo', text: 'What do plants release during photosynthesis?', options: ['CO2', 'Water', 'Oxygen', 'Nitrogen'], correct: 2 },
      { topicId: 'plant_life', text: 'What is the first stage of a plant life cycle?', options: ['Flower', 'Fruit', 'Seed', 'Leaf'], correct: 2 }
    ]
  },
  'Science - Animals': {
    topics: [
      { id: 'animal_class', name: 'Animal Classification', lessonOrder: 1, weight: 1 },
      { id: 'animal_habitat', name: 'Animal Habitats', lessonOrder: 2, weight: 2 },
      { id: 'animal_food', name: 'Food Chains', lessonOrder: 3, weight: 2 }
    ],
    diagnosticQuestions: [
      { topicId: 'animal_class', text: 'Humans belong to which group?', options: ['Birds', 'Reptiles', 'Mammals', 'Fish'], correct: 2 },
      { topicId: 'animal_class', text: 'What do all mammals have?', options: ['Can fly', 'Have scales', 'Feed babies milk', 'Live in water'], correct: 2 },
      { topicId: 'animal_class', text: 'Which animals are cold-blooded?', options: ['Dogs', 'Eagles', 'Snakes', 'Humans'], correct: 2 },
      { topicId: 'animal_habitat', text: 'Which habitat is very hot and dry?', options: ['Forest', 'Desert', 'Ocean', 'Arctic'], correct: 1 },
      { topicId: 'animal_food', text: 'What is at the base of a food chain?', options: ['Carnivore', 'Herbivore', 'Producer (plant)', 'Decomposer'], correct: 2 }
    ]
  },
  'English - Reading': {
    topics: [
      { id: 'read_comp', name: 'Reading Comprehension', lessonOrder: 1, weight: 1 }
    ],
    diagnosticQuestions: [
      { topicId: 'read_comp', text: 'What should you do BEFORE reading?', options: ['Look at title and pictures', 'Skip ahead', 'Close the book', 'Read fast'], correct: 0 },
      { topicId: 'read_comp', text: 'Main idea means:', options: ['A small detail', 'The most important point', 'The first word', 'The last sentence'], correct: 1 },
      { topicId: 'read_comp', text: 'While reading, you should:', options: ['Read as fast as possible', 'Picture what is happening', 'Skip words you don\'t know', 'Only look at pictures'], correct: 1 }
    ]
  }
};

function getLessonsForCourse(courseTitle) {
  const course = db.prepare('SELECT id FROM courses WHERE title = ? AND published = 1').get(courseTitle);
  if (!course) return [];
  return db.prepare('SELECT id, title, description, "order", duration FROM lessons WHERE courseId = ? ORDER BY "order"').all(course.id);
}

function getQuizForLesson(lessonId) {
  return db.prepare('SELECT id, title, passingScore FROM quizzes WHERE lessonId = ?').get(lessonId);
}

function generateDiagnostic(courseTitle) {
  const courseTopics = topicSkills[courseTitle];
  if (!courseTopics) return null;
  return courseTopics.diagnosticQuestions;
}

function analyzeResults(courseTitle, answers) {
  const courseTopics = topicSkills[courseTitle];
  if (!courseTopics) return null;

  const topicResults = {};
  for (const topic of courseTopics.topics) {
    topicResults[topic.id] = { name: topic.name, correct: 0, total: 0, percentage: 0, lessonOrder: topic.lessonOrder };
  }

  const questions = courseTopics.diagnosticQuestions;
  for (let i = 0; i < questions.length; i++) {
    const q = questions[i];
    const topic = topicResults[q.topicId];
    topic.total++;
    if (answers[i] === q.correct) {
      topic.correct++;
    }
  }

  for (const topicId of Object.keys(topicResults)) {
    const t = topicResults[topicId];
    t.percentage = t.total > 0 ? Math.round((t.correct / t.total) * 100) : 0;
  }

  return topicResults;
}

function generateLearningPath(courseTitle, topicResults) {
  const courseTopics = topicSkills[courseTitle];
  if (!courseTopics) return null;

  const lessons = getLessonsForCourse(courseTitle);
  const lessonMap = {};
  for (const l of lessons) {
    lessonMap[l.order] = l;
  }

  const path = [];
  for (const topic of courseTopics.topics) {
    const result = topicResults[topic.id];
    const lesson = lessonMap[topic.lessonOrder];
    const quiz = lesson ? getQuizForLesson(lesson.id) : null;

    let status;
    if (result.percentage < 50) status = 'needs_review';
    else if (result.percentage < 80) status = 'practice_recommended';
    else status = 'mastered';

    path.push({
      topicId: topic.id,
      name: topic.name,
      lessonOrder: topic.lessonOrder,
      status,
      score: result.percentage,
      priority: status === 'needs_review' ? 3 : status === 'practice_recommended' ? 2 : 0,
      lesson: lesson ? {
        id: lesson.id,
        title: lesson.title,
        description: lesson.description,
        duration: lesson.duration
      } : null,
      quiz: quiz ? {
        id: quiz.id,
        title: quiz.title
      } : null
    });
  }

  path.sort((a, b) => b.priority - a.priority || a.score - b.score);
  return path;
}

module.exports = { generateDiagnostic, analyzeResults, generateLearningPath, topicSkills };
