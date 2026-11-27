import { z } from 'zod';

export const webhookSchema = z.object({
  transactionReference: z.string().trim().min(3).max(100),
  orderNumber: z.string().trim().min(3).max(50),
  amount: z.coerce.number().positive().finite(),
  status: z.enum(['PENDING', 'SUCCESSFUL', 'FAILED'])
});

export type WebhookInput = z.infer<typeof webhookSchema>;
