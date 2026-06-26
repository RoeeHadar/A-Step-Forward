import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL);

const dbinfo = await sql`SELECT current_database() AS db, current_user AS usr, current_schema() AS schema`;
console.log('connection:', dbinfo[0]);

const schemas = await sql`SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('pg_catalog','information_schema','pg_toast') ORDER BY schema_name`;
console.log('schemas:', schemas.map((s) => s.schema_name).join(', '));

const tables = await sql`
  SELECT table_schema, table_name FROM information_schema.tables
  WHERE table_schema NOT IN ('pg_catalog','information_schema','pg_toast')
  ORDER BY table_schema, table_name
`;
console.log('\n=== all tables ===');
tables.forEach((t) => console.log('  ' + t.table_schema + '.' + t.table_name));

const candidates = tables.filter((t) => /content|bagrut|section|chapter/.test(t.table_name));
console.log('\n=== content-related tables ===');
candidates.forEach((t) => console.log('  ' + t.table_schema + '.' + t.table_name));

for (const t of candidates) {
  try {
    const counts = await sql.unsafe(`SELECT subject, COUNT(*)::int AS n FROM "${t.table_schema}"."${t.table_name}" GROUP BY subject ORDER BY subject`);
    console.log('\n--- ' + t.table_schema + '.' + t.table_name + ' ---');
    counts.forEach((r) => console.log('  ' + r.subject.padEnd(40) + r.n));
  } catch (e) {
    console.log(t.table_name + ' has no subject column or count failed: ' + e.message);
  }
}
