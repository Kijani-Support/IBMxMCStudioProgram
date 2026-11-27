import { Request, Response, NextFunction } from 'express';
import * as paymentsService from './payments.service';

export async function webhook(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const result = await paymentsService.processWebhook(req.body);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}
