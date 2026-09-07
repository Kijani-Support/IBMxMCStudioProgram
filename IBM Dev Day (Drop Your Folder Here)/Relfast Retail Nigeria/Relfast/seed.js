const { seed, init } = require('./db');

init();
seed();
console.log('Seed finished.');