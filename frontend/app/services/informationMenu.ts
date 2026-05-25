import { apiRequest } from './api';
import type { InformationMenuPart } from '../data/informationMenuContent';

export type InformationMenuEmbeddingRow = InformationMenuPart & {
  embedding: number[];
  embeddingModel: string;
};

export async function saveInformationMenuEmbeddings(
  rows: InformationMenuEmbeddingRow[]
) {
  assertRowsHaveEmbeddings(rows);

  return apiRequest<{ saved: number }>('/information-menu/embeddings', {
    method: 'POST',
    body: JSON.stringify({ rows }),
  });
}

export async function saveInformationMenuParts(rows: InformationMenuPart[]) {
  return apiRequest<{ saved: number }>('/information-menu/parts', {
    method: 'POST',
    body: JSON.stringify({ rows }),
  });
}

function assertRowsHaveEmbeddings(rows: InformationMenuEmbeddingRow[]) {
  for (const row of rows) {
    if (!Array.isArray(row.embedding) || row.embedding.length === 0) {
      throw new Error(
        `Missing embedding vector for ${row.menuKey}/${row.partKey}/${row.sectionTitle}`
      );
    }

    if (!row.embeddingModel.trim()) {
      throw new Error(
        `Missing embedding model for ${row.menuKey}/${row.partKey}/${row.sectionTitle}`
      );
    }
  }
}
