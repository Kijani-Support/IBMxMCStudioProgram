import { Request, Response, NextFunction } from 'express';
import { requireUser } from '../middleware/auth';
import * as deliveriesService from './deliveries.service';

export async function confirm(req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const user = requireUser(req);
    const result = await deliveriesService.confirmDelivery(req.params.orderId as string, user.id);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}
