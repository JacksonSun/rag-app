export type PromptRequest = {
  query: string;
};

export type ContactPerson = {
  name: string;
  email?: string;
  department?: string;
  employee_number?: string;
  position?: string;
  profile_photo?: string;
};

export type SourceMetadata = {
  source: string;
  source_id: string;
  url: string;
  created_at: null | string;
  author: string;
  document_id: string; // uuid
  title: string;
};

export type ResultSource = {
  id: string; // uuid
  text: string;
  score: number;
  embedding: number[];
  metadata: SourceMetadata;
};

export type ExternalSource = {
  title: string;
  snippet: string;
  url: string;
};

export type WebSummaryRequest = {
  query: string;
  url: string;
};
