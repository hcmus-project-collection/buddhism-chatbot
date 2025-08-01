// Mapping of book IDs to readable book names
// This should match the BOOK_ID_MAP in backend/constants.py
export const BOOK_ID_TO_NAME: Record<string, string> = {
  'RBI_002': 'An Sĩ Toàn Thư',
  'RBI_007': 'Quan Âm Thị Kính',
  'RBI_008': 'Thiền Uyển Tập Anh',
  'RBI_010': 'Kinh Tương Ưng Bộ',
};

export function getBookName(bookId: string): string {
  return BOOK_ID_TO_NAME[bookId] || bookId;
}