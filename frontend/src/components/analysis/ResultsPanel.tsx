import React from 'react';

interface ResultsPanelProps {
    className?: string;
}

export const ResultsPanel: React.FC<ResultsPanelProps> = ({ className }) => {
    return (
        <div className={`card p-4 ${className}`}>
            <h3 className="font-medium mb-3 text-slate-800 dark:text-slate-100">Results</h3>
            <div className="text-center py-8 text-slate-500 text-sm">
                Run analysis to view statistics
            </div>
        </div>
    );
};
