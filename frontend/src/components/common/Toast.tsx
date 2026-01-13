import React from 'react';
import { useAnalysisStore } from '@/stores/analysisStore';
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';
import { clsx } from 'clsx';

export const Toast: React.FC = () => {
    const { notification, hideNotification } = useAnalysisStore();

    if (!notification) return null;

    const { message, type } = notification;

    const typeConfig = {
        success: {
            icon: <CheckCircle className="w-5 h-5 text-green-500" />,
            border: 'border-green-200 dark:border-green-900',
            bg: 'bg-green-50 dark:bg-green-900/20',
            text: 'text-green-800 dark:text-green-300'
        },
        error: {
            icon: <AlertCircle className="w-5 h-5 text-red-500" />,
            border: 'border-red-200 dark:border-red-900',
            bg: 'bg-red-50 dark:bg-red-900/20',
            text: 'text-red-800 dark:text-red-300'
        },
        info: {
            icon: <Info className="w-5 h-5 text-blue-500" />,
            border: 'border-blue-200 dark:border-blue-900',
            bg: 'bg-blue-50 dark:bg-blue-900/20',
            text: 'text-blue-800 dark:text-blue-300'
        }
    };

    const config = typeConfig[type];

    return (
        <div className="fixed bottom-6 right-6 z-[9999] animate-in fade-in slide-in-from-bottom-5 duration-300">
            <div className={clsx(
                "flex items-center gap-3 px-4 py-3 rounded-xl border shadow-lg backdrop-blur-md min-w-[300px]",
                config.border,
                config.bg,
                config.text
            )}>
                <div className="flex-shrink-0">
                    {config.icon}
                </div>
                <div className="flex-1 text-sm font-medium">
                    {message}
                </div>
                <button
                    onClick={hideNotification}
                    className="flex-shrink-0 p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
                >
                    <X className="w-4 h-4 opacity-50" />
                </button>
            </div>
        </div>
    );
};
