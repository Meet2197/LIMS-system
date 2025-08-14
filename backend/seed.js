const User = require('./models/User');
const bcrypt = require('bcrypt');

async function seedAdmin() {
  const exists = await User.findOne({ username: 'admin' });
  if (!exists) {
    const hashedPassword = await bcrypt.hash('admin123', 10);
    await User.create({ username: 'admin', password: hashedPassword, role: 'admin' });
    console.log('Admin user seeded');
  }
}

module.exports = seedAdmin;
