import { z } from 'zod';
import { AppError } from '../../utils/errors';
import type { PaymentProvider, VerifiedPayment } from './PaymentProvider';

const webhookPayloadSchema = z.object({
  transactionReference: z.string().trim().min(3).max(100),
  orderNumber: z.string().trim().min(3).max(50),
      amount: z.coerce.number().positive().finite(),
      status: z.enum(['PENDING', 'SUCCESSFUL', 'FAILED'])
});

export class MockPaymentProvider implements PaymentProvider {
  readonly name = 'MOCK';
  private readonly transactions = new Map<string, VerifiedPayment>();

  async verifyPayment(payload: unknown): Promise<VerifiedPayment> {
    const parsed = webhookPayloadSchema.safeParse(payload);
    if (!parsed.success) {
      const firstIssue = parsed.error.issues[0];
      throw new AppError(400, firstIssue?.message ?? 'Invalid webhook payload', 'INVALID_WEBHOOK_PAYLOAD');
    }

    const verified: VerifiedPayment = {
      transactionReference: parsed.data.transactionReference,
      orderNumber: parsed.data.orderNumber,
      amount: parsed.data.amount,
      status: parsed.data.status,
      provider: this.name
    };

    this.transactions.set(verified.transactionReference, verified);
    return verified;
  }

  async getTransactionStatus(transactionReference: string): Promise<VerifiedPayment | null> {
    return this.transactions.get(transactionReference) ?? null;
  }
}
