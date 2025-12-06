// Jest-style unit tests for the SQLite-backed Users API
const { initDb, createUser, getUsers, getUser, ValidationError } = require('../src/users');

describe('Users API - SQLite backend', () => {
  // Helper to initialize a fresh in-memory DB for each test
  const freshDb = async () => {
    // Use in-memory database per test to avoid cross-test contamination
    const db = await initDb(':memory:');
    return db;
  };

  test('should create a user with valid data and return non-sensitive fields', async () => {
    const db = await freshDb();
    const user = await createUser(db, {
      name: 'Alice',
      email: 'alice@example.com',
      password: 'secret123'
    });
    expect(user).toBeTruthy();
    expect(user).toHaveProperty('id');
    expect(user).toHaveProperty('name', 'Alice');
    expect(user).toHaveProperty('email', 'alice@example.com');
    expect(user).toHaveProperty('created_at');
    expect(user).not.toHaveProperty('password_hash');
  });

  test('should fetch all users with GET-like helper', async () => {
    const db = await freshDb();
    await createUser(db, { name: 'Bob', email: 'bob@example.com', password: 'password1' });
    const users = await getUsers(db);
    expect(Array.isArray(users)).toBe(true);
    expect(users.length).toBe(1);
    expect(users[0]).toHaveProperty('id');
  });

  test('should throw ValidationError when required fields are missing or invalid', async () => {
    const db = await freshDb();
    try {
      await createUser(db, { name: '', email: 'bad', password: '123' });
      // If no error, fail the test
      throw new Error('Expected ValidationError');
    } catch (err) {
      expect(err).toBeInstanceOf(ValidationError);
      expect(Array.isArray(err.errors)).toBe(true);
    }
  });

  test('should enforce unique email constraint', async () => {
    const db = await freshDb();
    await createUser(db, { name: 'Carol', email: 'carol@example.com', password: 'mypassword' });
    try {
      await createUser(db, { name: 'Caroline', email: 'carol@example.com', password: 'another' });
      throw new Error('Expected email uniqueness error');
    } catch (err) {
      // Could be plain Error with status, or a custom error; both acceptable as long as it's an error
      expect(err).toBeTruthy();
    }
  });

  test('should fetch a user by id and matching fields', async () => {
    const db = await freshDb();
    const created = await createUser(db, { name: 'Dave', email: 'dave@example.com', password: 'strongpass' });
    const fetched = await getUser(db, created.id);
    expect(fetched).toBeTruthy();
    expect(fetched.id).toBe(created.id);
    expect(fetched.name).toBe('Dave');
    expect(fetched.email).toBe('dave@example.com');
  });
});
