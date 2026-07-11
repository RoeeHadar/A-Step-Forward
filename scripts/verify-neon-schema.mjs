#!/usr/bin/env node
import { neon } from '@neondatabase/serverless';

const url = process.env.DATABASE_URL ?? process.env.POSTGRES_URL ?? '';
if (!url) {
  console.error('DATABASE_URL not set');
  process.exit(1);
}

const sql = neon(url);
const host = new URL(url).hostname;
console.log('host:', host);

const versionRows = await sql`SELECT version_num FROM alembic_version LIMIT 1`;
console.log('alembic:', versionRows[0]?.version_num ?? 'none');

const tables = await sql`
  SELECT table_name
  FROM information_schema.tables
  WHERE table_schema = 'public'
    AND table_name IN ('chat_turns', 'learner_profiles', 'learning_plans')
  ORDER BY table_name
`;
const names = tables.map((r) => r.table_name);
console.log('tables:', names.length ? names.join(', ') : 'NONE');
console.log('tables_ok:', names.length === 3 ? 'yes' : 'no');
