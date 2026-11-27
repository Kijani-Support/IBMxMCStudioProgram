import { isTest } from './env';

export const logger = {
  info: (...args: unknown[]): void => {
    if (!isTest) {
      console.log(...args);
    }
  },
  error: (...args: unknown[]): void => {
    console.error(...args);
  }
};
