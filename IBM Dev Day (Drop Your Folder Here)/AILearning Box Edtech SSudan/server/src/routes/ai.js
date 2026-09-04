const express = require('express');
const router = express.Router();
const { auth } = require('../middleware/auth');

router.post('/tutor', auth, async (req, res) => {
  try {
    const { question, courseId, lessonId } = req.body;

    if (!question) {
      return res.status(400).json({ message: 'Question is required' });
    }

    const response = await generateTutorResponse(question, courseId, lessonId, req.user);
    res.json({ answer: response });
  } catch (error) {
    res.status(500).json({ message: 'AI tutor error', error: error.message });
  }
});

router.post('/generate-quiz', auth, async (req, res) => {
  try {
    const { lessonId, topic, difficulty } = req.body;

    const questions = generateQuizQuestions(topic, difficulty || 'medium');
    res.json({ questions });
  } catch (error) {
    res.status(500).json({ message: 'Quiz generation error', error: error.message });
  }
});

async function generateTutorResponse(question, courseId, lessonId, user) {
  const lowerQ = question.toLowerCase();

  if (lowerQ.includes('fraction')) {
    return `A fraction represents a part of a whole. For example, 1/2 means one part out of two equal parts.

Key concepts:
- The top number (numerator) tells how many parts we have
- The bottom number (denominator) tells how many equal parts make the whole
- Equivalent fractions: 1/2 = 2/4 = 3/6

Would you like me to explain any specific aspect of fractions?`;
  }

  if (lowerQ.includes('addition') || lowerQ.includes('add')) {
    return `Addition is combining two or more numbers to find their total.

For example:
- 5 + 3 = 8
- 12 + 7 = 19

Tips:
- Start with the ones column
- Carry over when numbers add up to 10 or more
- Use a number line to visualize addition

Would you like some practice problems?`;
  }

  if (lowerQ.includes('subtraction') || lowerQ.includes('subtract')) {
    return `Subtraction means taking away one number from another.

For example:
- 10 - 4 = 6
- 15 - 8 = 7

Tips:
- Start from the right column
- Borrow from the next column if needed
- Check your answer by adding

Would you like practice problems?`;
  }

  if (lowerQ.includes('multiplication') || lowerQ.includes('multiply')) {
    return `Multiplication is repeated addition.

For example:
- 4 x 3 = 4 + 4 + 4 = 12
- 6 x 5 = 6 + 6 + 6 + 6 + 6 = 30

Tips:
- Learn your times tables
- Use arrays to visualize
- Multiplication is commutative: 4 x 3 = 3 x 4

Would you like to practice?`;
  }

  if (lowerQ.includes('plant')) {
    return `Plants are living things that grow in soil and need sunlight, water, and air.

Parts of a plant:
- Roots: absorb water and nutrients from soil
- Stem: carries water and nutrients up and down
- Leaves: make food using sunlight (photosynthesis)
- Flowers: produce seeds for new plants

Key fact: Plants convert sunlight into energy through photosynthesis!

Would you like to learn more about any part?`;
  }

  if (lowerQ.includes('animal')) {
    return `Animals are living things that can move, eat, and grow.

Animal groups:
- Mammals: warm-blooded, have fur/hair, feed babies milk (humans, dogs, lions)
- Birds: have feathers, lay eggs, can fly (eagles, penguins)
- Fish: live in water, breathe through gills (sharks, goldfish)
- Reptiles: cold-blooded, have scales (snakes, lizards)

Would you like to know more about a specific animal group?`;
  }

  return `That's a great question! Let me help you understand this topic.

Based on the curriculum, I can help you with:
- Mathematics concepts (fractions, addition, subtraction, multiplication)
- Science topics (plants, animals, water cycle)
- Reading comprehension
- And more!

Could you ask about a specific topic? For example:
- "Explain equivalent fractions"
- "How do plants make food?"
- "What are the parts of a cell?"

I'll use the curriculum content to give you the best explanation!`;
}

function generateQuizQuestions(topic, difficulty) {
  const questions = {
    fractions: [
      {
        text: 'What is 1/2 + 1/4?',
        options: [
          { text: '2/6', isCorrect: false },
          { text: '3/4', isCorrect: true },
          { text: '1/6', isCorrect: false },
          { text: '2/4', isCorrect: false }
        ]
      },
      {
        text: 'Which fraction is equivalent to 1/2?',
        options: [
          { text: '1/4', isCorrect: false },
          { text: '2/3', isCorrect: false },
          { text: '2/4', isCorrect: true },
          { text: '3/4', isCorrect: false }
        ]
      }
    ],
    addition: [
      {
        text: 'What is 25 + 37?',
        options: [
          { text: '52', isCorrect: false },
          { text: '62', isCorrect: true },
          { text: '72', isCorrect: false },
          { text: '57', isCorrect: false }
        ]
      },
      {
        text: 'What is 145 + 256?',
        options: [
          { text: '391', isCorrect: false },
          { text: '401', isCorrect: true },
          { text: '301', isCorrect: false },
          { text: '411', isCorrect: false }
        ]
      }
    ]
  };

  return questions[topic] || questions.fractions;
}

module.exports = router;
