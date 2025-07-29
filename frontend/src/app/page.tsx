'use client';

import { useState } from 'react';
import QueryForm from '@/components/QueryForm';
import QueryResults from '@/components/QueryResults';
import { queryBackend } from '@/lib/api';
import { QueryRequest, QueryResponse } from '@/types/api';

export default function Home() {
    const [results, setResults] = useState<QueryResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleQuery = async (request: QueryRequest) => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await queryBackend(request);
            setResults(response);
        } catch (err) {
            console.error('Query failed:', err);
            setError('Failed to get response. Please check if the backend is running and try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="min-h-screen py-8 px-4">
            <div className="container mx-auto">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-gray-800 dark:text-gray-200 mb-4">
                        Eastern Religion Chatbot
                    </h1>
                    <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                        Ask questions about Buddhism, Hinduism, Taoism, and other Eastern philosophical traditions.
                        Get informed answers backed by relevant sources.
                    </p>
                </div>

                {/* Query Form */}
                <QueryForm onSubmit={handleQuery} isLoading={isLoading} />

                {/* Error Display */}
                {error && (
                    <div className="w-full max-w-4xl mx-auto mt-6">
                        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-xl p-4">
                            <div className="flex items-center">
                                <div className="w-2 h-2 bg-red-500 rounded-full mr-3"></div>
                                <h3 className="text-red-800 dark:text-red-200 font-medium">Error</h3>
                            </div>
                            <p className="text-red-700 dark:text-red-300 mt-2">{error}</p>
                        </div>
                    </div>
                )}

                {/* Results */}
                {results && !isLoading && (
                    <div className="mt-8">
                        <QueryResults results={results} />
                    </div>
                )}

                {/* Loading State */}
                {isLoading && (
                    <div className="w-full max-w-4xl mx-auto mt-8">
                        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700">
                            <div className="flex items-center justify-center space-x-3">
                                <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                                <span className="text-gray-700 dark:text-gray-300">Processing your question...</span>
                            </div>
                        </div>
                    </div>
                )}

                {/* Footer */}
                <footer className="mt-16 text-center text-gray-500 dark:text-gray-400 text-sm">
                    <p>
                        Powered by AI and vector search technology
                    </p>
                </footer>
            </div>
        </main>
    );
}