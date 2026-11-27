import { z } from 'zod';
import { phoneNumber } from '../auth/auth.schemas';

export const createOrderSchema = z.object({
  customerName: z.string().trim().min(2).max(100),
  customerPhone: phoneNumber,
  amount: z.number().positive().finite()
});

export const assignRiderSchema = z.object({
  riderId: z.string().uuid()
});

export type CreateOrderInput = z.infer<typeof createOrderSchema>;
export type AssignRiderInput = z.infer<typeof assignRiderSchema>;
