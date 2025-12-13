import { useCallback, useEffect, useMemo, useState } from "react";

export type CaseItem = {
 id: number;
 title?: string | null;
 status?: string | null;
 description?: string | null;
};

export type DocumentItem = {
 id: number;
 case_id?: number;
 title?: string | null;
 type?: string | null;
};

export type DocumentVersionItem = {
 id: number;
 document_id?: number;
 content?: string | null;
 source?: string | null;
 created_at?: string | null;
 // на случай, если backend назовёт поле иначе
 text?: string | null;
};

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
 const res = await fetch(url, {
  ...init,
  headers: {
   "Content-Type": "application/json",
   ...(init?.headers || {}),
  },
 });

 const raw = await res.text();

 let data: any = null;
 try {
  data = raw ? JSON.parse(raw) : null;
 } catch {
  // Если пришёл HTML/текст — покажем в ошибке первые 200 символов
  if (!res.ok) {
   throw new Error(`HTTP ${res.status}: ${raw.slice(0, 200)}`);
  }
  // Если ok, но не JSON — вернём как строку (на всякий случай)
  return raw as unknown as T;
 }

 if (!res.ok) {
  const msg =
   (data && (data.error || data.message)) || `HTTP ${res.status}`;
  throw new Error(String(msg));
 }

 return data as T;
}

export function useCasesDocuments(apiBaseRaw: string) {
 const apiBase = useMemo(
  () => (apiBaseRaw || "/api").replace(/\/$/, ""),
  [apiBaseRaw]
 );

 const [cases, setCases] = useState<CaseItem[]>([]);
 const [documents, setDocuments] = useState<DocumentItem[]>([]);
 const [versions, setVersions] = useState<DocumentVersionItem[]>([]);

 const [activeCaseId, setActiveCaseId] = useState<number | null>(null);
 const [activeDocumentId, setActiveDocumentId] = useState<number | null>(null);

 const [loadingCases, setLoadingCases] = useState(false);
 const [loadingDocuments, setLoadingDocuments] = useState(false);
 const [loadingVersions, setLoadingVersions] = useState(false);

 const [error, setError] = useState<string | null>(null);

 const loadCases = useCallback(async () => {
  setLoadingCases(true);
  setError(null);
  try {
   const data = await fetchJson<CaseItem[]>(`${apiBase}/cases`);
   setCases(Array.isArray(data) ? data : []);
  } catch (e: any) {
   setError(e?.message ? String(e.message) : String(e));
  } finally {
   setLoadingCases(false);
  }
 }, [apiBase]);

 const loadDocuments = useCallback(
  async (caseId: number) => {
   setLoadingDocuments(true);
   setError(null);
   try {
    const data = await fetchJson<DocumentItem[]>(
     `${apiBase}/cases/${caseId}/documents`
    );
    setDocuments(Array.isArray(data) ? data : []);
   } catch (e: any) {
    setError(e?.message ? String(e.message) : String(e));
    setDocuments([]);
   } finally {
    setLoadingDocuments(false);
   }
  },
  [apiBase]
 );

 const loadVersions = useCallback(
  async (documentId: number) => {
   setLoadingVersions(true);
   setError(null);
   try {
    const data = await fetchJson<DocumentVersionItem[]>(
     `${apiBase}/documents/${documentId}/versions`
    );
    setVersions(Array.isArray(data) ? data : []);
   } catch (e: any) {
    setError(e?.message ? String(e.message) : String(e));
    setVersions([]);
   } finally {
    setLoadingVersions(false);
   }
  },
  [apiBase]
 );

 const selectCase = useCallback(
  async (caseId: number) => {
   setActiveCaseId(caseId);
   setActiveDocumentId(null);
   setVersions([]);
   await loadDocuments(caseId);
  },
  [loadDocuments]
 );

 const selectDocument = useCallback(
  async (documentId: number) => {
   setActiveDocumentId(documentId);
   await loadVersions(documentId);
  },
  [loadVersions]
 );

 const reloadVersions = useCallback(
  async (documentId: number) => {
   await loadVersions(documentId);
  },
  [loadVersions]
 );

 const saveVersion = useCallback(
  async (documentId: number, content: string, source: "user" | "ai") => {
   setError(null);
   await fetchJson<{ id?: number }>(
    `${apiBase}/documents/${documentId}/versions`,
    {
     method: "POST",
     body: JSON.stringify({ content, source }),
    }
   );
  },
  [apiBase]
 );

 // Автозагрузка дел при старте
 useEffect(() => {
  loadCases();
 }, [loadCases]);

 return {
  cases,
  documents,
  versions,
  loadingCases,
  loadingDocuments,
  loadingVersions,
  error,
  activeCaseId,
  activeDocumentId,
  selectCase,
  selectDocument,
  reloadVersions,
  saveVersion,
 };
}

