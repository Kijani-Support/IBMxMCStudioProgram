import type { AuthResponse, Notification, Order, RiderSummary, User } from './types';
import { clearSessionToken, getSessionToken, setSessionToken } from './session';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:3000';
const WEBHOOK_SECRET = import.meta.env.VITE_WEBHOOK_SECRET ?? '';

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

function friendlyMessage(status: number, message?: string, code?: string): string {
  switch (code) {
    case 'INVALID_CREDENTIALS':
      return 'Invalid email or password.';
    case 'ACCOUNT_EXISTS':
      return 'An account with this email or phone already exists.';
    case 'UNAUTHENTICATED':
      return 'Please log in to continue.';
    case 'FORBIDDEN':
      return 'You do not have permission to do that.';
    case 'ORDER_NOT_FOUND':
      return 'That order could not be found.';
    case 'RIDER_NOT_FOUND':
      return 'That rider could not be found.';
    case 'PAYMENT_NOT_CONFIRMED':
      return 'Payment has not been confirmed. Delivery cannot be completed.';
    case 'ALREADY_DELIVERED':
      return 'Delivery has already been confirmed.';
    case 'AMOUNT_MISMATCH':
      return 'The payment amount does not match this order.';
    case 'INVALID_WEBHOOK':
      return 'Demo payment could not be verified.';
    default:
      break;
  }

  if (message && message.length < 140 && !message.toLowerCase().includes('prisma')) {
    return message;
  }

  if (status === 401) return 'Please log in to continue.';
  if (status === 403) return 'You do not have permission to do that.';
  if (status === 404) return 'We could not find what you were looking for.';
  return 'Something went wrong. Please try again.';
}

function getToken(): string | null {
  return getSessionToken();
}

export function storeToken(token: string): void {
  setSessionToken(token);
}

export function clearToken(): void {
  clearSessionToken();
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (!headers.has('Content-Type') && options.body) {
    headers.set('Content-Type', 'application/json');
  }

  const token = getToken();
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers });
  } catch {
    throw new ApiError(0, 'Cannot reach TrustPay. Check that the API is running.');
  }

  const data = (await response.json().catch(() => ({}))) as {
    message?: string;
    code?: string;
  };

  if (!response.ok) {
    throw new ApiError(
      response.status,
      friendlyMessage(response.status, data.message, data.code),
      data.code
    );
  }

  return data as T;
}

export const api = {
  login(body: { email: string; password: string }) {
    return request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(body)
    });
  },

  register(body: {
    name: string;
    phone: string;
    email: string;
    password: string;
    role: 'BUSINESS' | 'RIDER';
  }) {
    return request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(body)
    });
  },

  getMe() {
    return request<{ user: User }>('/auth/me');
  },

  getOrders() {
    return request<{ orders: Order[] }>('/orders');
  },

  getOrder(orderId: string) {
    return request<{ order: Order }>(`/orders/${orderId}`);
  },

  createOrder(body: { customerName: string; customerPhone: string; amount: number }) {
    return request<{ order: Order }>('/orders', {
      method: 'POST',
      body: JSON.stringify(body)
    });
  },

  assignRider(orderId: string, riderId: string) {
    return request<{ order: Order }>(`/orders/${orderId}/assign-rider`, {
      method: 'POST',
      body: JSON.stringify({ riderId })
    });
  },

  getRiders() {
    return request<{ riders: RiderSummary[] }>('/riders');
  },

  getNotifications() {
    return request<{ notifications: Notification[] }>('/notifications');
  },

  markNotificationRead(id: string) {
    return request<{ notification: Notification }>(`/notifications/${id}/read`, {
      method: 'PATCH'
    });
  },

  confirmDelivery(orderId: string) {
    return request<{ message: string; order: Order }>(`/orders/${orderId}/deliver`, {
      method: 'POST'
    });
  },

  simulatePayment(order: Pick<Order, 'orderNumber' | 'amount'>) {
    return request<{
      received: boolean;
      duplicate?: boolean;
      matched?: boolean;
      paymentStatus?: string;
      notificationCreated?: boolean;
      message?: string;
    }>('/payments/webhook', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Webhook-Secret': WEBHOOK_SECRET
      },
      body: JSON.stringify({
        transactionReference: `DEMO-${order.orderNumber}-${Date.now()}`,
        orderNumber: order.orderNumber,
        amount: order.amount,
        status: 'SUCCESSFUL'
      })
    });
  }
};
