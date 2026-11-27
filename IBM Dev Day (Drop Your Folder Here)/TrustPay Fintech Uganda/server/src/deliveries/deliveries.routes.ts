import { Router } from 'express';
import { Role } from '../types/domain';
import { authenticate, requireRole } from '../middleware/auth';
import * as deliveriesController from './deliveries.controller';

export const deliveriesRouter = Router();

deliveriesRouter.post(
  '/:orderId/deliver',
  authenticate,
  requireRole(Role.RIDER),
  deliveriesController.confirm
);
