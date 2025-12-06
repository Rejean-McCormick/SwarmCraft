Project: Discord bot backend with modular services (auth, wallet, shop, games).

API surface:
- POST /auth/register
- POST /auth/login
- GET /wallet/balance
- POST /wallet/deposit
- GET /shop/items
- POST /shop/buy
- POST /games/blackjack/start
- POST /games/blackjack/join
- GET /games/blackjack/state/:sessionId

Security notes:
- Use JWT for auth (stateless)
- Validate inputs, rate limit in production (omitted in this draft)
