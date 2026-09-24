import jwt, { type SignOptions } from 'jsonwebtoken';
import type { Role } from '../types/domain';
import { env } from './env';
import { AppError } from './errors';

export interface JwtPayload {
  sub: string;
  role: Role;
}

export function signToken(userId: string, role: Role): string {
  const options: SignOptions = {
    expiresIn: env.jwtExpiresIn as SignOptions['expiresIn']
  };
  return jwt.sign({ sub: userId, role }, env.jwtSecret, options);
}

export function verifyToken(token: string): JwtPayload {
  try {
    const decoded = jwt.verify(token, env.jwtSecret) as JwtPayload;
    if (!decoded.sub || !decoded.role) {
      throw new AppError(401, 'Invalid token', 'INVALID_TOKEN');
    }
    return decoded;
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }
    throw new AppError(401, 'Invalid or expired token', 'INVALID_TOKEN');
  }
}
