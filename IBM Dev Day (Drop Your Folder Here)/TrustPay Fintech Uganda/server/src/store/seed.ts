import bcrypt from 'bcryptjs';
import { Role } from '../types/domain';
import { isTest } from '../utils/env';
import { store } from './memory';

export const DEMO_PASSWORD = 'password123';

export async function seedDemoData(): Promise<void> {
  if (isTest || store.users.length > 0) {
    return;
  }

  const now = store.now();
  const passwordHash = await bcrypt.hash(DEMO_PASSWORD, 10);

  store.users.push(
    {
      id: store.id(),
      name: 'Kampala Parcels',
      phone: '+256700000001',
      email: 'business@trustpay.test',
      passwordHash,
      role: Role.BUSINESS,
      createdAt: now,
      updatedAt: now
    },
    {
      id: store.id(),
      name: 'John Rider',
      phone: '+256700000002',
      email: 'john@trustpay.test',
      passwordHash,
      role: Role.RIDER,
      createdAt: now,
      updatedAt: now
    }
  );
}
