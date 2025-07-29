'use client';

import { QueryResponse } from '@/types/api';
import { getBookName } from '@/lib/bookMapping';

interface QueryResultsProps {
    results: QueryResponse;
}

export default function QueryResults({ results }: QueryResultsProps) {
    return (
        <div className="w-full max-w-4xl mx-auto space-y-6">
            {/* Answer Section */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4 flex items-center">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                    Answer
                </h2>
                <div className="prose dark:prose-invert max-w-none">
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                        {results.answer}
                    </p>
                </div>
            </div>

            {/* Relevant Sources Section */}
            {results.relevant_texts && results.relevant_texts.length > 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                    <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4 flex items-center">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                        Relevant Sources ({results.relevant_texts.length})
                    </h2>
                    <div className="space-y-4">
                        {results.relevant_texts.map((text, index) => (
                            <div
                                key={text.sentence_id || index}
                                className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:shadow-md transition-shadow duration-200"
                            >
                                <div className="flex justify-between items-start mb-3">
                                    <div className="flex flex-col space-y-1">
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                                            {text.book_id ? getBookName(text.book_id) : `Source ${index + 1}`}
                                        </span>
                                        {text.chapter_id && text.page && (
                                            <span className="text-xs text-gray-500 dark:text-gray-400">
                                                Chapter {text.chapter_id}, Page {text.page}
                                            </span>
                                        )}
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <span className="text-xs text-gray-500 dark:text-gray-400">
                                            Relevance: {(text.score * 100).toFixed(1)}%
                                        </span>
                                        <div
                                            className="w-16 h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden"
                                            title={`Relevance score: ${(text.score * 100).toFixed(1)}%`}
                                        >
                                            <div
                                                className="h-full bg-gradient-to-r from-red-400 via-yellow-400 to-green-400 rounded-full transition-all duration-300"
                                                style={{ width: `${Math.min(100, text.score * 100)}%` }}
                                            />
                                        </div>
                                    </div>
                                </div>
                                <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">
                                    {text.text}
                                </p>
                                {(text.meta && Object.keys(text.meta).length > 0) || text.book_id && (
                                    <div className="mt-2 pt-2 border-t border-gray-100 dark:border-gray-600">
                                        <details className="group">
                                            <summary className="cursor-pointer text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                                                Show technical details
                                            </summary>
                                            <div className="mt-2 space-y-1">
                                                {text.book_id && (
                                                    <div className="text-xs text-gray-600 dark:text-gray-400">
                                                        <span className="font-medium">Book ID:</span> {text.book_id}
                                                    </div>
                                                )}
                                                {text.chapter_id && (
                                                    <div className="text-xs text-gray-600 dark:text-gray-400">
                                                        <span className="font-medium">Chapter ID:</span> {text.chapter_id}
                                                    </div>
                                                )}
                                                {text.page && (
                                                    <div className="text-xs text-gray-600 dark:text-gray-400">
                                                        <span className="font-medium">Page:</span> {text.page}
                                                    </div>
                                                )}
                                                {text.sentence_id && (
                                                    <div className="text-xs text-gray-600 dark:text-gray-400">
                                                        <span className="font-medium">Sentence ID:</span> {text.sentence_id}
                                                    </div>
                                                )}
                                                {text.meta && Object.entries(text.meta).map(([key, value]) => (
                                                    <div key={key} className="text-xs text-gray-600 dark:text-gray-400">
                                                        <span className="font-medium">{key}:</span> {String(value)}
                                                    </div>
                                                ))}
                                            </div>
                                        </details>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}