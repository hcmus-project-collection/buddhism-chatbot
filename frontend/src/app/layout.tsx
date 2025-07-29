import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Buddhism Chatbot',
  description: 'Ask questions about Buddhism and get informed answers',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        {children}
      </body>
    </html>
  )
}