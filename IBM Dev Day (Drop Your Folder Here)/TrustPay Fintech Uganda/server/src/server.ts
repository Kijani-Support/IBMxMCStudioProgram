import { app } from './app';
import { seedDemoData } from './store/seed';
import { env } from './utils/env';
import { logger } from './utils/logger';

async function start(): Promise<void> {
  await seedDemoData();
  app.listen(env.port, () => {
    logger.info(`TrustPay API listening on port ${env.port}`);
    logger.info('Using in-memory mock data (no database).');
  });
}

void start();

process.on('SIGINT', () => process.exit(0));
process.on('SIGTERM', () => process.exit(0));
