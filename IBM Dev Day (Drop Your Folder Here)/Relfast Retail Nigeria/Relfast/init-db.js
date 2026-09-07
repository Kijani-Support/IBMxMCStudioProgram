const Database = require('better-sqlite3');
const path = require('path');
const db = new Database(path.join(__dirname, 'reflex.db'));

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT,
    role TEXT NOT NULL CHECK(role IN ('retailer', 'dispatcher', 'rider')),
    password TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS deliveries (
    id TEXT PRIMARY KEY,
    retailer_id TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    customer_phone TEXT,
    address TEXT NOT NULL,
    item_description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
      CHECK(status IN ('pending', 'assigned', 'picked_up', 'delivered', 'cancelled')),
    rider_id TEXT,
    assigned_at DATETIME,
    picked_up_at DATETIME,
    delivered_at DATETIME,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (retailer_id) REFERENCES users(id),
    FOREIGN KEY (rider_id) REFERENCES users(id)
  );

  CREATE INDEX IF NOT EXISTS idx_deliveries_status ON deliveries(status);
  CREATE INDEX IF NOT EXISTS idx_deliveries_rider ON deliveries(rider_id);
  CREATE INDEX IF NOT EXISTS idx_deliveries_retailer ON deliveries(retailer_id);
`);

console.log('Database initialized: reflex.db');
db.close();
