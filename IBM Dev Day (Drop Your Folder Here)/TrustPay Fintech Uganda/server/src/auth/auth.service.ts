import bcrypt from 'bcryptjs';
import { store } from '../store/memory';
import { AppError } from '../utils/errors';
import { signToken } from '../utils/jwt';
import { serializeUser } from '../utils/serialize';
import type { LoginInput, RegisterInput } from './auth.schemas';

const SALT_ROUNDS = 10;

export async function register(input: RegisterInput) {
  if (store.findUserByEmail(input.email) || store.findUserByPhone(input.phone)) {
    throw new AppError(409, 'An account with this email or phone already exists', 'ACCOUNT_EXISTS');
  }

  const now = store.now();
  const user = {
    id: store.id(),
    name: input.name,
    phone: input.phone,
    email: input.email,
    passwordHash: await bcrypt.hash(input.password, SALT_ROUNDS),
    role: input.role,
    createdAt: now,
    updatedAt: now
  };

  store.users.push(user);
  return { user: serializeUser(user), token: signToken(user.id, user.role) };
}

export async function login(input: LoginInput) {
  const user = store.findUserByEmail(input.email);
  if (!user) {
    throw new AppError(401, 'Invalid email or password', 'INVALID_CREDENTIALS');
  }

  const matches = await bcrypt.compare(input.password, user.passwordHash);
  if (!matches) {
    throw new AppError(401, 'Invalid email or password', 'INVALID_CREDENTIALS');
  }

  return { user: serializeUser(user), token: signToken(user.id, user.role) };
}

export async function getMe(userId: string) {
  const user = store.findUserById(userId);
  if (!user) {
    throw new AppError(401, 'User not found', 'UNAUTHENTICATED');
  }
  return serializeUser(user);
}
