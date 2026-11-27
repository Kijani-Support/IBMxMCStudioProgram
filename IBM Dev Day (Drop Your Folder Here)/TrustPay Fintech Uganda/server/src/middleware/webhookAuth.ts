import { NextFunction, Request, Response } from 'express';
import { env } from '../utils/env';
import { AppError } from '../utils/errors';

export function validateWebhookSecret(req: Request, _res: Response, next: NextFunction): void {
  const secret = req.header('x-webhook-secret');
  if (!secret || secret !== env.webhookSecret) {
    next(new AppError(401, 'Invalid webhook secret', 'INVALID_WEBHOOK'));
    return;
  }
  next();
}
