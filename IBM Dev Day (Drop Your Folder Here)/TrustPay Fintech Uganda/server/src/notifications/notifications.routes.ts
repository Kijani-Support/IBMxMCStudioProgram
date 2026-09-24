import { Router } from 'express';
import { Role } from '../types/domain';
import { authenticate, requireRole } from '../middleware/auth';
import * as notificationsController from './notifications.controller';

export const notificationsRouter = Router();

notificationsRouter.use(authenticate, requireRole(Role.RIDER));

notificationsRouter.get('/', notificationsController.list);
notificationsRouter.patch('/:id/read', notificationsController.markRead);
