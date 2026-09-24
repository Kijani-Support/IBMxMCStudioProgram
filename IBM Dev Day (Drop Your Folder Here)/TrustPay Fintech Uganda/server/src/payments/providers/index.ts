import { MockPaymentProvider } from './MockPaymentProvider';
import type { PaymentProvider } from './PaymentProvider';

export const paymentProvider: PaymentProvider = new MockPaymentProvider();
