import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(process.cwd(), '.env') });

process.env.NODE_ENV = 'test';
process.env.JWT_SECRET ??= 'test-jwt-secret-change-me';
process.env.WEBHOOK_SECRET ??= 'test-webhook-secret';
