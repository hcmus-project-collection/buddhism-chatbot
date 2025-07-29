'use client';

import { useState, useEffect } from 'react';
import { QueryRequest, Book } from '@/types/api';
import { fetchBooks } from '@/lib/api';

interface QueryFormProps {
    onSubmit: (request: QueryRequest) => void;
    isLoading: boolean;
}

export default function QueryForm({ onSubmit, isLoading }: QueryFormProps) {
    const [query, setQuery] = useState('');
    const [topK, setTopK] = useState(5);
    const [usingTools, setUsingTools] = useState(false);
    const [books, setBooks] = useState<Book[]>([]);
    const [selectedBookId, setSelectedBookId] = useState<string>('');
    const [isLoadingBooks, setIsLoadingBooks] = useState(true);

    useEffect(() => {
        const loadBooks = async () => {
            try {
                const response = await fetchBooks();
                setBooks(response.books);
            } catch (error) {
                console.error('Failed to load books:', error);
            } finally {
                setIsLoadingBooks(false);
            }
        };

        loadBooks();
    }, []);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (query.trim()) {
            const metadata_filter: Record<string, string> = {};
            if (selectedBookId) {
                metadata_filter.book_id = selectedBookId;
            }

            onSubmit({
                query: query.trim(),
                top_k: topK,
                using_tools: usingTools,
                metadata_filter
            });
        }
    };

    return (
        <form onSubmit={handleSubmit} className="w-full max-w-4xl mx-auto space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="space-y-4">
                    <div>
                        <label htmlFor="query" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Ask your question about Buddhism
                        </label>
                        <textarea
                            id="query"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="e.g., What is the concept of karma in Buddhism?"
                            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
                            rows={3}
                            disabled={isLoading}
                        />
                    </div>

                    <div className="flex flex-col sm:flex-row gap-4">
                        <div className="flex-1">
                            <label htmlFor="topK" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Number of sources (1-10)
                            </label>
                            <input
                                id="topK"
                                type="number"
                                value={topK}
                                onChange={(e) => setTopK(Math.max(1, Math.min(10, parseInt(e.target.value) || 5)))}
                                min="1"
                                max="10"
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                                disabled={isLoading}
                            />
                        </div>

                        <div className="flex-1">
                            <label htmlFor="bookFilter" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Filter by book
                            </label>
                            <select
                                id="bookFilter"
                                value={selectedBookId}
                                onChange={(e) => setSelectedBookId(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                                disabled={isLoading || isLoadingBooks}
                            >
                                <option value="">All books</option>
                                {books.map((book) => (
                                    <option key={book.id} value={book.id}>
                                        {book.title}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="flex items-end">
                            <label className="flex items-center space-x-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                                <input
                                    type="checkbox"
                                    checked={usingTools}
                                    onChange={(e) => setUsingTools(e.target.checked)}
                                    className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                                    disabled={isLoading}
                                />
                                <span>Use AI tools</span>
                            </label>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={!query.trim() || isLoading}
                        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-3 px-6 rounded-lg transition duration-200 ease-in-out transform hover:scale-[1.02] disabled:hover:scale-100 disabled:cursor-not-allowed"
                    >
                        {isLoading ? (
                            <div className="flex items-center justify-center space-x-2">
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                <span>Searching...</span>
                            </div>
                        ) : (
                            'Ask Question'
                        )}
                    </button>
                </div>
            </div>
        </form>
    );
}