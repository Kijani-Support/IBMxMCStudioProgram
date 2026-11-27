import { store } from '../store/memory';

export function generateOrderNumber(): string {
  const last = [...store.orders].sort(
    (a, b) => a.createdAt.getTime() - b.createdAt.getTime()
  ).at(-1);

  if (!last) {
    return 'TP-1001';
  }

  const numeric = Number.parseInt(last.orderNumber.replace('TP-', ''), 10);
  if (Number.isNaN(numeric)) {
    return `TP-${Date.now().toString().slice(-8)}`;
  }

  return `TP-${numeric + 1}`;
}
