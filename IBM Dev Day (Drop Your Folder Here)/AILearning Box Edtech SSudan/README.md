# Learning Box

## The Problem

South Sudan faces a severe education crisis — decades of conflict have destroyed infrastructure, displaced millions, and left the country with some of the lowest literacy rates in the world. Schools lack textbooks, trained teachers, and basic learning materials. The few existing digital education platforms assume constant internet access, modern devices, and English-only interfaces — none of which reflect the reality in South Sudan. Students in rural and conflict-affected areas have no reliable way to access structured learning content, track their progress, or receive personalized guidance.

## Our Solution

Learning Box is an offline-first, multilingual learning platform built specifically for underserved communities in South Sudan. It works without internet, speaks both Arabic and English, and adapts to each student's skill level through diagnostic assessments and personalized learning paths. Teachers and administrators can manage content and monitor student progress through role-based dashboards — all running on low-cost hardware with no cloud dependency.

**Key differentiators:**
- Works fully offline with background sync when connectivity returns
- Native Arabic and English support for South Sudan's bilingual context
- Diagnostic engine identifies weak topics and auto-generates targeted learning paths
- Designed for low-bandwidth, low-resource environments
- South Sudan-themed UI reflecting national identity and pride

## Features

- **Diagnostic Assessment** — Generates topic-level diagnostic quizzes, analyzes results, and creates adaptive learning paths (needs review / practice recommended / mastered)
- **Adaptive Learning Paths** — Links directly to lessons and quizzes based on assessment performance
- **Progress Tracking** — Per-lesson completion, per-course progress bars, quiz scores, and overall stats
- **Offline-First PWA** — Service worker caches assets; IndexedDB queues progress changes for background sync when back online
- **Arabic / English i18n** — Full translations with one-click language switcher
- **Role-Based Access** — Student, Teacher, and Admin dashboards with different views and permissions
- **South Sudan Theme** — Flag-inspired color palette (black, red, green, blue, gold) with gradient headers, glass cards, and smooth animations

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite 8, Tailwind CSS 4, React Router 7 |
| Backend | Express 4, SQLite (better-sqlite3), JWT auth |
| Offline | Dexie (IndexedDB), vite-plugin-pwa (service worker) |
| Security | Helmet, CORS, express-rate-limit, input sanitization |
| i18n | Custom context provider with `en` and `ar` translations |

## Getting Started

### Prerequisites

- Node.js 18+
- npm

### Quick Start

```bash
# Install dependencies
npm install
cd client && npm install && cd ..
cd server && npm install && cd ..

# Seed the database
cd server && npm run seed && cd ..

# Start both (from root)
cd server && npm run dev &   # API on :5000
cd client && npm run dev     # UI on :5173
```

### Docker

```bash
docker-compose up --build
```

Server runs on `:5000`, client on `:5173`.

## Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@learningbox.org | admin123 |
| Teacher | amina@learningbox.org | teacher123 |
| Student | james@student.com | student123 |
| Student | nyamal@student.com | student123 |
| Student | peter@student.com | student123 |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/courses` | List courses |
| POST | `/api/courses` | Create course (admin/teacher) |
| GET | `/api/courses/:id` | Get course with lessons |
| PUT | `/api/courses/:id` | Update course |
| DELETE | `/api/courses/:id` | Delete course |
| GET | `/api/lessons/:id` | Get lesson content |
| GET | `/api/quizzes/lesson/:id` | Get quiz for lesson |
| POST | `/api/quizzes/:id/submit` | Submit quiz answers |
| GET | `/api/progress` | Get student progress |
| GET | `/api/progress/courses` | All courses with progress |
| GET | `/api/progress/course/:id` | Per-course progress detail |
| GET | `/api/assessment/courses` | List assessable courses |
| GET | `/api/assessment/diagnostic/:course` | Generate diagnostic quiz |
| POST | `/api/assessment/diagnostic/:course/submit` | Submit + get learning path |

## Project Structure

```
AI-Learning-Box/
├── client/                 # React frontend
│   └── src/
│       ├── components/     # OfflineIndicator, LanguageSwitcher
│       ├── db/             # Dexie IndexedDB schema
│       ├── hooks/          # useAuth, useOffline
│       ├── i18n/           # Arabic/English translations
│       ├── layouts/        # Layout with navbar
│       ├── pages/          # Dashboard, Course, Lesson, Quiz, Assessment, Admin, Teacher
│       └── services/       # Axios API client
├── server/                 # Express backend
│   └── src/
│       ├── config/         # SQLite schema
│       ├── controllers/    # Route handlers
│       ├── middleware/      # Auth, rate limiting, sanitization
│       ├── models/         # Database queries
│       ├── routes/         # API routes
│       ├── services/       # Assessment engine
│       └── seed.js         # Database seeder
└── shared/                 # Shared types/constants
```

## Seeded Content

6 courses (Mathematics, Science, English) with 20 lessons, 6 quizzes, and 50+ diagnostic questions across topics like fractions, decimals, geometry, plants, animals, and reading comprehension.

## Future Improvements

### Short-Term
- **AI Tutor Integration** — Context-aware Q&A assistant using local or cloud LLMs to answer student questions in Arabic and English
- **Quiz Auto-Generation** — Generate quizzes from lesson content using AI, reducing manual content creation burden
- **Multilingual Content** — Extend i18n to Nuer, Dinka, and other local languages spoken across South Sudan
- **Rich Media Support** — Audio lessons and illustrated content for students with limited reading proficiency
- **Bulk Content Import** — CSV/JSON upload for teachers to create courses and lessons in bulk

### Medium-Term
- **Peer-to-Peer Sync** — Device-to-device content sharing via Bluetooth/Wi-Fi Direct for areas with zero connectivity
- **Teacher Analytics Dashboard** — Class-wide performance insights, at-risk student identification, and intervention recommendations
- **Offline SCORM/xAPI** — Import existing OpenStax and Khan Academy content packages
- **Parent Portal** — Simplified view for parents to track their child's learning progress via SMS or USSD
- **Assessment Reports** — PDF export of student progress reports for school administrators

### Long-Term
- **Solar-Powered Learning Box** — Bundle the platform with Raspberry Pi, solar panel, and local Wi-Fi hotspot for deployment in off-grid schools
- **Curriculum Alignment** — Map all content to South Sudan's national curriculum standards
- **Community Content Contributions** — Allow teachers to author and publish lessons directly from the platform
- **Impact Measurement** — Longitudinal analytics to measure learning outcomes across regions
- **UNICEF/NGO Integration** — API for education NGOs to push targeted content and pull progress data for reporting


# Team                             Github username
Brian Kiprono                       krispytank
Melanie Kibet                       not-zendaya 
Alvin Sure                          alivinliberite


## License
MIT
