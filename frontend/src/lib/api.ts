import axios from 'axios';
import { QueryRequest, QueryResponse, BooksResponse } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const healthCheck = async (): Promise<{ status: string }> => {
    const response = await apiClient.get('/');
    return response.data;
};

export const queryBackend = async (request: QueryRequest): Promise<QueryResponse> => {
    const response = await apiClient.post('/query', request);
    return response.data;
};

export const fetchBooks = async (): Promise<BooksResponse> => {
    const response = await apiClient.get('/books');
    return response.data;
};