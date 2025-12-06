Environment variable mapping for the Discord Casino Bot Backend.

**Secrets** must be provided via a secret store or CI/CD vault.

Variables:
- DISCORD_BOT_TOKEN: Bot token from Discord Developer Portal
- REQUESTY_API_KEY: API key for Requesty
- DATABASE_URL: SQLite DB path (sqlite:///data/bot.db)
- DISCORD_APP_ID: Discord application client ID
- DISCORD_GUILD_ID: Discord guild/server ID
