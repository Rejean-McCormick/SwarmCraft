const { initDb, get, run } = require('../db');

async function listItems() {
  const db = await initDb();
  return await new Promise((resolve, reject) => {
    db.all('SELECT * FROM items', [], (err, rows) => {
      if (err) return reject(err);
      resolve(rows);
    });
  });
}

async function buyItem(userId, itemId, quantity = 1) {
  const db = await initDb();
  const item = await get(db, 'SELECT * FROM items WHERE id = ?', [itemId]);
  if (!item) throw new Error('item not found');
  const total = item.price * quantity;
  // Deduct from wallet
  const { modifyBalance } = require('../wallet/walletService');
  await modifyBalance(userId, -total);
  // Update stock
  const current = item.stock;
  if (current < quantity) throw new Error('not enough stock');
  await run(db, 'UPDATE items SET stock = stock - ? WHERE id = ?', [quantity, itemId]);
  // Add to inventory (simplified: just increase quantity in inventories)
  const existing = await get(db, 'SELECT quantity FROM inventories WHERE user_id = ? AND item_id = ?', [userId, itemId]);
  if (existing) {
    await run(db, 'UPDATE inventories SET quantity = quantity + ? WHERE user_id = ? AND item_id = ?', [quantity, userId, itemId]);
  } else {
    await run(db, 'INSERT INTO inventories (user_id, item_id, quantity) VALUES (?, ?, ?)', [userId, itemId, quantity]);
  }
  return { itemId, quantity, total };
}

module.exports = { listItems, buyItem };
