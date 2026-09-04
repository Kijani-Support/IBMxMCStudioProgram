const db = require('../src/config/db');
const bcrypt = require('bcryptjs');

const users = [
  { name: 'Admin User', email: 'admin@learningbox.org', password: 'admin123', role: 'ADMIN' },
  { name: 'Teacher Amina', email: 'amina@learningbox.org', password: 'teacher123', role: 'TEACHER', grade: 'Grade 5', school: 'Juba Primary' },
  { name: 'James Kuol', email: 'james@student.com', password: 'student123', role: 'STUDENT', grade: 'Grade 5', school: 'Juba Primary' },
  { name: 'Nyamal Gatluak', email: 'nyamal@student.com', password: 'student123', role: 'STUDENT', grade: 'Grade 5', school: 'Juba Primary' },
  { name: 'Peter Mak', email: 'peter@student.com', password: 'student123', role: 'STUDENT', grade: 'Grade 5', school: 'Juba Primary' },
];

const courses = [
  { title: 'Mathematics - Fractions', description: 'Learn about fractions, equivalent fractions, comparing and operating with fractions.', grade: 'Grade 5', subject: 'Mathematics', published: true },
  { title: 'Mathematics - Decimals', description: 'Understanding decimal numbers, place value, and operations with decimals.', grade: 'Grade 5', subject: 'Mathematics', published: true },
  { title: 'Mathematics - Geometry', description: 'Shapes, angles, area, perimeter, and spatial reasoning.', grade: 'Grade 5', subject: 'Mathematics', published: true },
  { title: 'Science - Plants', description: 'Parts of plants, photosynthesis, plant life cycles, and growth.', grade: 'Grade 5', subject: 'Science', published: true },
  { title: 'Science - Animals', description: 'Animal classification, habitats, food chains, and adaptation.', grade: 'Grade 5', subject: 'Science', published: true },
  { title: 'English - Reading', description: 'Reading comprehension, vocabulary, and storytelling.', grade: 'Grade 5', subject: 'English', published: true }
];

const lessonsData = {
  0: [
    { title: 'What is a Fraction?', description: 'Introduction to fractions and their parts',
      content: `WHAT IS A FRACTION?

A fraction represents a part of a whole or a group.

PARTS OF A FRACTION:
- Numerator (top number): tells how many parts we have
- Denominator (bottom number): tells how many equal parts make the whole

EXAMPLES:
- 1/2 means one part out of two equal parts
- 3/4 means three parts out of four equal parts
- 2/5 means two parts out of five equal parts

VISUAL EXAMPLE:
If you cut a pizza into 4 equal slices and eat 1, you ate 1/4 of the pizza.
If you eat 3 slices, you ate 3/4 of the pizza.

KEY POINTS:
- A fraction less than 1 (like 1/2) means less than a whole
- A fraction equal to 1 (like 4/4) means exactly one whole
- A fraction greater than 1 (like 5/4) means more than one whole

PRACTICE:
Write the fraction for:
1. One part out of three equal parts = ___
2. Five parts out of eight equal parts = ___
3. Seven parts out of ten equal parts = ___

REMEMBER: The denominator tells us how many EQUAL parts the whole is divided into.`, order: 1, duration: 10 },
    { title: 'Equivalent Fractions', description: 'Understanding fractions that represent the same amount',
      content: `EQUIVALENT FRACTIONS

Equivalent fractions are different fractions that represent the same amount.

HOW TO FIND EQUIVALENT FRACTIONS:
Multiply or divide both the numerator and denominator by the same number.

EXAMPLES:
- 1/2 = 2/4 = 3/6 = 4/8 (multiply by 2, 3, 4)
- 2/3 = 4/6 = 6/9 (multiply by 2, 3)
- 4/8 = 2/4 = 1/2 (divide by 2)

RULE:
If you multiply or divide both parts of a fraction by the same number, you get an equivalent fraction.

VISUAL:
Imagine a chocolate bar with 4 pieces. Eating 2 pieces (2/4) is the same as eating half the bar (1/2).

COMMON EQUIVALENT FRACTIONS TO REMEMBER:
- 1/2 = 2/4 = 3/6 = 4/8 = 5/10
- 1/3 = 2/6 = 3/9
- 1/4 = 2/8 = 3/12
- 2/5 = 4/10 = 6/15

PRACTICE:
Find an equivalent fraction for:
1. 1/3 = ___/6
2. 2/5 = 6/___
3. 3/4 = ___/12`, order: 2, duration: 15 },
    { title: 'Comparing Fractions', description: 'How to compare which fraction is larger or smaller',
      content: `COMPARING FRACTIONS

To compare fractions, we need to determine which one is larger or smaller.

METHOD 1: SAME DENOMINATOR
If fractions have the same denominator, compare the numerators.
- 3/8 vs 5/8: 5/8 is larger (5 > 3)

METHOD 2: CROSS MULTIPLICATION
To compare A/B and C/D:
- Multiply A x D
- Multiply B x C
- Compare the results

EXAMPLE:
Compare 2/3 and 3/5:
- 2 x 5 = 10
- 3 x 3 = 9
- 10 > 9, so 2/3 > 3/5

METHOD 3: COMMON DENOMINATOR
Convert both fractions to have the same denominator, then compare.

EXAMPLE:
Compare 1/2 and 2/3:
- 1/2 = 3/6
- 2/3 = 4/6
- 4/6 > 3/6, so 2/3 > 1/2

TIPS:
- A fraction with a larger numerator is not always larger
- The closer the numerator is to the denominator, the larger the fraction
- 7/8 is almost 1 whole

PRACTICE:
Compare using <, >, or =:
1. 1/2 ___ 3/4
2. 2/3 ___ 4/6
3. 5/8 ___ 3/4`, order: 3, duration: 15 },
    { title: 'Adding Fractions', description: 'How to add fractions with same and different denominators',
      content: `ADDING FRACTIONS

Adding fractions is combining parts together.

SAME DENOMINATOR:
Simply add the numerators and keep the denominator.
- 1/4 + 2/4 = 3/4
- 3/8 + 5/8 = 8/8 = 1

DIFFERENT DENOMINATORS:
1. Find a common denominator
2. Convert both fractions
3. Add the numerators

EXAMPLE:
1/3 + 1/4:
- Common denominator: 12
- 1/3 = 4/12
- 1/4 = 3/12
- 4/12 + 3/12 = 7/12

ADDING MIXED NUMBERS:
1. Add the whole numbers
2. Add the fractions
3. Simplify if needed

EXAMPLE:
2 1/4 + 1 2/4 = 3 3/4

PRACTICE:
1. 3/5 + 1/5 = ___
2. 1/2 + 1/3 = ___
3. 2 1/4 + 1 3/4 = ___`, order: 4, duration: 20 },
    { title: 'Subtracting Fractions', description: 'How to subtract fractions',
      content: `SUBTRACTING FRACTIONS

Subtracting fractions means taking away parts.

SAME DENOMINATOR:
Subtract the numerators and keep the denominator.
- 5/8 - 3/8 = 2/8 = 1/4

DIFFERENT DENOMINATORS:
1. Find a common denominator
2. Convert both fractions
3. Subtract the numerators

EXAMPLE:
3/4 - 1/3:
- Common denominator: 12
- 3/4 = 9/12
- 1/3 = 4/12
- 9/12 - 4/12 = 5/12

SUBTRACTING MIXED NUMBERS:
1. If the first fraction is smaller, borrow from the whole number
2. Subtract the fractions
3. Subtract the whole numbers

EXAMPLE:
3 1/4 - 1 3/4:
- Borrow: 2 5/4 - 1 3/4 = 1 2/4 = 1 1/2

PRACTICE:
1. 7/8 - 3/8 = ___
2. 5/6 - 1/3 = ___
3. 4 1/2 - 2 3/4 = ___`, order: 5, duration: 20 },
    { title: 'Multiplying Fractions', description: 'How to multiply fractions together',
      content: `MULTIPLYING FRACTIONS

Multiplying fractions is simpler than adding or subtracting.

THE RULE:
Multiply the numerators together and multiply the denominators together.

EXAMPLE:
2/3 x 4/5:
- Numerators: 2 x 4 = 8
- Denominators: 3 x 5 = 15
- Answer: 8/15

MULTIPLYING BY A WHOLE NUMBER:
Convert the whole number to a fraction (put it over 1).
- 3 x 2/5 = 3/1 x 2/5 = 6/5 = 1 1/5

SIMPLIFY BEFORE MULTIPLYING:
Cancel common factors before multiplying to make it easier.
- 4/6 x 3/8 = 2/3 x 3/8 = 6/24 = 1/4

MULTIPLYING MIXED NUMBERS:
1. Convert to improper fractions
2. Multiply
3. Convert back to mixed number

EXAMPLE:
1 1/2 x 2 1/3 = 3/2 x 7/3 = 21/6 = 3 3/6 = 3 1/2

PRACTICE:
1. 1/2 x 3/4 = ___
2. 2/3 x 5/6 = ___
3. 1 1/3 x 2 1/2 = ___`, order: 6, duration: 15 },
    { title: 'Dividing Fractions', description: 'How to divide fractions using the reciprocal',
      content: `DIVIDING FRACTIONS

Dividing fractions uses a special rule called "Keep, Change, Flip".

THE RULE (KCF):
Keep the first fraction, Change division to multiplication, Flip the second fraction.

EXAMPLE:
1/2 / 3/4:
- Keep: 1/2
- Change: x
- Flip: 4/3
- Solve: 1/2 x 4/3 = 4/6 = 2/3

WHY DOES THIS WORK?
Dividing by a fraction is the same as multiplying by its reciprocal.

EXAMPLE WITH WHOLE NUMBERS:
6 / 3/4:
- Convert 6 to 6/1
- 6/1 / 3/4 = 6/1 x 4/3 = 24/3 = 8

DIVIDING MIXED NUMBERS:
1. Convert to improper fractions
2. Apply KCF rule
3. Solve

EXAMPLE:
2 1/2 / 1 1/4:
- 5/2 / 5/4 = 5/2 x 4/5 = 20/10 = 2

PRACTICE:
1. 3/4 / 1/2 = ___
2. 2/3 / 4/5 = ___
3. 3 1/2 / 1 1/4 = ___`, order: 7, duration: 15 }
  ],
  1: [
    { title: 'What are Decimals?', description: 'Introduction to decimal numbers and their place value',
      content: `WHAT ARE DECIMALS?

Decimals are another way to write fractions. They use a decimal point.

PLACE VALUE OF DECIMALS:
- 0.1 = one tenth (1/10)
- 0.01 = one hundredth (1/100)
- 0.001 = one thousandth (1/1000)

EXAMPLE:
In the number 3.456:
- 3 is in the ones place
- 4 is in the tenths place
- 5 is in the hundredths place
- 6 is in the thousandths place

READING DECIMALS:
- 0.5 = "five tenths" or "zero point five"
- 0.25 = "twenty-five hundredths" or "zero point two five"

FRACTIONS TO DECIMALS:
- 1/2 = 0.5
- 1/4 = 0.25
- 3/4 = 0.75
- 1/5 = 0.2
- 1/10 = 0.1

PRACTICE:
Convert to decimals:
1. 3/4 = ___
2. 7/10 = ___
3. 2/5 = ___`, order: 1, duration: 10 },
    { title: 'Comparing Decimals', description: 'How to compare decimal numbers',
      content: `COMPARING DECIMALS

To compare decimals, look at each place value from left to right.

STEPS:
1. Compare the whole number parts
2. If equal, compare the tenths
3. If equal, compare the hundredths
4. Continue until you find a difference

EXAMPLE:
Compare 3.45 and 3.42:
- Whole numbers: 3 = 3
- Tenths: 4 = 4
- Hundredths: 5 > 2
- So 3.45 > 3.42

COMMON MISTAKE:
0.5 is NOT less than 0.25!
- 0.5 = 0.50
- 0.50 > 0.25

TIPS:
- Add trailing zeros to make comparison easier
- 0.5 = 0.50 = 0.500
- 0.25 = 0.250

PRACTICE:
Compare using <, >, or =:
1. 0.3 ___ 0.25
2. 1.5 ___ 1.50
3. 0.8 ___ 0.79`, order: 2, duration: 10 },
    { title: 'Adding and Subtracting Decimals', description: 'Operations with decimal numbers',
      content: `ADDING AND SUBTRACTING DECIMALS

Adding and subtracting decimals is like adding whole numbers, but you must line up the decimal points.

STEPS:
1. Line up the decimal points vertically
2. Add zeros as placeholders if needed
3. Add or subtract as usual
4. Place the decimal point in the answer

EXAMPLE - ADDITION:
  3.45
+ 2.3
-----
  5.75

EXAMPLE - SUBTRACTION:
  5.60
- 2.34
------
  3.26

TIPS:
- Always line up decimal points
- Use placeholder zeros to avoid mistakes
- Place decimal point directly below in the answer

PRACTICE:
1. 4.5 + 2.3 = ___
2. 7.8 - 3.45 = ___
3. 12.6 + 5.78 = ___`, order: 3, duration: 15 }
  ],
  2: [
    { title: '2D Shapes', description: 'Properties of two-dimensional shapes',
      content: `2D SHAPES

2D shapes are flat shapes that have length and width but no depth.

COMMON 2D SHAPES:

TRIANGLE:
- 3 sides and 3 angles
- The angles in a triangle add up to 180 degrees
- Types: equilateral, isosceles, scalene

SQUARE:
- 4 equal sides
- 4 right angles (90 degrees)
- Opposite sides are parallel

RECTANGLE:
- 4 sides
- 4 right angles (90 degrees)
- Opposite sides are equal and parallel

CIRCLE:
- No sides or corners
- All points on the edge are the same distance from the center
- Has a diameter and radius

PENTAGON:
- 5 sides and 5 angles

HEXAGON:
- 6 sides and 6 angles

PRACTICE:
1. How many sides does a triangle have? ___
2. A square has how many right angles? ___
3. What shape has 6 sides? ___`, order: 1, duration: 10 },
    { title: '3D Shapes', description: 'Properties of three-dimensional shapes',
      content: `3D SHAPES

3D shapes have length, width, and depth (or height).

COMMON 3D SHAPES:

CUBE:
- 6 square faces
- 8 corners (vertices)
- 12 edges

CUBOID (RECTANGULAR PRISM):
- 6 rectangular faces
- 8 vertices
- 12 edges

SPHERE:
- No faces, edges, or vertices
- Perfectly round
- Like a ball

CYLINDER:
- 2 circular faces
- 1 curved surface
- Like a can

CONE:
- 1 circular face
- 1 curved surface
- 1 vertex (tip)

PYRAMID:
- Triangular faces meeting at a point
- Square or triangular base

PRACTICE:
1. A cube has ___ faces
2. A sphere is perfectly ___
3. A cylinder has ___ circular faces`, order: 2, duration: 10 },
    { title: 'Perimeter and Area', description: 'Calculating perimeter and area of shapes',
      content: `PERIMETER AND AREA

Perimeter and area measure different properties of shapes.

PERIMETER:
The total distance around the outside of a shape.

Rectangle: Perimeter = 2 x (length + width)
Example: length=5, width=3: P = 2 x (5+3) = 16 cm

Square: Perimeter = 4 x side
Example: side=4: P = 4 x 4 = 16 cm

AREA:
The amount of space inside a shape.

Rectangle: Area = length x width
Example: length=5, width=3: A = 5 x 3 = 15 cm squared

Square: Area = side x side
Example: side=4: A = 4 x 4 = 16 cm squared

Triangle: Area = (base x height) / 2

REMEMBER:
- Perimeter is measured in units (cm)
- Area is measured in square units (cm squared)

PRACTICE:
1. Perimeter of rectangle with length 6, width 4 = ___
2. Area of square with side 5 = ___
3. Area of triangle with base 8, height 3 = ___`, order: 3, duration: 15 }
  ],
  3: [
    { title: 'Parts of a Plant', description: 'Learn about roots, stem, leaves, flowers, and their functions',
      content: `PARTS OF A PLANT

Plants have several important parts, each with a special job.

ROOT SYSTEM:
- ROOTS: Anchor the plant and absorb water and nutrients from soil
- Root hairs increase surface area for absorption
- Some roots store food (like carrots and potatoes)

SHOOT SYSTEM:

STEM:
- Supports the plant
- Carries water and nutrients up and down
- Connects roots to leaves
- Some stems store food (like cacti)

LEAVES:
- Make food for the plant through photosynthesis
- Have tiny pores called stomata for gas exchange
- Contain chlorophyll (makes them green)
- Different shapes help identify plants

FLOWERS:
- The reproductive part of the plant
- Attract insects with color and scent
- Produce seeds after pollination
- Have petals, sepals, stamens, and pistils

FRUIT:
- Protects seeds
- Helps seeds spread to new locations
- Often eaten by animals who spread the seeds

PRACTICE:
1. Which part absorbs water from soil? ___
2. What makes leaves green? ___
3. What is the reproductive part of a plant? ___`, order: 1, duration: 10 },
    { title: 'Photosynthesis', description: 'How plants make their own food using sunlight',
      content: `PHOTOSYNTHESIS

Photosynthesis is the process plants use to make their own food.

WHAT PLANTS NEED:
- Sunlight
- Water (from soil through roots)
- Carbon dioxide (from air through leaves)

WHAT PLANTS MAKE:
- Glucose (sugar) - food for the plant
- Oxygen - released into the air

THE PROCESS:
1. Leaves absorb sunlight
2. Roots absorb water
3. Leaves take in carbon dioxide
4. Using sunlight energy, plants combine water and carbon dioxide
5. This produces glucose and oxygen

CHEMICAL WORD EQUATION:
Water + Carbon Dioxide = Glucose + Oxygen

WHY PHOTOSYNTHESIS MATTERS:
- Produces food for the plant
- Releases oxygen for animals and humans
- Removes carbon dioxide from the air
- Base of most food chains on Earth

WHERE DOES IT HAPPEN?
In tiny structures inside leaves called chloroplasts. They contain chlorophyll, which gives leaves their green color.

PRACTICE:
1. What gas do plants release during photosynthesis? ___
2. What do plants need from the sun? ___
3. Where does photosynthesis happen in a leaf? ___`, order: 2, duration: 15 },
    { title: 'Plant Life Cycles', description: 'How plants grow and reproduce',
      content: `PLANT LIFE CYCLES

All plants go through a life cycle from seed to maturity.

SEED:
- Contains a baby plant (embryo)
- Has stored food
- Needs water, warmth, and air to germinate

GERMINATION:
- Seed absorbs water and swells
- Root grows downward
- Shoot grows upward
- Seed coat breaks open

GROWTH:
- Plant develops roots, stems, and leaves
- Begins photosynthesis
- Grows larger and stronger

FLOWERING:
- Mature plant produces flowers
- Pollination occurs (by wind, insects, or animals)
- Fertilization happens

SEED PRODUCTION:
- Seeds develop inside fruit
- Seeds are spread by wind, water, or animals
- Cycle begins again

TYPES OF PLANTS:

ANNUALS:
Complete their life cycle in one year (e.g., beans, corn)

BIENNIALS:
Take two years to complete life cycle (e.g., carrots)

PERENNIALS:
Live for many years (e.g., trees, roses)

PRACTICE:
1. What is the first stage of a plant life cycle? ___
2. What happens during germination? ___
3. Name a type of plant that lives for many years: ___`, order: 3, duration: 15 }
  ],
  4: [
    { title: 'Animal Classification', description: 'How scientists group animals into categories',
      content: `ANIMAL CLASSIFICATION

Scientists classify animals based on their characteristics.

VERTEBRATES (Animals with Backbone):

MAMMALS:
- Have fur or hair
- Feed babies milk
- Warm-blooded
- Examples: humans, dogs, lions, elephants

BIRDS:
- Have feathers
- Lay eggs
- Most can fly
- Warm-blooded
- Examples: eagles, penguins, chickens

FISH:
- Live in water
- Breathe through gills
- Have scales
- Cold-blooded
- Examples: sharks, goldfish, salmon

REPTILES:
- Have scales
- Cold-blooded
- Most lay eggs
- Examples: snakes, lizards, turtles

AMPHIBIANS:
- Live in water and on land
- Cold-blooded
- Moist skin
- Examples: frogs, toads, salamanders

INVERTEBRATES (Animals without Backbone):
- Insects, spiders, worms, jellyfish
- Make up 95% of all animal species!

PRACTICE:
1. Humans belong to which group? ___
2. What do all mammals feed their babies? ___
3. Which animals are cold-blooded: dogs or snakes? ___`, order: 1, duration: 10 },
    { title: 'Animal Habitats', description: 'Where animals live and why',
      content: `ANIMAL HABITATS

An animal's habitat is its natural home where it finds food, water, and shelter.

MAJOR HABITATS:

FOREST:
- Trees provide shelter
- Many birds, insects, and mammals
- Examples: deer, owls, squirrels

DESERT:
- Very hot and dry
- Animals have special adaptations
- Examples: camels, lizards, scorpions

OCEAN:
- Salt water
- Many different zones
- Examples: whales, fish, octopus

GRASSLAND:
- Wide open spaces with grass
- Few trees
- Examples: lions, zebras, elephants

ARCTIC:
- Very cold and icy
- Animals have thick fur
- Examples: polar bears, penguins, seals

FRESHWATER:
- Rivers, lakes, ponds
- Important for drinking water
- Examples: frogs, fish, ducks

ADAPTATIONS:
Animals develop special features to survive in their habitat:
- Camels: store fat in humps for desert survival
- Fish: gills for breathing underwater
- Polar bears: thick fur for cold

PRACTICE:
1. Which habitat is very hot and dry? ___
2. Why do polar bears have thick fur? ___
3. Name an animal that lives in the ocean: ___`, order: 2, duration: 15 },
    { title: 'Food Chains', description: 'How energy flows from plants to animals',
      content: `FOOD CHAINS

A food chain shows how energy passes from one organism to another.

COMPONENTS OF A FOOD CHAIN:

PRODUCER:
- Makes its own food (plants)
- Base of every food chain
- Gets energy from sunlight

PRIMARY CONSUMER:
- Eats plants (herbivore)
- Examples: rabbits, grasshoppers

SECONDARY CONSUMER:
- Eats herbivores (carnivore)
- Examples: frogs, small birds

TERTIARY CONSUMER:
- Eats other carnivores
- Examples: eagles, sharks

DECOMPOSER:
- Breaks down dead organisms
- Returns nutrients to soil
- Examples: bacteria, fungi

EXAMPLE FOOD CHAIN:
Sun -> Grass -> Grasshopper -> Frog -> Snake -> Eagle

- Sun provides energy to grass
- Grasshopper eats grass
- Frog eats grasshopper
- Snake eats frog
- Eagle eats snake

ENERGY FLOW:
- Energy decreases at each level
- Only about 10% passes to the next level
- This is why there are fewer top predators than plants

PRACTICE:
1. What is at the start of every food chain? ___
2. A rabbit is a ___ consumer
3. What breaks down dead organisms? ___`, order: 3, duration: 15 }
  ],
  5: [
    { title: 'Reading Comprehension', description: 'Strategies to understand what you read',
      content: `READING COMPREHENSION

Reading comprehension means understanding and thinking about what you read.

BEFORE READING:
- Look at the title and pictures
- What do you think the text will be about?
- What do you already know about this topic?
- Set a purpose for reading

WHILE READING:
- Read slowly and carefully
- Picture what is happening in your mind
- Ask yourself questions
- Look up words you don't know
- Make connections to what you know

AFTER READING:
- What was the main idea?
- What happened first, next, and last?
- Can you retell the story in your own words?
- What did you learn?

IMPORTANT SKILLS:

MAIN IDEA:
The most important point the author wants to make

DETAILS:
Facts and examples that support the main idea

SEQUENCE:
The order events happen in

CAUSE AND EFFECT:
Why something happened and what resulted

VOCABULARY:
Meaning of words used in the text

TIPS:
- Practice reading every day
- Read different types of books
- Talk about what you read with others
- Write about what you read
- Use a dictionary for new words

PRACTICE:
1. What should you do BEFORE reading? ___
2. The main idea is the ___ point
3. Why is reading every day important? ___`, order: 1, duration: 10 }
  ]
};

const quizzesData = {
  0: [
    { lessonIndex: 0, title: 'Quiz: What is a Fraction?', passingScore: 60, questions: [
      { text: 'What is the top number of a fraction called?', options: [{ text: 'Denominator', isCorrect: false }, { text: 'Numerator', isCorrect: true }, { text: 'Divisor', isCorrect: false }, { text: 'Quotient', isCorrect: false }] },
      { text: 'What does 3/4 mean?', options: [{ text: '3 divided by 4', isCorrect: false }, { text: '3 parts out of 4 equal parts', isCorrect: true }, { text: '4 parts out of 3 equal parts', isCorrect: false }, { text: '3 wholes and 4 parts', isCorrect: false }] },
      { text: 'If you eat 2 slices of a pizza cut into 8 equal slices, what fraction did you eat?', options: [{ text: '2/8', isCorrect: true }, { text: '8/2', isCorrect: false }, { text: '2/6', isCorrect: false }, { text: '6/8', isCorrect: false }] },
      { text: 'Which fraction represents exactly one whole?', options: [{ text: '1/2', isCorrect: false }, { text: '3/4', isCorrect: false }, { text: '5/4', isCorrect: false }, { text: '4/4', isCorrect: true }] }
    ]},
    { lessonIndex: 1, title: 'Quiz: Equivalent Fractions', passingScore: 60, questions: [
      { text: 'Which fraction is equivalent to 1/2?', options: [{ text: '1/4', isCorrect: false }, { text: '2/3', isCorrect: false }, { text: '2/4', isCorrect: true }, { text: '3/4', isCorrect: false }] },
      { text: 'What is 2/3 equivalent to?', options: [{ text: '4/6', isCorrect: true }, { text: '3/5', isCorrect: false }, { text: '2/6', isCorrect: false }, { text: '3/4', isCorrect: false }] },
      { text: 'To find equivalent fractions, you can:', options: [{ text: 'Add the same number to numerator and denominator', isCorrect: false }, { text: 'Multiply numerator and denominator by the same number', isCorrect: true }, { text: 'Subtract the same number from both', isCorrect: false }, { text: 'Divide only the denominator', isCorrect: false }] },
      { text: 'Which is NOT equivalent to 3/4?', options: [{ text: '6/8', isCorrect: false }, { text: '9/12', isCorrect: false }, { text: '3/8', isCorrect: true }, { text: '12/16', isCorrect: false }] }
    ]},
    { lessonIndex: 2, title: 'Quiz: Comparing Fractions', passingScore: 60, questions: [
      { text: 'Which is larger: 3/8 or 5/8?', options: [{ text: '3/8', isCorrect: false }, { text: '5/8', isCorrect: true }, { text: 'They are equal', isCorrect: false }, { text: 'Cannot tell', isCorrect: false }] },
      { text: 'Compare 2/3 and 3/5 using cross multiplication. Which is larger?', options: [{ text: '2/3', isCorrect: true }, { text: '3/5', isCorrect: false }, { text: 'They are equal', isCorrect: false }, { text: 'Cannot compare', isCorrect: false }] },
      { text: 'Which symbol makes this true: 1/2 ___ 3/4?', options: [{ text: '>', isCorrect: false }, { text: '<', isCorrect: true }, { text: '=', isCorrect: false }, { text: 'None', isCorrect: false }] }
    ]},
    { lessonIndex: 3, title: 'Quiz: Adding Fractions', passingScore: 60, questions: [
      { text: 'What is 1/4 + 2/4?', options: [{ text: '3/8', isCorrect: false }, { text: '3/4', isCorrect: true }, { text: '2/8', isCorrect: false }, { text: '1/2', isCorrect: false }] },
      { text: 'What is 1/3 + 1/6?', options: [{ text: '1/2', isCorrect: true }, { text: '2/9', isCorrect: false }, { text: '2/6', isCorrect: false }, { text: '1/18', isCorrect: false }] },
      { text: 'When adding fractions with different denominators, you must first:', options: [{ text: 'Add the denominators', isCorrect: false }, { text: 'Find a common denominator', isCorrect: true }, { text: 'Multiply the fractions', isCorrect: false }, { text: 'Subtract the numerators', isCorrect: false }] }
    ]},
    { lessonIndex: 4, title: 'Quiz: Subtracting Fractions', passingScore: 60, questions: [
      { text: 'What is 5/8 - 3/8?', options: [{ text: '2/8', isCorrect: false }, { text: '1/4', isCorrect: true }, { text: '8/8', isCorrect: false }, { text: '2/16', isCorrect: false }] },
      { text: 'What is 3/4 - 1/3?', options: [{ text: '2/1', isCorrect: false }, { text: '5/12', isCorrect: true }, { text: '2/12', isCorrect: false }, { text: '4/7', isCorrect: false }] },
      { text: 'When subtracting fractions, you must:', options: [{ text: 'Always multiply first', isCorrect: false }, { text: 'Have the same denominator', isCorrect: true }, { text: 'Add the numerators', isCorrect: false }, { text: 'Flip the second fraction', isCorrect: false }] }
    ]},
    { lessonIndex: 5, title: 'Quiz: Multiplying Fractions', passingScore: 60, questions: [
      { text: 'What is 1/2 x 3/4?', options: [{ text: '3/8', isCorrect: true }, { text: '4/6', isCorrect: false }, { text: '5/6', isCorrect: false }, { text: '3/6', isCorrect: false }] },
      { text: 'To multiply fractions, you:', options: [{ text: 'Find a common denominator', isCorrect: false }, { text: 'Multiply numerators and denominators', isCorrect: true }, { text: 'Flip the second fraction', isCorrect: false }, { text: 'Add the fractions', isCorrect: false }] },
      { text: 'What is 2/3 x 5/6?', options: [{ text: '10/18 = 5/9', isCorrect: true }, { text: '7/9', isCorrect: false }, { text: '10/9', isCorrect: false }, { text: '7/18', isCorrect: false }] }
    ]},
    { lessonIndex: 6, title: 'Quiz: Dividing Fractions', passingScore: 60, questions: [
      { text: 'What is the "Keep, Change, Flip" rule used for?', options: [{ text: 'Adding fractions', isCorrect: false }, { text: 'Dividing fractions', isCorrect: true }, { text: 'Comparing fractions', isCorrect: false }, { text: 'Simplifying fractions', isCorrect: false }] },
      { text: 'What is 3/4 / 1/2?', options: [{ text: '3/8', isCorrect: false }, { text: '3/2', isCorrect: true }, { text: '6/4', isCorrect: false }, { text: '1/6', isCorrect: false }] },
      { text: 'Dividing by a fraction is the same as:', options: [{ text: 'Multiplying by the fraction', isCorrect: false }, { text: 'Multiplying by its reciprocal', isCorrect: true }, { text: 'Adding the fraction', isCorrect: false }, { text: 'Subtracting the fraction', isCorrect: false }] }
    ]}
  ],
  1: [
    { lessonIndex: 0, title: 'Quiz: What are Decimals?', passingScore: 60, questions: [
      { text: 'What is 0.5 as a fraction?', options: [{ text: '1/2', isCorrect: true }, { text: '1/5', isCorrect: false }, { text: '5/10', isCorrect: false }, { text: '1/10', isCorrect: false }] },
      { text: 'In the number 3.456, which digit is in the hundredths place?', options: [{ text: '3', isCorrect: false }, { text: '4', isCorrect: false }, { text: '5', isCorrect: true }, { text: '6', isCorrect: false }] },
      { text: 'What is 1/4 as a decimal?', options: [{ text: '0.1', isCorrect: false }, { text: '0.25', isCorrect: true }, { text: '0.75', isCorrect: false }, { text: '0.5', isCorrect: false }] }
    ]},
    { lessonIndex: 1, title: 'Quiz: Comparing Decimals', passingScore: 60, questions: [
      { text: 'Which is larger: 0.3 or 0.25?', options: [{ text: '0.25', isCorrect: false }, { text: '0.3', isCorrect: true }, { text: 'They are equal', isCorrect: false }, { text: 'Cannot tell', isCorrect: false }] },
      { text: 'Compare 1.5 and 1.50:', options: [{ text: '1.5 > 1.50', isCorrect: false }, { text: '1.5 < 1.50', isCorrect: false }, { text: '1.5 = 1.50', isCorrect: true }, { text: 'Cannot compare', isCorrect: false }] },
      { text: 'Which is smaller: 0.8 or 0.79?', options: [{ text: '0.8', isCorrect: false }, { text: '0.79', isCorrect: true }, { text: 'They are equal', isCorrect: false }, { text: 'Cannot tell', isCorrect: false }] }
    ]},
    { lessonIndex: 2, title: 'Quiz: Adding and Subtracting Decimals', passingScore: 60, questions: [
      { text: 'When adding decimals, what must you line up?', options: [{ text: 'The whole numbers only', isCorrect: false }, { text: 'The decimal points', isCorrect: true }, { text: 'The last digits', isCorrect: false }, { text: 'The first digits', isCorrect: false }] },
      { text: 'What is 4.5 + 2.3?', options: [{ text: '6.8', isCorrect: true }, { text: '6.08', isCorrect: false }, { text: '0.68', isCorrect: false }, { text: '68', isCorrect: false }] },
      { text: 'What is 7.8 - 3.45?', options: [{ text: '4.45', isCorrect: true }, { text: '4.35', isCorrect: false }, { text: '4.3', isCorrect: false }, { text: '3.35', isCorrect: false }] }
    ]}
  ],
  2: [
    { lessonIndex: 0, title: 'Quiz: 2D Shapes', passingScore: 60, questions: [
      { text: 'How many sides does a triangle have?', options: [{ text: '2', isCorrect: false }, { text: '3', isCorrect: true }, { text: '4', isCorrect: false }, { text: '5', isCorrect: false }] },
      { text: 'A square has how many right angles?', options: [{ text: '2', isCorrect: false }, { text: '3', isCorrect: false }, { text: '4', isCorrect: true }, { text: '1', isCorrect: false }] },
      { text: 'Which shape has 6 sides?', options: [{ text: 'Pentagon', isCorrect: false }, { text: 'Hexagon', isCorrect: true }, { text: 'Octagon', isCorrect: false }, { text: 'Square', isCorrect: false }] }
    ]},
    { lessonIndex: 1, title: 'Quiz: 3D Shapes', passingScore: 60, questions: [
      { text: 'How many faces does a cube have?', options: [{ text: '4', isCorrect: false }, { text: '6', isCorrect: true }, { text: '8', isCorrect: false }, { text: '12', isCorrect: false }] },
      { text: 'A sphere is perfectly:', options: [{ text: 'Flat', isCorrect: false }, { text: 'Square', isCorrect: false }, { text: 'Round', isCorrect: true }, { text: 'Triangular', isCorrect: false }] },
      { text: 'How many circular faces does a cylinder have?', options: [{ text: '1', isCorrect: false }, { text: '2', isCorrect: true }, { text: '3', isCorrect: false }, { text: '0', isCorrect: false }] }
    ]},
    { lessonIndex: 2, title: 'Quiz: Perimeter and Area', passingScore: 60, questions: [
      { text: 'What is the perimeter of a rectangle with length 6 and width 4?', options: [{ text: '10', isCorrect: false }, { text: '20', isCorrect: true }, { text: '24', isCorrect: false }, { text: '12', isCorrect: false }] },
      { text: 'What is the area of a square with side 5?', options: [{ text: '10', isCorrect: false }, { text: '20', isCorrect: false }, { text: '25', isCorrect: true }, { text: '15', isCorrect: false }] },
      { text: 'Area is measured in:', options: [{ text: 'Units', isCorrect: false }, { text: 'Square units', isCorrect: true }, { text: 'Cubic units', isCorrect: false }, { text: 'Lines', isCorrect: false }] }
    ]}
  ],
  3: [
    { lessonIndex: 0, title: 'Quiz: Parts of a Plant', passingScore: 60, questions: [
      { text: 'Which part of the plant absorbs water from the soil?', options: [{ text: 'Leaves', isCorrect: false }, { text: 'Stem', isCorrect: false }, { text: 'Roots', isCorrect: true }, { text: 'Flowers', isCorrect: false }] },
      { text: 'What is the main function of leaves?', options: [{ text: 'Absorb water', isCorrect: false }, { text: 'Support the plant', isCorrect: false }, { text: 'Make food through photosynthesis', isCorrect: true }, { text: 'Produce seeds', isCorrect: false }] },
      { text: 'Which part of the plant produces seeds?', options: [{ text: 'Roots', isCorrect: false }, { text: 'Stem', isCorrect: false }, { text: 'Leaves', isCorrect: false }, { text: 'Flowers', isCorrect: true }] }
    ]},
    { lessonIndex: 1, title: 'Quiz: Photosynthesis', passingScore: 60, questions: [
      { text: 'What does a plant need for photosynthesis?', options: [{ text: 'Only water', isCorrect: false }, { text: 'Sunlight, water, and carbon dioxide', isCorrect: true }, { text: 'Only sunlight', isCorrect: false }, { text: 'Soil and oxygen', isCorrect: false }] },
      { text: 'What do plants release during photosynthesis?', options: [{ text: 'Carbon dioxide', isCorrect: false }, { text: 'Water', isCorrect: false }, { text: 'Oxygen', isCorrect: true }, { text: 'Nitrogen', isCorrect: false }] },
      { text: 'Where does photosynthesis happen in a leaf?', options: [{ text: 'Roots', isCorrect: false }, { text: 'Chloroplasts', isCorrect: true }, { text: 'Stem', isCorrect: false }, { text: 'Flowers', isCorrect: false }] }
    ]},
    { lessonIndex: 2, title: 'Quiz: Plant Life Cycles', passingScore: 60, questions: [
      { text: 'What is the first stage of a plant life cycle?', options: [{ text: 'Flower', isCorrect: false }, { text: 'Seed', isCorrect: true }, { text: 'Fruit', isCorrect: false }, { text: 'Leaf', isCorrect: false }] },
      { text: 'What happens during germination?', options: [{ text: 'The plant produces flowers', isCorrect: false }, { text: 'The seed absorbs water and begins to grow', isCorrect: true }, { text: 'The plant dies', isCorrect: false }, { text: 'Seeds are spread', isCorrect: false }] },
      { text: 'Which type of plant lives for many years?', options: [{ text: 'Annual', isCorrect: false }, { text: 'Biennial', isCorrect: false }, { text: 'Perennial', isCorrect: true }, { text: 'Seedling', isCorrect: false }] }
    ]}
  ],
  4: [
    { lessonIndex: 0, title: 'Quiz: Animal Classification', passingScore: 60, questions: [
      { text: 'Which group do humans belong to?', options: [{ text: 'Birds', isCorrect: false }, { text: 'Reptiles', isCorrect: false }, { text: 'Mammals', isCorrect: true }, { text: 'Fish', isCorrect: false }] },
      { text: 'What characteristic do all mammals share?', options: [{ text: 'They can fly', isCorrect: false }, { text: 'They have scales', isCorrect: false }, { text: 'They feed their babies milk', isCorrect: true }, { text: 'They live in water', isCorrect: false }] },
      { text: 'Which animals are cold-blooded?', options: [{ text: 'Dogs and cats', isCorrect: false }, { text: 'Eagles and penguins', isCorrect: false }, { text: 'Snakes and lizards', isCorrect: true }, { text: 'Humans and elephants', isCorrect: false }] }
    ]},
    { lessonIndex: 1, title: 'Quiz: Animal Habitats', passingScore: 60, questions: [
      { text: 'Which habitat is very hot and dry?', options: [{ text: 'Forest', isCorrect: false }, { text: 'Desert', isCorrect: true }, { text: 'Ocean', isCorrect: false }, { text: 'Arctic', isCorrect: false }] },
      { text: 'Why do polar bears have thick fur?', options: [{ text: 'To swim faster', isCorrect: false }, { text: 'To stay warm in cold habitats', isCorrect: true }, { text: 'To fly', isCorrect: false }, { text: 'To hide', isCorrect: false }] },
      { text: 'Which animal lives in the ocean?', options: [{ text: 'Camel', isCorrect: false }, { text: 'Polar bear', isCorrect: false }, { text: 'Whale', isCorrect: true }, { text: 'Lion', isCorrect: false }] }
    ]},
    { lessonIndex: 2, title: 'Quiz: Food Chains', passingScore: 60, questions: [
      { text: 'What is at the start of every food chain?', options: [{ text: 'A predator', isCorrect: false }, { text: 'A producer (plant)', isCorrect: true }, { text: 'A decomposer', isCorrect: false }, { text: 'Water', isCorrect: false }] },
      { text: 'A rabbit that eats grass is a:', options: [{ text: 'Secondary consumer', isCorrect: false }, { text: 'Primary consumer', isCorrect: true }, { text: 'Producer', isCorrect: false }, { text: 'Decomposer', isCorrect: false }] },
      { text: 'What breaks down dead organisms?', options: [{ text: 'Herbivores', isCorrect: false }, { text: 'Carnivores', isCorrect: false }, { text: 'Decomposers', isCorrect: true }, { text: 'Producers', isCorrect: false }] }
    ]}
  ],
  5: [
    { lessonIndex: 0, title: 'Quiz: Reading Comprehension', passingScore: 60, questions: [
      { text: 'What should you do BEFORE reading a text?', options: [{ text: 'Skip to the end', isCorrect: false }, { text: 'Look at the title and pictures', isCorrect: true }, { text: 'Close the book', isCorrect: false }, { text: 'Read very fast', isCorrect: false }] },
      { text: 'The main idea is the:', options: [{ text: 'Smallest detail', isCorrect: false }, { text: 'Most important point', isCorrect: true }, { text: 'Last sentence only', isCorrect: false }, { text: 'Title of the book', isCorrect: false }] },
      { text: 'Why is reading every day important?', options: [{ text: 'It is not important', isCorrect: false }, { text: 'It helps improve your skills over time', isCorrect: true }, { text: 'Teachers require it', isCorrect: false }, { text: 'Books are expensive', isCorrect: false }] }
    ]}
  ]
};

function seed() {
  console.log('Seeding database...');

  db.exec('DELETE FROM enrollments');
  db.exec('DELETE FROM sync_operations');
  db.exec('DELETE FROM assessments');
  db.exec('DELETE FROM progress');
  db.exec('DELETE FROM quizzes');
  db.exec('DELETE FROM lessons');
  db.exec('DELETE FROM courses');
  db.exec('DELETE FROM users');

  const insertUser = db.prepare('INSERT INTO users (name, email, password, role, grade, school) VALUES (?, ?, ?, ?, ?, ?)');
  const userIds = {};
  for (const u of users) {
    const hashed = bcrypt.hashSync(u.password, 12);
    const result = insertUser.run(u.name, u.email, hashed, u.role, u.grade || null, u.school || null);
    userIds[u.email] = result.lastInsertRowid;
    console.log(`  User: ${u.name} (${u.role})`);
  }

  const teacherId = userIds['amina@learningbox.org'];

  const insertCourse = db.prepare('INSERT INTO courses (title, description, grade, subject, published, createdBy) VALUES (?, ?, ?, ?, ?, ?)');
  const courseIds = {};
  for (let i = 0; i < courses.length; i++) {
    const c = courses[i];
    const result = insertCourse.run(c.title, c.description, c.grade, c.subject, c.published ? 1 : 0, teacherId);
    courseIds[i] = result.lastInsertRowid;
    console.log(`  Course: ${c.title}`);
  }

  const insertLesson = db.prepare('INSERT INTO lessons (courseId, title, description, content, "order", duration) VALUES (?, ?, ?, ?, ?, ?)');
  const lessonIds = {};
  for (const [courseIdx, lessons] of Object.entries(lessonsData)) {
    lessonIds[courseIdx] = [];
    for (const l of lessons) {
      const result = insertLesson.run(courseIds[courseIdx], l.title, l.description, l.content, l.order, l.duration);
      lessonIds[courseIdx].push(result.lastInsertRowid);
      console.log(`    Lesson: ${l.title}`);
    }
  }

  const insertQuiz = db.prepare('INSERT INTO quizzes (lessonId, title, questions, passingScore) VALUES (?, ?, ?, ?)');
  for (const [courseIdx, quizzes] of Object.entries(quizzesData)) {
    for (const q of quizzes) {
      const lessonId = lessonIds[courseIdx][q.lessonIndex];
      insertQuiz.run(lessonId, q.title, JSON.stringify(q.questions), q.passingScore);
      console.log(`      Quiz: ${q.title}`);
    }
  }

  console.log('\nDone! Credentials:');
  console.log('  Admin:   admin@learningbox.org / admin123');
  console.log('  Teacher: amina@learningbox.org / teacher123');
  console.log('  Student: james@student.com / student123');
  console.log('  Student: nyamal@student.com / student123');
  console.log('  Student: peter@student.com / student123');
}

seed();
