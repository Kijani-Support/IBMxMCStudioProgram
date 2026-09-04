import Dexie from 'dexie';

const db = new Dexie('LearningBox');

db.version(1).stores({
  courses: '++id, serverId, title, grade, subject, downloaded',
  lessons: '++id, serverId, courseId, order',
  quizzes: '++id, serverId, lessonId',
  progress: '++id, [courseId+lessonId], synced',
  syncQueue: '++id, type, synced, createdAt',
  downloads: '++id, courseId, url, type',
  user: 'id'
});

export default db;

export const offlineStorage = {
  async saveCourse(course, lessons, quizzes) {
    const courseId = await db.courses.add({
      serverId: course._id,
      title: course.title,
      grade: course.grade,
      subject: course.subject,
      description: course.description,
      thumbnail: course.thumbnail,
      downloaded: true,
      downloadedAt: new Date().toISOString()
    });

    for (const lesson of lessons) {
      const lessonId = await db.lessons.add({
        serverId: lesson._id,
        courseId,
        title: lesson.title,
        content: lesson.content,
        video: lesson.video,
        audio: lesson.audio,
        documents: lesson.documents || [],
        order: lesson.order,
        duration: lesson.duration
      });

      if (lesson.quiz) {
        await db.quizzes.add({
          serverId: lesson.quiz._id,
          lessonId,
          title: lesson.quiz.title,
          questions: lesson.quiz.questions,
          passingScore: lesson.quiz.passingScore
        });
      }
    }

    return courseId;
  },

  async getCourses() {
    return await db.courses.toArray();
  },

  async getLessons(courseId) {
    return await db.lessons.where('courseId').equals(courseId).sortBy('order');
  },

  async getQuiz(lessonId) {
    return await db.quizzes.where('lessonId').equals(lessonId).first();
  },

  async saveProgress(courseId, lessonId, data) {
    const existing = await db.progress
      .where('[courseId+lessonId]')
      .equals([courseId, lessonId])
      .first();

    if (existing) {
      await db.progress.update(existing.id, { ...data, synced: false });
    } else {
      await db.progress.add({
        courseId,
        lessonId,
        ...data,
        synced: false,
        createdAt: new Date().toISOString()
      });
    }
  },

  async addToSyncQueue(operation) {
    return await db.syncQueue.add({
      ...operation,
      synced: false,
      createdAt: new Date().toISOString(),
      retryCount: 0
    });
  },

  async getPendingSync() {
    return await db.syncQueue.where('synced').equals(0).toArray();
  },

  async markSynced(id) {
    await db.syncQueue.update(id, { synced: 1, syncedAt: new Date().toISOString() });
  },

  async removeSynced() {
    await db.syncQueue.where('synced').equals(1).delete();
  }
};
