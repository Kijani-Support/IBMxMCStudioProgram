import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { env } from './utils/env';
import { authRouter } from './auth/auth.routes';
import { ordersRouter } from './orders/orders.routes';
import { paymentsRouter } from './payments/payments.routes';
import { notificationsRouter } from './notifications/notifications.routes';
import { deliveriesRouter } from './deliveries/deliveries.routes';
import { ridersRouter } from './users/users.routes';
import { errorHandler, notFoundHandler } from './middleware/errorHandler';

export const app = express();

app.use(helmet());
app.use(
  cors({
    origin: env.corsOrigin === '*' ? true : env.corsOrigin.split(',').map((origin) => origin.trim()),
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Webhook-Secret'],
    methods: ['GET', 'POST', 'PATCH', 'OPTIONS']
  })
);
app.use(express.json());

app.get('/health', (_req, res) => {
  res.status(200).json({ status: 'ok', service: 'trustpay' });
});

app.use('/auth', authRouter);
app.use('/orders', ordersRouter);
app.use('/orders', deliveriesRouter);
app.use('/payments', paymentsRouter);
app.use('/notifications', notificationsRouter);
app.use('/riders', ridersRouter);

app.use(notFoundHandler);
app.use(errorHandler);
