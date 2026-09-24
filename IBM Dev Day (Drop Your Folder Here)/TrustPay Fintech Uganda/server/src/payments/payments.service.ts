import { store } from '../store/memory';
import { PaymentRecordStatus, PaymentStatus } from '../types/domain';
import { notificationService } from '../notifications/notifications.service';
import { AppError } from '../utils/errors';
import { amountsMatch } from '../utils/money';
import { serializePayment } from '../utils/serialize';
import { paymentProvider } from './providers';

export async function processWebhook(payload: unknown) {
  const verified = await paymentProvider.verifyPayment(payload);

  const existing = store.findPaymentByReference(verified.transactionReference);
  if (existing) {
    const existingOrder = store.findOrderById(existing.orderId);
    return {
      received: true,
      duplicate: true,
      matched: existing.status === PaymentRecordStatus.SUCCESSFUL,
      orderNumber: existingOrder?.orderNumber ?? verified.orderNumber,
      paymentStatus: existingOrder?.paymentStatus,
      notificationCreated: false,
      payment: serializePayment(existing)
    };
  }

  const order = store.findOrderByNumber(verified.orderNumber);
  if (!order) {
    throw new AppError(404, 'Order not found for payment', 'ORDER_NOT_FOUND');
  }

  if (order.paymentStatus === PaymentStatus.PAID) {
    return {
      received: true,
      duplicate: true,
      matched: true,
      orderNumber: order.orderNumber,
      paymentStatus: order.paymentStatus,
      notificationCreated: false,
      message: 'Order already marked as paid.'
    };
  }

  const now = store.now();
  const isSuccessful =
    verified.status === 'SUCCESSFUL' && amountsMatch(order.amount, verified.amount);

  if (!isSuccessful) {
    const payment = {
      id: store.id(),
      orderId: order.id,
      transactionReference: verified.transactionReference,
      amount: verified.amount,
      status: PaymentRecordStatus.FAILED,
      provider: verified.provider,
      paidAt: null,
      createdAt: now,
      updatedAt: now
    };
    store.payments.push(payment);
    order.paymentStatus = PaymentStatus.FAILED;
    order.updatedAt = now;

    const reason = verified.status === 'SUCCESSFUL' ? 'AMOUNT_MISMATCH' : 'PAYMENT_FAILED';
    return {
      received: true,
      duplicate: false,
      matched: false,
      reason,
      orderNumber: order.orderNumber,
      paymentStatus: PaymentStatus.FAILED,
      notificationCreated: false,
      message:
        reason === 'AMOUNT_MISMATCH'
          ? 'Payment amount does not match the order amount.'
          : 'Payment was not successful.',
      payment: serializePayment(payment)
    };
  }

  const payment = {
    id: store.id(),
    orderId: order.id,
    transactionReference: verified.transactionReference,
    amount: verified.amount,
    status: PaymentRecordStatus.SUCCESSFUL,
    provider: verified.provider,
    paidAt: now,
    createdAt: now,
    updatedAt: now
  };
  store.payments.push(payment);
  order.paymentStatus = PaymentStatus.PAID;
  order.updatedAt = now;

  let notificationCreated = false;
  if (order.riderId) {
    await notificationService.notifyPaymentConfirmed(order);
    notificationCreated = true;
  }

  return {
    received: true,
    duplicate: false,
    matched: true,
    orderNumber: order.orderNumber,
    paymentStatus: order.paymentStatus,
    notificationCreated,
    payment: serializePayment(payment)
  };
}
