import { Router } from 'express';
import { Role } from '../types/domain';
import { authenticate, requireRole } from '../middleware/auth';
import * as usersController from './users.controller';

export const ridersRouter = Router();

ridersRouter.get('/', authenticate, requireRole(Role.BUSINESS), usersController.listRiders);
