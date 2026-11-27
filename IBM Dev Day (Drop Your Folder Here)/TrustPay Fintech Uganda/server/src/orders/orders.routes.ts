import { Router } from 'express';
import { Role } from '../types/domain';
import { authenticate, requireRole } from '../middleware/auth';
import { validateBody } from '../middleware/validate';
import * as ordersController from './orders.controller';
import { assignRiderSchema, createOrderSchema } from './orders.schemas';

export const ordersRouter = Router();

ordersRouter.use(authenticate);

ordersRouter.post('/', requireRole(Role.BUSINESS), validateBody(createOrderSchema), ordersController.create);
ordersRouter.get('/', ordersController.list);
ordersRouter.get('/:orderId', ordersController.getById);
ordersRouter.post(
  '/:orderId/assign-rider',
  requireRole(Role.BUSINESS),
  validateBody(assignRiderSchema),
  ordersController.assignRider
);
