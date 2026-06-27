import { neon } from '@neondatabase/serverless';
const sql = neon(process.env.DATABASE_URL);
try {
  const r = await sql`SELECT 1 as ping`;
  console.log('Connected OK:', r);
} catch (e) {
  console.error('Connection failed:', e.message);
  process.exit(1);
}
