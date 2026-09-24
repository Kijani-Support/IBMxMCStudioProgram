export type Role = 'BUSINESS' | 'RIDER';
export type OrderStatus = 'PENDING' | 'ASSIGNED' | 'OUT_FOR_DELIVERY' | 'DELIVERED' | 'CANCELLED';
export type PaymentStatusValue = 'PENDING' | 'PAID' | 'FAILED';

export interface User {
  id: string;
  name: string;
  phone: string;
  email: string;
  role: Role;
  createdAt: string;
  updatedAt: string;
}

export interface RiderSummary {
  id: string;
  name: string;
  phone: string;
  email?: string;
}

export interface Order {
  id: string;
  orderNumber: string;
  businessId: string;
  riderId: string | null;
  rider: RiderSummary | null;
  customerName: string;
  customerPhone: string;
  amount: number;
  currency: 'UGX';
  status: OrderStatus;
  paymentStatus: PaymentStatusValue;
  safeToDeliver: boolean;
  riderNotified: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Notification {
  id: string;
  riderId: string;
  orderId: string;
  type: 'PAYMENT_CONFIRMED';
  title: string;
  message: string;
  read: boolean;
  createdAt: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}
