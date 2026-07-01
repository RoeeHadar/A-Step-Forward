/**
 * Incremental git commit + push for long-running CI expansion jobs.
 */
import { execSync } from 'node:child_process';

function run(cmd) {
  return execSync(cmd, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
}

export function pushProgressCommit(completedCount, { dryRun = false, maxAttempts = 3 } = {}) {
  if (dryRun || process.env.AUTO_COMMIT !== 'true') return false;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      run('git config user.name "github-actions[bot]"');
      run('git config user.email "41898282+github-actions[bot]@users.noreply.github.com"');
      run('git add scripts/seed_data/lessons/ scripts/.expand-substantive-progress.json');

      const staged = run('git diff --cached --name-only');
      if (!staged) {
        console.log('[git-push] no staged changes — skip commit');
        return false;
      }

      run(
        `git commit -m "feat(curriculum): substantive expansion progress (${completedCount} lessons)"`,
      );

      try {
        run('git pull --rebase --autostash origin main');
      } catch {
        // Fresh checkout may not need rebase
      }

      run('git push origin HEAD:main');
      console.log(`[git-push] pushed ${completedCount} lessons to main`);
      return true;
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      const stderr = err?.stderr?.toString?.() ?? '';
      console.error(
        `[git-push] attempt ${attempt}/${maxAttempts} failed: ${msg.slice(0, 120)} ${stderr.slice(0, 200)}`,
      );
      if (attempt < maxAttempts) {
        run('sleep 5');
      }
    }
  }
  return false;
}
