import { NextFunction, Request, Response } from 'express';
import { ZodType } from 'zod';
import { AppError } from '../utils/errors';

export function validateBody(schema: ZodType) {
  return (req: Request, _res: Response, next: NextFunction): void => {
    const parsed = schema.safeParse(req.body);
    if (!parsed.success) {
      const firstIssue = parsed.error.issues[0];
      next(
        new AppError(400, firstIssue?.message ?? 'Invalid request body', 'VALIDATION_ERROR')
      );
      return;
    }

    req.body = parsed.data;
    next();
  };
}
