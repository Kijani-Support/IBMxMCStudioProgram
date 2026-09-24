export const TOKEN_KEY = 'trustpay_token';
export const USER_KEY = 'trustpay_user';

function memory(): Storage {
  return sessionStorage;
}

/** Old builds used localStorage, which forced every tab to share one account. */
function dropSharedLocalSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

dropSharedLocalSession();

export function getSessionToken(): string | null {
  return memory().getItem(TOKEN_KEY);
}

export function setSessionToken(token: string): void {
  memory().setItem(TOKEN_KEY, token);
}

export function clearSessionToken(): void {
  memory().removeItem(TOKEN_KEY);
}

export function getSessionUser(): string | null {
  return memory().getItem(USER_KEY);
}

export function setSessionUser(serialized: string): void {
  memory().setItem(USER_KEY, serialized);
}

export function clearSessionUser(): void {
  memory().removeItem(USER_KEY);
}

export function clearSession(): void {
  clearSessionToken();
  clearSessionUser();
}
