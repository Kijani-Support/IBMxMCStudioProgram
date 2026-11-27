export interface NotificationPayload {
  riderId: string;
  orderId: string;
  type: 'PAYMENT_CONFIRMED';
  title: string;
  message: string;
}

export interface NotificationChannel {
  readonly name: string;
  send(payload: NotificationPayload): Promise<void>;
}
