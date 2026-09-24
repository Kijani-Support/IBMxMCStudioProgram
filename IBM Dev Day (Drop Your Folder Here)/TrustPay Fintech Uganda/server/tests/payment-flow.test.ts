import request from 'supertest';
import { beforeAll, describe, expect, it } from 'vitest';
import { app } from '../src/app';
import { store } from '../src/store/memory';
import { env } from '../src/utils/env';

const webhookSecret = env.webhookSecret;

interface AuthResponse {
  token: string;
  user: { id: string; role: string; name: string };
}

describe('TrustPay payment-to-rider notification flow', () => {
  let businessToken: string;
  let riderToken: string;
  let riderId: string;
  let orderId: string;
  let orderNumber: string;
  let notificationId: string;

  beforeAll(async () => {
    store.reset();

    const business = await request(app)
      .post('/auth/register')
      .send({
        name: 'Kampala Parcels',
        phone: '+256700000001',
        email: 'business@trustpay.test',
        password: 'password123',
        role: 'BUSINESS'
      });

    expect(business.status).toBe(201);
    businessToken = (business.body as AuthResponse).token;

    const rider = await request(app)
      .post('/auth/register')
      .send({
        name: 'John Rider',
        phone: '+256700000002',
        email: 'john@trustpay.test',
        password: 'password123',
        role: 'RIDER'
      });

    expect(rider.status).toBe(201);
    riderToken = (rider.body as AuthResponse).token;
    riderId = (rider.body as AuthResponse).user.id;
  });

  it('1. business creates an order', async () => {
    const response = await request(app)
      .post('/orders')
      .set('Authorization', `Bearer ${businessToken}`)
      .send({
        customerName: 'Sarah',
        customerPhone: '+256700000003',
        amount: 50000
      });

    expect(response.status).toBe(201);
    expect(response.body.order.customerName).toBe('Sarah');
    expect(response.body.order.amount).toBe(50000);
    expect(response.body.order.paymentStatus).toBe('PENDING');
    expect(response.body.order.safeToDeliver).toBe(false);

    orderId = response.body.order.id;
    orderNumber = response.body.order.orderNumber;
  });

  it('2. business assigns a rider', async () => {
    const response = await request(app)
      .post(`/orders/${orderId}/assign-rider`)
      .set('Authorization', `Bearer ${businessToken}`)
      .send({ riderId });

    expect(response.status).toBe(200);
    expect(response.body.order.riderId).toBe(riderId);
    expect(response.body.order.status).toBe('ASSIGNED');

    const deliveries = await request(app)
      .get('/orders')
      .set('Authorization', `Bearer ${riderToken}`);

    expect(deliveries.status).toBe(200);
    expect(deliveries.body.orders).toHaveLength(1);
    expect(deliveries.body.orders[0].id).toBe(orderId);
  });

  it('8. rider cannot complete delivery before payment is confirmed', async () => {
    const response = await request(app)
      .post(`/orders/${orderId}/deliver`)
      .set('Authorization', `Bearer ${riderToken}`);

    expect(response.status).toBe(409);
    expect(response.body.message).toBe(
      'Payment has not been confirmed. Delivery cannot be completed.'
    );
  });

  it('3. payment webhook is received', async () => {
    const response = await request(app)
      .post('/payments/webhook')
      .set('X-Webhook-Secret', webhookSecret)
      .send({
        transactionReference: 'TXN123456',
        orderNumber,
        amount: 50000,
        status: 'SUCCESSFUL'
      });

    expect(response.status).toBe(200);
    expect(response.body.received).toBe(true);
    expect(response.body.duplicate).toBe(false);
  });

  it('4. payment is successfully matched to the order', async () => {
    const payment = store.findPaymentByReference('TXN123456');

    expect(payment).toBeDefined();
    expect(payment?.orderId).toBe(orderId);
    expect(payment?.status).toBe('SUCCESSFUL');
    expect(payment?.amount).toBe(50000);
  });

  it('5. order becomes PAID', async () => {
    const response = await request(app)
      .get(`/orders/${orderId}`)
      .set('Authorization', `Bearer ${riderToken}`);

    expect(response.status).toBe(200);
    expect(response.body.order.paymentStatus).toBe('PAID');
    expect(response.body.order.safeToDeliver).toBe(true);
  });

  it('6. rider receives a payment confirmation notification', async () => {
    const notifications = store.notifications.filter(
      (notification) => notification.riderId === riderId && notification.orderId === orderId
    );

    expect(notifications).toHaveLength(1);
    expect(notifications[0]?.type).toBe('PAYMENT_CONFIRMED');
    expect(notifications[0]?.title).toBe('Payment Confirmed');
    expect(notifications[0]?.message).toContain(orderNumber);
    expect(notifications[0]?.message).toContain('UGX 50,000');
    notificationId = notifications[0]!.id;
  });

  it('7. rider can see the notification', async () => {
    const response = await request(app)
      .get('/notifications')
      .set('Authorization', `Bearer ${riderToken}`);

    expect(response.status).toBe(200);
    expect(response.body.notifications).toHaveLength(1);
    expect(response.body.notifications[0].id).toBe(notificationId);
    expect(response.body.notifications[0].read).toBe(false);

    const markRead = await request(app)
      .patch(`/notifications/${notificationId}/read`)
      .set('Authorization', `Bearer ${riderToken}`);

    expect(markRead.status).toBe(200);
    expect(markRead.body.notification.read).toBe(true);
  });

  it('9. rider can complete delivery after payment is confirmed', async () => {
    const response = await request(app)
      .post(`/orders/${orderId}/deliver`)
      .set('Authorization', `Bearer ${riderToken}`);

    expect(response.status).toBe(200);
    expect(response.body.message).toBe('Delivery confirmed successfully.');
    expect(response.body.order.status).toBe('DELIVERED');
  });

  it('10. duplicate payment webhook does not create duplicate notifications', async () => {
    const response = await request(app)
      .post('/payments/webhook')
      .set('X-Webhook-Secret', webhookSecret)
      .send({
        transactionReference: 'TXN123456',
        orderNumber,
        amount: 50000,
        status: 'SUCCESSFUL'
      });

    expect(response.status).toBe(200);
    expect(response.body.duplicate).toBe(true);

    const notifications = store.notifications.filter(
      (notification) =>
        notification.riderId === riderId &&
        notification.orderId === orderId &&
        notification.type === 'PAYMENT_CONFIRMED'
    );
    const payments = store.payments.filter(
      (payment) => payment.transactionReference === 'TXN123456'
    );

    expect(notifications).toHaveLength(1);
    expect(payments).toHaveLength(1);
  });

  it('rejects a webhook with an invalid secret', async () => {
    const response = await request(app)
      .post('/payments/webhook')
      .set('X-Webhook-Secret', 'wrong-secret')
      .send({
        transactionReference: 'TXN-INVALID',
        orderNumber,
        amount: 50000,
        status: 'SUCCESSFUL'
      });

    expect(response.status).toBe(401);
  });

  it('does not notify the rider when the payment amount does not match', async () => {
    const order = await request(app)
      .post('/orders')
      .set('Authorization', `Bearer ${businessToken}`)
      .send({
        customerName: 'Mismatch Customer',
        customerPhone: '+256700000004',
        amount: 20000
      });

    await request(app)
      .post(`/orders/${order.body.order.id}/assign-rider`)
      .set('Authorization', `Bearer ${businessToken}`)
      .send({ riderId });

    const webhook = await request(app)
      .post('/payments/webhook')
      .set('X-Webhook-Secret', webhookSecret)
      .send({
        transactionReference: 'TXN-MISMATCH',
        orderNumber: order.body.order.orderNumber,
        amount: 15000,
        status: 'SUCCESSFUL'
      });

    expect(webhook.status).toBe(200);
    expect(webhook.body.matched).toBe(false);
    expect(webhook.body.reason).toBe('AMOUNT_MISMATCH');
    expect(webhook.body.notificationCreated).toBe(false);

    const notifications = store.notifications.filter(
      (notification) => notification.orderId === order.body.order.id
    );
    expect(notifications).toHaveLength(0);
  });
});
