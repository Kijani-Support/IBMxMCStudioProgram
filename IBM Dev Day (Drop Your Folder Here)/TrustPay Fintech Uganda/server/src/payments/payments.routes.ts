import { Router } from 'express';
import { validateBody } from '../middleware/validate';
import { validateWebhookSecret } from '../middleware/webhookAuth';
import * as paymentsController from './payments.controller';
import { webhookSchema } from './payments.schemas';

export const paymentsRouter = Router();

paymentsRouter.post(
  '/webhook',
  validateWebhookSecret,
  validateBody(webhookSchema),
  paymentsController.webhook
);
