import { Request, Response, NextFunction } from 'express';
import { requireUser } from '../middleware/auth';
import { notificationService } from './notifications.service';

export async function list(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const user = requireUser(req);
    const unreadOnly = req.query.unread === 'true';
    const notifications = await notificationService.listForRider(user.id, unreadOnly);
    res.status(200).json({ notifications });
  } catch (error) {
    next(error);
  }
}

export async function markRead(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const user = requireUser(req);
    const notification = await notificationService.markRead(req.params.id as string, user.id);
    res.status(200).json({ notification });
  } catch (error) {
    next(error);
  }
}
