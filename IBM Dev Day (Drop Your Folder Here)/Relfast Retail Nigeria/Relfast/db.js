const fs = require("fs");
const path = require("path");
const { v4: uuidv4 } = require("uuid");

const DB_PATH = path.join(__dirname, "reflex-data.json");

function load() {
  if (!fs.existsSync(DB_PATH)) {
    return { users: [], deliveries: [] };
  }
  return JSON.parse(fs.readFileSync(DB_PATH, "utf8"));
}

function save(data) {
  fs.writeFileSync(DB_PATH, JSON.stringify(data, null, 2));
}

function init() {
  if (fs.existsSync(DB_PATH)) return;
  save({ users: [], deliveries: [] });
  console.log("JSON store created:", DB_PATH);
}

function seed() {
  const data = load();

  // Always re-seed with correct Nigerian data for the demo
  const users = [
    { id: uuidv4(), name: "Chioma Electronics", phone: "+2348010000001", role: "retailer", password: "retailer123" },
    { id: uuidv4(), name: "Adaeze Pharmacy", phone: "+2348010000002", role: "retailer", password: "retailer123" },
    { id: uuidv4(), name: "Tunde Adebayo", phone: "+2348020000010", role: "dispatcher", password: "dispatch123" },
    { id: uuidv4(), name: "Emeka Obi", phone: "+2348030000020", role: "rider", password: "rider123" },
    { id: uuidv4(), name: "Fatima Bello", phone: "+2348030000021", role: "rider", password: "rider123" },
    { id: uuidv4(), name: "Ibrahim Yusuf", phone: "+2348030000022", role: "rider", password: "rider123" },
  ];

  const retailerId = users[0].id;

  data.users = users;
  data.deliveries = [
    {
      id: uuidv4(),
      retailer_id: retailerId,
      customer_name: "Adebayo Okonkwo",
      customer_phone: "+2348091112222",
      address: "Lekki Phase 1, Lagos – near Circle Mall",
      item_description: "Samsung Galaxy A15 + screen protector",
      status: "pending",
      rider_id: null,
      assigned_at: null,
      picked_up_at: null,
      delivered_at: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: uuidv4(),
      retailer_id: retailerId,
      customer_name: "Ngozi Eze",
      customer_phone: "+2348074445555",
      address: "Ikeja GRA, Lagos",
      item_description: "Laptop charger 65W USB-C",
      status: "pending",
      rider_id: null,
      assigned_at: null,
      picked_up_at: null,
      delivered_at: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ];

  save(data);
  console.log("Seeded. Demo logins:");
  console.log("  Retailer:   Chioma Electronics / retailer123");
  console.log("  Dispatcher: Tunde Adebayo / dispatch123");
  console.log("  Rider:      Emeka Obi / rider123");
}

module.exports = { load, save, init, seed };