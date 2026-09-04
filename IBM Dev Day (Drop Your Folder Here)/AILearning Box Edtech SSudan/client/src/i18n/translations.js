const en = {
  app: { name: 'Learning Box', tagline: 'Offline-First Education' },
  auth: {
    login: 'Sign In',
    register: 'Create Account',
    email: 'Email',
    password: 'Password',
    name: 'Full Name',
    grade: 'Grade',
    school: 'School',
    noAccount: "Don't have an account?",
    hasAccount: 'Already have an account?',
    signUp: 'Register',
    signIn: 'Sign in'
  },
  nav: {
    dashboard: 'Dashboard',
    admin: 'Admin',
    analytics: 'Analytics',
    logout: 'Logout',
    assessment: 'Assessment'
  },
  student: {
    title: 'Continue Learning',
    noCourses: 'No courses available yet.',
    availableOffline: 'Available Offline',
    downloadForOffline: 'Download for Offline',
    downloading: 'Downloading...',
    remove: 'Remove',
    lessons: 'lessons',
    selfPaced: 'Self-paced',
    markComplete: 'Mark Complete',
    takeQuiz: 'Take Quiz',
    saving: 'Saving...',
    viewLesson: 'View Lesson',
    startLesson: 'Start Lesson'
  },
  admin: {
    title: 'Content Management',
    newCourse: '+ New Course',
    courseTitle: 'Title',
    courseDescription: 'Description',
    courseGrade: 'Grade',
    courseSubject: 'Subject',
    createCourse: 'Create Course',
    published: 'Published',
    draft: 'Draft',
    publish: 'Publish',
    unpublish: 'Unpublish',
    cancel: 'Cancel'
  },
  teacher: {
    title: 'Teacher Dashboard',
    students: 'Students',
    publishedCourses: 'Published Courses',
    avgProgress: 'Avg Progress',
    studentProgress: 'Student Progress',
    noData: 'No student data yet',
    overall: 'Overall'
  },
  quiz: {
    submit: 'Submit Quiz',
    submitting: 'Submitting...',
    passed: 'Congratulations! You passed!',
    failed: 'Keep practicing!',
    correct: 'out of correct',
    passing: 'passing',
    backToDashboard: 'Back to Dashboard'
  },
  assessment: {
    title: 'Assessment',
    subtitle: 'Find your level and get a personalized learning path',
    selectCourse: 'Select a Course',
    startAssessment: 'Start Assessment',
    question: 'Question',
    of: 'of',
    submitAssessment: 'Submit Assessment',
    submitting: 'Submitting...',
    yourScore: 'Your Score',
    topicResults: 'Topic Breakdown',
    learningPath: 'Your Learning Path',
    needsReview: 'Needs Review',
    practiceRecommended: 'Practice Recommended',
    mastered: 'Mastered',
    startLesson: 'Start Lesson',
    viewLesson: 'View Lesson',
    noAssessment: 'Take an assessment first',
    takeAgain: 'Retake Assessment',
    history: 'Assessment History',
    topics: 'topics',
    resources: 'Learning Resources',
    resourceDesc: 'Lessons to help you improve',
    recommendedForYou: 'Recommended for you',
    basedOnScore: 'Based on your assessment score',
    viewResources: 'View Resources',
    improveSkills: 'Improve your skills with these lessons',
    lessonContent: 'Lesson Content',
    quizAvailable: 'Quiz Available',
    previousScore: 'Previous Score'
  },
  offline: {
    syncing: 'Syncing',
    pendingChange: 'pending change',
    pendingChanges: 'pending changes',
    offlineMessage: 'Progress saved locally',
    waitingSync: 'waiting to sync'
  },
  progress: {
    overall: 'Overall Progress',
    coursesStarted: 'Courses Started',
    lessonsCompleted: 'Lessons Completed',
    avgScore: 'Avg Quiz Score'
  },
  common: {
    loading: 'Loading...',
    notFound: 'Not found',
    error: 'Something went wrong',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    cancel: 'Cancel',
    confirm: 'Confirm',
    back: 'Back'
  }
};

const ar = {
  app: { name: 'صندوق التعلم', tagline: 'تعليم يعمل بدون إنترنت' },
  auth: {
    login: 'تسجيل الدخول',
    register: 'إنشاء حساب',
    email: 'البريد الإلكتروني',
    password: 'كلمة المرور',
    name: 'الاسم الكامل',
    grade: 'الصف',
    school: 'المدرسة',
    noAccount: 'ليس لديك حساب؟',
    hasAccount: 'لديك حساب بالفعل؟',
    signUp: 'تسجيل',
    signIn: 'دخول'
  },
  nav: {
    dashboard: 'لوحة التحكم',
    admin: 'الإدارة',
    analytics: 'التحليلات',
    logout: 'خروج',
    assessment: 'التقييم'
  },
  student: {
    title: 'تابع التعلم',
    noCourses: 'لا توجد دورات متاحة.',
    availableOffline: 'متاح بدون إنترنت',
    downloadForOffline: 'تحميل للعمل بدون إنترنت',
    downloading: 'جاري التحميل...',
    remove: 'إزالة',
    lessons: 'دروس',
    selfPaced: 'بالسرعة المناسبة',
    markComplete: 'تحديد كمكتمل',
    takeQuiz: 'اختبار',
    saving: 'جاري الحفظ...',
    viewLesson: 'عرض الدرس',
    startLesson: 'ابدأ الدرس'
  },
  admin: {
    title: 'إدارة المحتوى',
    newCourse: '+ دورة جديدة',
    courseTitle: 'العنوان',
    courseDescription: 'الوصف',
    courseGrade: 'الصف',
    courseSubject: 'المادة',
    createCourse: 'إنشاء دورة',
    published: 'منشور',
    draft: 'مسودة',
    publish: 'نشر',
    unpublish: 'إلغاء النشر',
    cancel: 'إلغاء'
  },
  teacher: {
    title: 'لوحة تحكم المعلم',
    students: 'الطلاب',
    publishedCourses: 'الدورات المنشورة',
    avgProgress: 'متوسط التقدم',
    studentProgress: 'تقدم الطلاب',
    noData: 'لا توجد بيانات بعد',
    overall: 'العام'
  },
  quiz: {
    submit: 'إرسال الاختبار',
    submitting: 'جاري الإرسال...',
    passed: 'مبروك! لقد نجحت!',
    failed: 'واصل التدريب!',
    correct: 'من أصل صحيح',
    passing: 'النجاح',
    backToDashboard: 'العودة للوحة التحكم'
  },
  assessment: {
    title: 'التقييم',
    subtitle: 'اكتشف مستواك واحصل على مسار تعلم مخصص',
    selectCourse: 'اختر دورة',
    startAssessment: 'ابدأ التقييم',
    question: 'سؤال',
    of: 'من',
    submitAssessment: 'إرسال التقييم',
    submitting: 'جاري الإرسال...',
    yourScore: 'نتيجتك',
    topicResults: 'تفاصيل المواضيع',
    learningPath: 'مسار التعلم الخاص بك',
    needsReview: 'يحتاج مراجعة',
    practiceRecommended: 'يُنصح بالتدريب',
    mastered: 'مُتقن',
    startLesson: 'ابدأ الدرس',
    viewLesson: 'عرض الدرس',
    noAssessment: 'قم بتقييم أولاً',
    takeAgain: 'إعادة التقييم',
    history: 'سجل التقييمات',
    topics: 'مواضيع',
    resources: 'موارد التعلم',
    resourceDesc: 'دروس لمساعدتك على التحسن',
    recommendedForYou: 'موصى بها لك',
    basedOnScore: 'بناءً على نتيجتك',
    viewResources: 'عرض الموارد',
    improveSkills: 'حسّن مهاراتك بهذه الدروس',
    lessonContent: 'محتوى الدرس',
    quizAvailable: 'اختبار متاح',
    previousScore: 'النتيجة السابقة'
  },
  offline: {
    syncing: 'جاري المزامنة',
    pendingChange: 'تغيير معلق',
    pendingChanges: 'تغييرات معلقة',
    offlineMessage: 'يتم حفظ التقدم محلياً',
    waitingSync: 'تغييرات للمزامنة'
  },
  progress: {
    overall: 'التقدم العام',
    coursesStarted: 'الدورات المبدأة',
    lessonsCompleted: 'الدروس المكتملة',
    avgScore: 'متوسط درجات الاختبارات'
  },
  common: {
    loading: 'جاري التحميل...',
    notFound: 'غير موجود',
    error: 'حدث خطأ',
    save: 'حفظ',
    delete: 'حذف',
    edit: 'تعديل',
    cancel: 'إلغاء',
    confirm: 'تأكيد',
    back: 'رجوع'
  }
};

export const translations = { en, ar };
export const languages = [
  { code: 'en', label: 'English', dir: 'ltr' },
  { code: 'ar', label: 'العربية', dir: 'rtl' }
];
