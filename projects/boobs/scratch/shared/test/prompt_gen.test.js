// Jest-style tests for the Educational Anatomy Prompt Generator
const promptGen = require('../src/prompt_gen.js');

const { clearPrompts, insertPromptFromSeed, getPromptById, listPrompts, countPrompts, deletePromptById, bulkGenerate } = promptGen;

describe('Prompt Generator API (logic layer, SQLite)', () => {
  beforeAll(async () => {
    // Ensure a clean DB before tests
    await clearPrompts();
  });

  test('insertPromptFromSeed creates a prompt and can be fetched by id', async () => {
    const seed = 1;
    const inserted = await insertPromptFromSeed(seed);
    expect(inserted).toHaveProperty('id');
    expect(inserted).toHaveProperty('content');
    const fetched = await getPromptById(inserted.id);
    expect(fetched).not.toBeNull();
    expect(fetched.content).toBe(inserted.content);
  });

  test('listPrompts returns paginated results and total count', async () => {
    // insert another prompt
    await insertPromptFromSeed(2);
    const list = await listPrompts(1, 5);
    expect(list).toHaveProperty('items');
    expect(Array.isArray(list.items)).toBe(true);
    const total = await countPrompts();
    expect(total).toBeGreaterThanOrEqual(2);
  });

  test('inserting duplicate seed should fail with UNIQUE constraint', async () => {
    try {
      await insertPromptFromSeed(1);
      // Should not reach here
      throw new Error('Expected duplicate seed to fail');
    } catch (e) {
      // SQLite returns an error object/string; ensure error is present
      expect(e).toBeTruthy();
      const msg = String(e);
      // Depending on sqlite3, the error message includes UNIQUE constraint
      expect(msg.includes('UNIQUE') || msg.includes('UNIQUE constraint failed')).toBe(true);
    }
  });

  test('deletePromptById removes a prompt', async () => {
    const seed = 3;
    const inserted = await insertPromptFromSeed(seed);
    const ok = await deletePromptById(inserted.id);
    expect(ok).toBe(true);
    const row = await getPromptById(inserted.id);
    expect(row).toBeNull();
  });

  test('bulkGenerate creates multiple prompts', async () => {
    await clearPrompts();
    const { generated } = await bulkGenerate(5);
    expect(generated).toBe(5);
    const total = await countPrompts();
    expect(total).toBe(5);
  });
});
