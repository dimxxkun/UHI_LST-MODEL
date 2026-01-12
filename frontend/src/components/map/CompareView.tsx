import React from 'react';
import { TiffViewer } from './TiffViewer';
import { MapViewer } from './MapViewer';

interface CompareViewProps {
    inputFile: File | null;
    // outputUrl? or outputData? For now just placeholders
}

export const CompareView: React.FC<CompareViewProps> = ({ inputFile }) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
            <div className="flex flex-col h-full bg-white dark:bg-slate-900 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden">
                <div className="p-3 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 font-medium text-sm">
                    Input Preview
                </div>
                <div className="flex-1 p-2 min-h-[300px]">
                    <TiffViewer file={inputFile} className="w-full h-full" />
                </div>
            </div>

            <div className="flex flex-col h-full bg-white dark:bg-slate-900 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden">
                <div className="p-3 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 font-medium text-sm">
                    Map / Result overlay
                </div>
                <div className="flex-1 min-h-[300px]">
                    <MapViewer className="h-full w-full" />
                </div>
            </div>
        </div>
    );
};
