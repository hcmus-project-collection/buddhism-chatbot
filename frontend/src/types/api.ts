export interface RelevantText {
  text: string;
  score: number;
  sentence_id: string;
  book_id: string;
  chapter_id: string;
  page: string;
  meta: Record<string, any>;
}

export interface QueryRequest {
  query: string;
  top_k?: number;
  metadata_filter?: Record<string, string>;
  using_tools?: boolean;
}

export interface QueryResponse {
  answer: string;
  relevant_texts: RelevantText[];
}

export interface Book {
  id: string;
  title: string;
}

export interface BooksResponse {
  books: Book[];
}