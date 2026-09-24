import { NextFunction, Request, Response } from 'express';
import { Role } from '../types/domain';
import { AppError } from '../utils/errors';
import { verifyToken } from '../utils/jwt';

export function authenticate(req: Request, _res: Response, next: NextFunction): void {
  const header = req.header('authorization');
  if (!header?.startsWith('Bearer ')) {
    next(new AppError(401, 'Authentication required', 'UNAUTHENTICATED'));
    return;
  }

  try {
    const payload = verifyToken(header.slice('Bearer '.length));
    req.user = { id: payload.sub, role: payload.role };
    next();
  } catch (error) {
    next(error);
  }
}

export function requireRole(...roles: Role[]) {
  return (req: Request, _res: Response, next: NextFunction): void => {
    if (!req.user) {
      next(new AppError(401, 'Authentication required', 'UNAUTHENTICATED'));
      return;
    }

    if (!roles.includes(req.user.role)) {
      next(new AppError(403, 'You do not have permission to perform this action', 'FORBIDDEN'));
      return;
    }

    next();
  };
}

export function requireUser(req: Request): { id: string; role: Role } {
  if (!req.user) {
    throw new AppError(401, 'Authentication required', 'UNAUTHENTICATED');
  }
  return req.user;
}
