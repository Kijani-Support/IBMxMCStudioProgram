import { useState, useEffect, useCallback } from 'react';
import db, { offlineStorage } from '../db/dexie';
import api from '../services/api';

export function useOfflineSync() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isSyncing, setIsSyncing] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useEffect(() => {
    const updatePending = async () => {
      const pending = await db.syncQueue.where('synced').equals(0).count();
      setPendingCount(pending);
    };
    updatePending();
    const interval = setInterval(updatePending, 5000);
    return () => clearInterval(interval);
  }, []);

  const syncPending = useCallback(async () => {
    if (!isOnline || isSyncing) return;

    setIsSyncing(true);
    try {
      const pending = await offlineStorage.getPendingSync();
      if (pending.length === 0) {
        setIsSyncing(false);
        return;
      }

      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const operations = pending.map(op => ({
        type: op.type,
        ...op.payload
      }));

      const res = await api.post('/sync', {
        deviceId: getDeviceId(),
        lastSync: null,
        operations
      });

      if (res.data.success) {
        for (const op of pending) {
          await offlineStorage.markSynced(op.id);
        }
        await offlineStorage.removeSynced();
      }
    } catch (error) {
      console.error('Sync failed:', error);
    }
    setIsSyncing(false);
  }, [isOnline, isSyncing]);

  useEffect(() => {
    if (isOnline) {
      syncPending();
    }
  }, [isOnline, syncPending]);

  return { isOnline, isSyncing, pendingCount, syncPending };
}

export function useDownloadedCourse(courseId) {
  const [downloaded, setDownloaded] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    db.courses.where('serverId').equals(courseId).first().then(c => {
      setDownloaded(!!c?.downloaded);
    });
  }, [courseId]);

  const download = async () => {
    setDownloading(true);
    setProgress(0);
    try {
      const courseRes = await api.get(`/courses/${courseId}`);
      const course = courseRes.data;
      const lessons = course.lessons || [];

      setProgress(20);
      await offlineStorage.saveCourse(course, lessons, []);
      setProgress(100);
      setDownloaded(true);
    } catch (error) {
      console.error('Download failed:', error);
    }
    setDownloading(false);
  };

  const remove = async () => {
    const course = await db.courses.where('serverId').equals(courseId).first();
    if (course) {
      await db.lessons.where('courseId').equals(course.id).delete();
      await db.quizzes.where('lessonId').anyOf(
        (await db.lessons.where('courseId').equals(course.id).toArray()).map(l => l.id)
      ).delete();
      await db.courses.delete(course.id);
      setDownloaded(false);
    }
  };

  return { downloaded, downloading, progress, download, remove };
}

export function useOfflineProgress() {
  const saveProgress = async (courseId, lessonId, data) => {
    const serverCourseId = courseId?._id || courseId;
    const serverLessonId = lessonId?._id || lessonId;

    try {
      await api.post('/progress', {
        courseId: serverCourseId,
        lessonId: serverLessonId,
        ...data
      });
    } catch {
      await offlineStorage.saveProgress(serverCourseId, serverLessonId, data);
      await offlineStorage.addToSyncQueue({
        type: 'LESSON_PROGRESS',
        payload: {
          courseId: serverCourseId,
          lessonId: serverLessonId,
          ...data
        }
      });
    }
  };

  const submitQuizOffline = async (quiz, answers, courseId, lessonId) => {
    let correct = 0;
    quiz.questions.forEach((q, idx) => {
      if (q.options[answers[idx]]?.isCorrect) correct++;
    });
    const score = Math.round((correct / quiz.questions.length) * 100);

    const serverCourseId = courseId?._id || courseId;
    const serverLessonId = lessonId?._id || lessonId;

    try {
      await api.post(`/quizzes/${quiz._id}/submit`, { answers });
    } catch {
      await offlineStorage.saveProgress(serverCourseId, serverLessonId, {
        completed: true,
        percentage: 100,
        quizScore: score
      });
      await offlineStorage.addToSyncQueue({
        type: 'QUIZ_RESULT',
        payload: { quizId: quiz._id || quiz.serverId, score, courseId: serverCourseId, lessonId: serverLessonId }
      });
    }

    return { score, passed: score >= quiz.passingScore, correct, total: quiz.questions.length };
  };

  return { saveProgress, submitQuizOffline };
}

function getDeviceId() {
  let id = localStorage.getItem('deviceId');
  if (!id) {
    id = 'device_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('deviceId', id);
  }
  return id;
}
