export function formatUgx(amount: number): string {
  return `UGX ${Math.round(amount).toLocaleString('en-US')}`;
}

export function amountsMatch(orderAmount: unknown, paymentAmount: unknown): boolean {
  return Number(orderAmount) === Number(paymentAmount);
}
