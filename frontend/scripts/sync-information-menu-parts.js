const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const projectRoot = path.resolve(__dirname, '..');
const envPath = path.join(projectRoot, '.env');

function parseEnvFile(filePath) {
  if (!fs.existsSync(filePath)) {
    return {};
  }

  return fs
    .readFileSync(filePath, 'utf8')
    .split(/\r?\n/)
    .reduce((entries, line) => {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) {
        return entries;
      }

      const separatorIndex = trimmed.indexOf('=');
      if (separatorIndex === -1) {
        return entries;
      }

      const key = trimmed.slice(0, separatorIndex).trim();
      const value = trimmed.slice(separatorIndex + 1).trim();
      entries[key] = value;
      return entries;
    }, {});
}

function loadInformationMenuParts() {
  const output = execFileSync('node', ['scripts/export-topic-details.js'], {
    cwd: projectRoot,
    encoding: 'utf8',
  });
  const rows = JSON.parse(output);
  if (!Array.isArray(rows) || rows.length === 0) {
    throw new Error('No information menu rows were exported.');
  }
  return rows;
}

async function main() {
  const env = {
    ...parseEnvFile(envPath),
    ...process.env,
  };
  const apiBaseUrl = env.INFORMATION_MENU_API_URL || env.EXPO_PUBLIC_API_BASE_URL;

  if (!apiBaseUrl) {
    throw new Error(
      'Set INFORMATION_MENU_API_URL or EXPO_PUBLIC_API_BASE_URL in frontend/.env.'
    );
  }

  const rows = loadInformationMenuParts();
  const response = await fetch(`${apiBaseUrl.replace(/\/$/, '')}/information-menu/parts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ rows }),
  });

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(
      `Failed to sync information menu parts (${response.status}): ${JSON.stringify(body)}`
    );
  }

  console.log(`Saved ${body.saved ?? rows.length} information menu parts.`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
