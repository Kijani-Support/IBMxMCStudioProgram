import { store } from '../store/memory';
import { Role } from '../types/domain';
import { AppError } from '../utils/errors';

export async function getUserById(id: string) {
  return store.findUserById(id);
}

export async function getRiderById(id: string) {
  const user = store.findUserById(id);
  if (!user || user.role !== Role.RIDER) {
    throw new AppError(404, 'Rider not found', 'RIDER_NOT_FOUND');
  }
  return user;
}

export async function listRiders() {
  return store.users
    .filter((user) => user.role === Role.RIDER)
    .sort((a, b) => a.name.localeCompare(b.name))
    .map((user) => ({
      id: user.id,
      name: user.name,
      phone: user.phone,
      email: user.email
    }));
}
