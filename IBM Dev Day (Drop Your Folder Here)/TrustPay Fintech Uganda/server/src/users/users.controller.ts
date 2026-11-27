import { Request, Response, NextFunction } from 'express';
import * as usersService from './users.service';

export async function listRiders(_req: Request, res: Response, next: NextFunction): Promise<void> {
  try {
    const riders = await usersService.listRiders();
    res.status(200).json({ riders });
  } catch (error) {
    next(error);
  }
}
