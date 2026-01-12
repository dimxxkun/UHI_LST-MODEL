import { useState } from 'react';
import { UploadPanel } from '@/components/analysis/UploadPanel';
import type { BandFiles } from '@/components/analysis/UploadPanel';
import { MapViewer } from '@/components/map/MapViewer';
import { TiffLayer } from '@/components/map/TiffLayer';

export const AnalysisPage = () => {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [bandFiles, setBandFiles] = useState<BandFiles>({ B10: null, B5: null, B4: null });

    const handleFileSelect = (file: File) => {
        setSelectedFile(file);
    };

    const handleBandFilesSelect = (bands: BandFiles) => {
        setBandFiles(bands);
        // When using individual bands, clear composite file
        if (bands.B10 || bands.B5 || bands.B4) {
            setSelectedFile(null);
        }
    };

    // Determine which file to preview (composite or Band 10 for thermal preview)
    const previewFile = selectedFile || bandFiles.B10;

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)] gap-4">
            <div className="flex-none">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Analysis Workspace</h1>
                <p className="text-slate-500 dark:text-slate-400">Upload Landsat imagery to generate LST and UHI maps.</p>
            </div>

            <div className="flex-1 flex gap-4 min-h-0">
                {/* Left Panel: Upload & Config (30%) */}
                <div className="w-80 flex-none flex flex-col gap-4 overflow-y-auto pr-2">
                    <UploadPanel
                        onFileSelect={handleFileSelect}
                        onBandFilesSelect={handleBandFilesSelect}
                        selectedFile={selectedFile}
                    />

                    {/* Analysis Config Placeholder */}
                    <div className="card p-4">
                        <h3 className="font-medium mb-3 text-slate-800 dark:text-slate-100">Configuration</h3>
                        <div className="space-y-3">
                            <div>
                                <label className="block text-sm text-slate-600 dark:text-slate-300 mb-1">Model</label>
                                <select className="w-full p-2 border rounded-md dark:bg-slate-800 dark:border-slate-700 dark:text-slate-100">
                                    <option>Random Forest (Default)</option>
                                    <option>CNN (Experimental)</option>
                                </select>
                            </div>
                            <button className="btn-primary w-full mt-2">
                                Run Analysis
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right Panel: Map (70%) */}
                <div className="flex-1 card p-0 overflow-hidden relative border-0 shadow-md">
                    <MapViewer>
                        {previewFile && <TiffLayer file={previewFile} />}
                    </MapViewer>
                </div>
            </div>
        </div>
    );
};
