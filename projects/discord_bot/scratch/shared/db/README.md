SQLite backed storage for user accounts, wallets, shop, and games. Schema:
- users(id, username, password_hash, created_at)
- wallets(user_id, balance)
- items(id, name, price, stock)
- inventories(user_id, item_id, quantity)
- sessions(session_id, type, user_id, bet, state, data, created_at, updated_at)
