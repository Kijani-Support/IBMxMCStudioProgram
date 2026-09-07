const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const QRCode = require('qrcode');
const path = require('path');
const { load, save, init, seed } = require('./db');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

const JWT_SECRET = process.env.JWT_SECRET || 'reflex-sprint-secret-change-in-prod';
const PORT = process.env.PORT || 3000;

init();
seed();

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

function auth(requiredRoles = []) {
  return (req, res, next) => {
    const header = req.headers.authorization;
    if (!header || !header.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
    try {
      const payload = jwt.verify(header.slice(7), JWT_SECRET);
      if (requiredRoles.length && !requiredRoles.includes(payload.role)) {
        return res.status(403).json({ error: 'Forbidden for this role' });
      }
      req.user = payload;
      next();
    } catch (e) {
      return res.status(401).json({ error: 'Invalid token' });
    }
  };
}

app.post('/api/login', (req, res) => {
  const { name, password } = req.body;
  const data = load();
  const user = data.users.find(u => u.name === name && u.password === password);
  if (!user) return res.status(401).json({ error: 'Invalid credentials' });
  const token = jwt.sign(
    { id: user.id, name: user.name, role: user.role },
    JWT_SECRET,
    { expiresIn: '12h' }
  );
  res.json({
    token,
    user: { id: user.id, name: user.name, role: user.role, phone: user.phone }
  });
});

app.get('/api/me', auth(), (req, res) => {
  const data = load();
  const user = data.users.find(u => u.id === req.user.id);
  if (!user) return res.status(404).json({ error: 'User not found' });
  res.json({ id: user.id, name: user.name, phone: user.phone, role: user.role });
});

app.get('/api/riders', auth(['dispatcher']), (req, res) => {
  const data = load();
  res.json(
    data.users
      .filter(u => u.role === 'rider')
      .map(u => ({ id: u.id, name: u.name, phone: u.phone }))
  );
});

app.post('/api/deliveries', auth(['retailer']), (req, res) => {
  const { customer_name, customer_phone, address, item_description } = req.body;
  if (!customer_name || !address || !item_description) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  const data = load();
  const delivery = {
    id: uuidv4(),
    retailer_id: req.user.id,
    customer_name,
    customer_phone: customer_phone || null,
    address,
    item_description,
    status: 'pending',
    rider_id: null,
    assigned_at: null,
    picked_up_at: null,
    delivered_at: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };
  data.deliveries.unshift(delivery);
  save(data);
  io.emit('delivery:new', delivery);
  res.status(201).json(delivery);
});

app.get('/api/deliveries', auth(), (req, res) => {
  const data = load();
  let rows = data.deliveries;
  if (req.user.role === 'retailer') {
    rows = rows.filter(d => d.retailer_id === req.user.id);
  } else if (req.user.role === 'rider') {
    rows = rows.filter(d => d.rider_id === req.user.id);
  }
  const nameMap = Object.fromEntries(data.users.map(u => [u.id, u.name]));
  rows = rows.map(r => ({
    ...r,
    retailer_name: nameMap[r.retailer_id] || null,
    rider_name: r.rider_id ? nameMap[r.rider_id] : null
  }));
  res.json(rows);
});

app.post('/api/deliveries/:id/assign', auth(['dispatcher']), (req, res) => {
  const { rider_id } = req.body;
  const data = load();
  const delivery = data.deliveries.find(d => d.id === req.params.id);
  if (!delivery) return res.status(404).json({ error: 'Delivery not found' });
  if (delivery.status !== 'pending') {
    return res.status(400).json({ error: 'Only pending can be assigned' });
  }
  const rider = data.users.find(u => u.id === rider_id && u.role === 'rider');
  if (!rider) return res.status(400).json({ error: 'Invalid rider' });

  delivery.status = 'assigned';
  delivery.rider_id = rider_id;
  delivery.assigned_at = new Date().toISOString();
  delivery.updated_at = new Date().toISOString();
  save(data);
  io.emit('delivery:updated', delivery);
  res.json(delivery);
});

app.post('/api/deliveries/:id/status', auth(['rider']), (req, res) => {
  const { status } = req.body;
  const allowed = { assigned: 'picked_up', picked_up: 'delivered' };
  const data = load();
  const delivery = data.deliveries.find(d => d.id === req.params.id);
  if (!delivery) return res.status(404).json({ error: 'Not found' });
  if (delivery.rider_id !== req.user.id) {
    return res.status(403).json({ error: 'Not your delivery' });
  }
  if (!allowed[delivery.status] || allowed[delivery.status] !== status) {
    return res.status(400).json({ error: `Cannot go from ${delivery.status} to ${status}` });
  }
  delivery.status = status;
  if (status === 'picked_up') delivery.picked_up_at = new Date().toISOString();
  if (status === 'delivered') delivery.delivered_at = new Date().toISOString();
  delivery.updated_at = new Date().toISOString();
  save(data);
  io.emit('delivery:updated', delivery);
  res.json(delivery);
});

app.get('/api/deliveries/:id/qr', auth(), async (req, res) => {
  const data = load();
  const delivery = data.deliveries.find(d => d.id === req.params.id);
  if (!delivery) return res.status(404).json({ error: 'Not found' });
  try {
    const dataUrl = await QRCode.toDataURL(
      JSON.stringify({ deliveryId: delivery.id, type: 'reflex-pod' })
    );
    res.json({ qr: dataUrl, deliveryId: delivery.id });
  } catch (e) {
    res.status(500).json({ error: 'QR generation failed' });
  }
});

app.post('/api/deliveries/confirm-scan', auth(['rider']), (req, res) => {
  const { deliveryId } = req.body;
  const data = load();
  const delivery = data.deliveries.find(d => d.id === deliveryId);
  if (!delivery) return res.status(404).json({ error: 'Delivery not found' });
  if (delivery.rider_id !== req.user.id) {
    return res.status(403).json({ error: 'Not assigned to you' });
  }
  let nextStatus = null;
  if (delivery.status === 'assigned') nextStatus = 'picked_up';
  else if (delivery.status === 'picked_up') nextStatus = 'delivered';
  else return res.status(400).json({ error: 'Nothing to confirm for current status' });

  delivery.status = nextStatus;
  if (nextStatus === 'picked_up') delivery.picked_up_at = new Date().toISOString();
  if (nextStatus === 'delivered') delivery.delivered_at = new Date().toISOString();
  delivery.updated_at = new Date().toISOString();
  save(data);
  io.emit('delivery:updated', delivery);
  res.json(delivery);
});

io.on('connection', (socket) => {
  console.log('Client connected', socket.id);
  socket.on('disconnect', () => console.log('Client disconnected', socket.id));
});

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

server.listen(PORT, () => {
  console.log(`Reflex running at http://localhost:${PORT}`);
});