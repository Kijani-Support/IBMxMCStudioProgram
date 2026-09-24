export type PaymentVerificationStatus = 'PENDING' | 'SUCCESSFUL' | 'FAILED';

export interface VerifiedPayment {
  transactionReference: string;
  orderNumber: string;
  amount: number;
  status: PaymentVerificationStatus;
  provider: string;
}

export interface PaymentProvider {
  verifyPayment(payload: unknown): Promise<VerifiedPayment>;
  getTransactionStatus(transactionReference: string): Promise<VerifiedPayment | null>;
}
