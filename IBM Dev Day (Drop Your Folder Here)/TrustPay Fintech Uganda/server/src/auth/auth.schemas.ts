import { z } from 'zod';

export const phoneNumber = z
  .string()
  .trim()
  .regex(/^\+[1-9]\d{6,14}$/, 'Enter a phone number with country code, e.g. +256700000001');

export const registerSchema = z.object({
  name: z.string().trim().min(2).max(100),
  phone: phoneNumber,
  email: z.string().trim().email().toLowerCase(),
  password: z.string().min(8).max(128),
  role: z.enum(['BUSINESS', 'RIDER'])
});

export const loginSchema = z.object({
  email: z.string().trim().email().toLowerCase(),
  password: z.string().min(1)
});

export type RegisterInput = z.infer<typeof registerSchema>;
export type LoginInput = z.infer<typeof loginSchema>;
