export function formatUgx(amount: number): string {
  return `UGX ${Math.round(amount).toLocaleString('en-US')}`;
}

export function formatPhone(phone: string): string {
  const cleaned = phone.replace(/\s/g, '');
  if (!cleaned.startsWith('+')) {
    return phone;
  }

  const digits = cleaned.slice(1);
  if (!/^\d+$/.test(digits) || digits.length < 8) {
    return phone;
  }

  return `+${digits.replace(/(\d{3})(?=\d)/g, '$1 ').trim()}`;
}

export function formatOrderStatus(status: string): string {
  switch (status) {
    case 'PENDING':
      return 'Pending';
    case 'ASSIGNED':
      return 'Assigned';
    case 'OUT_FOR_DELIVERY':
      return 'Out for delivery';
    case 'DELIVERED':
      return 'Delivered';
    case 'CANCELLED':
      return 'Cancelled';
    default:
      return status;
  }
}

export function toInternationalPhone(input: string): string {
  const digits = input.replace(/\D/g, '');
  return digits ? `+${digits}` : input.trim();
}
