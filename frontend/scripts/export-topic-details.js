const fs = require('fs');
const path = require('path');
const ts = require('typescript');

const sourcePath = path.resolve(__dirname, '..', 'app', 'topic', '[topicKey].tsx');

const MENU_TITLES = {
  visa: '비자',
  topik: 'TOPIK',
  register: '입학 등록',
  scholarship: '장학금',
  life: '생활 정보',
};

function evaluate(node) {
  if (!node) return undefined;

  if (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) {
    return node.text;
  }

  if (node.kind === ts.SyntaxKind.TrueKeyword) return true;
  if (node.kind === ts.SyntaxKind.FalseKeyword) return false;
  if (node.kind === ts.SyntaxKind.NullKeyword) return null;

  if (ts.isNumericLiteral(node)) {
    return Number(node.text);
  }

  if (ts.isArrayLiteralExpression(node)) {
    return node.elements.map((element) => evaluate(element));
  }

  if (ts.isObjectLiteralExpression(node)) {
    return node.properties.reduce((value, property) => {
      if (!ts.isPropertyAssignment(property)) return value;
      const name = property.name;
      const key = ts.isIdentifier(name) || ts.isStringLiteral(name) ? name.text : name.getText();
      value[key] = evaluate(property.initializer);
      return value;
    }, {});
  }

  if (ts.isAsExpression(node) || ts.isTypeAssertionExpression(node)) {
    return evaluate(node.expression);
  }

  return undefined;
}

function loadConstants() {
  const source = fs.readFileSync(sourcePath, 'utf8');
  const sourceFile = ts.createSourceFile(
    sourcePath,
    source,
    ts.ScriptTarget.Latest,
    true,
    ts.ScriptKind.TSX
  );
  const constants = {};

  for (const statement of sourceFile.statements) {
    if (!ts.isVariableStatement(statement)) continue;
    for (const declaration of statement.declarationList.declarations) {
      if (!ts.isIdentifier(declaration.name)) continue;
      constants[declaration.name.text] = evaluate(declaration.initializer);
    }
  }

  return constants;
}

function labelByKey(tabs, key) {
  return tabs.find((tab) => tab.key === key)?.label || key;
}

function sectionContent(section) {
  const lines = [];
  if (Array.isArray(section.items)) {
    for (const item of section.items) {
      if (item) lines.push(`- ${item}`);
    }
  }
  if (Array.isArray(section.tableColumns) && Array.isArray(section.tableRows)) {
    lines.push(`표 컬럼: ${section.tableColumns.join(' | ')}`);
    for (const row of section.tableRows) {
      lines.push(`표 행: ${row.join(' | ')}`);
    }
  }
  return lines.join('\n');
}

function pushSection(rows, menuKey, partKey, partTitle, sectionTitle, content, sourceUrl) {
  if (!content || !content.trim()) return;
  rows.push({
    menuKey,
    menuTitle: MENU_TITLES[menuKey],
    partKey,
    partTitle,
    sectionTitle,
    content,
    sourceUrl,
  });
}

function pushTextSections(rows, menuKey, partKey, partTitle, sections) {
  for (const section of sections || []) {
    pushSection(rows, menuKey, partKey, partTitle, section.title, sectionContent(section));
  }
}

function pushLinks(rows, menuKey, partKey, partTitle, sectionTitle, links) {
  for (const link of links || []) {
    pushSection(rows, menuKey, partKey, partTitle, `${sectionTitle}: ${link.title}`, link.url, link.url);
  }
}

function buildRows(constants) {
  const rows = [];

  for (const [partKey, sections] of Object.entries(constants.VISA_CONTENT || {})) {
    pushTextSections(rows, 'visa', partKey, labelByKey(constants.VISA_TABS || [], partKey), sections);
  }
  pushLinks(rows, 'visa', 'links', labelByKey(constants.VISA_TABS || [], 'links'), '공식 링크', constants.VISA_LINKS);

  for (const [partKey, sections] of Object.entries(constants.TOPIK_CONTENT || {})) {
    pushTextSections(rows, 'topik', partKey, labelByKey(constants.TOPIK_TABS || [], partKey), sections);
  }

  pushSection(
    rows,
    'register',
    'steps',
    labelByKey(constants.REGISTER_TABS || [], 'steps'),
    '지원 절차',
    (constants.REGISTER_STEPS || []).map((step, index) => `${index + 1}. ${step}`).join('\n')
  );
  for (const card of constants.TUITION_CARDS || []) {
    pushSection(
      rows,
      'register',
      'info',
      labelByKey(constants.REGISTER_TABS || [], 'info'),
      `학비/정보: ${card.title}`,
      [`금액: ${card.value}`, `상세: ${card.detail}`].join('\n')
    );
  }
  for (const [documentKey, sections] of Object.entries(constants.REGISTER_DOCUMENTS || {})) {
    const documentTitle = labelByKey(constants.REGISTER_DOCUMENT_TABS || [], documentKey);
    for (const section of sections || []) {
      pushSection(
        rows,
        'register',
        'documents',
        labelByKey(constants.REGISTER_TABS || [], 'documents'),
        `${documentTitle}: ${section.title}`,
        sectionContent(section)
      );
    }
  }
  for (const item of constants.REGISTER_SCHEDULE || []) {
    pushSection(
      rows,
      'register',
      'schedule',
      labelByKey(constants.REGISTER_TABS || [], 'schedule'),
      `학사일정: ${item.term}`,
      [
        `신청: ${item.apply}`,
        `레벨테스트: ${item.levelTest}`,
        `오리엔테이션: ${item.orientation}`,
        `개강: ${item.start}`,
        `종료: ${item.end}`,
      ].join('\n')
    );
  }

  const scholarshipGroups = {
    korean: constants.KOREAN_SCHOLARSHIPS,
    gks: constants.GKS_SCHOLARSHIPS,
    achievement: constants.ACHIEVEMENT_SCHOLARSHIPS,
    etc: constants.ETC_SCHOLARSHIPS,
  };
  for (const [partKey, sections] of Object.entries(scholarshipGroups)) {
    pushTextSections(
      rows,
      'scholarship',
      partKey,
      labelByKey(constants.SCHOLARSHIP_TABS || [], partKey),
      sections
    );
  }
  pushLinks(rows, 'scholarship', 'links', '공식 링크', '장학금 공식 링크', constants.SCHOLARSHIP_LINKS);

  pushTextSections(
    rows,
    'life',
    'support',
    labelByKey(constants.LIFE_TABS || [], 'support'),
    constants.LIFE_SUPPORT_SECTIONS
  );
  pushLinks(
    rows,
    'life',
    'support',
    labelByKey(constants.LIFE_TABS || [], 'support'),
    '생활지원 공식 링크',
    constants.LIFE_LINKS
  );
  pushTextSections(
    rows,
    'life',
    'dorm',
    labelByKey(constants.LIFE_TABS || [], 'dorm'),
    constants.DORM_APPLICATION_SECTIONS
  );
  for (const card of constants.DORM_FEE_CARDS || []) {
    pushSection(
      rows,
      'life',
      'dorm',
      labelByKey(constants.LIFE_TABS || [], 'dorm'),
      `기숙사비: ${card.title}`,
      [
        `봄/가을: ${card.spring}`,
        `여름/겨울: ${card.vacation}`,
        card.note ? `비고: ${card.note}` : '',
      ]
        .filter(Boolean)
        .join('\n')
    );
  }
  pushSection(
    rows,
    'life',
    'dorm',
    labelByKey(constants.LIFE_TABS || [], 'dorm'),
    '기숙사 유의사항',
    (constants.DORM_NOTES || []).map((note) => `- ${note}`).join('\n')
  );
  pushLinks(
    rows,
    'life',
    'dorm',
    labelByKey(constants.LIFE_TABS || [], 'dorm'),
    '기숙사 동영상 링크',
    constants.DORM_VIDEO_LINKS
  );

  return rows;
}

function aggregateRows(rows) {
  const grouped = new Map();

  for (const row of rows) {
    const key = `${row.menuKey}/${row.partKey}`;
    const existing =
      grouped.get(key) ||
      {
        menuKey: row.menuKey,
        menuTitle: row.menuTitle,
        partKey: row.partKey,
        sections: [],
      };
    existing.sections.push(
      [`## ${row.sectionTitle}`, row.content, row.sourceUrl ? `링크: ${row.sourceUrl}` : '']
        .filter(Boolean)
        .join('\n')
    );
    grouped.set(key, existing);
  }

  return Array.from(grouped.values()).map((row) => ({
    menuKey: row.menuKey,
    menuTitle: row.menuTitle,
    partKey: row.partKey,
    content: row.sections.join('\n\n'),
  }));
}

const rows = aggregateRows(buildRows(loadConstants()));
process.stdout.write(
  JSON.stringify(rows).replace(/[^\x00-\x7F]/g, (char) => {
    const codePoint = char.codePointAt(0);
    if (codePoint <= 0xffff) {
      return `\\u${codePoint.toString(16).padStart(4, '0')}`;
    }
    const high = Math.floor((codePoint - 0x10000) / 0x400) + 0xd800;
    const low = ((codePoint - 0x10000) % 0x400) + 0xdc00;
    return `\\u${high.toString(16).padStart(4, '0')}\\u${low
      .toString(16)
      .padStart(4, '0')}`;
  })
);
