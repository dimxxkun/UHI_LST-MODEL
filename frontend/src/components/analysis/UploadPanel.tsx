import React, { useCallback, useState } from 'react';
import { Upload, File as FileIcon, CheckCircle, X } from 'lucide-react';
import { clsx } from 'clsx';

// Band configuration for Landsat 8/9
const BAND_CONFIG = [
    { id: 'B10', label: 'Band 10 (Thermal)', description: 'TIRS1 - Required for LST' },
    { id: 'B5', label: 'Band 5 (NIR)', description: 'Near Infrared - For NDVI' },
    { id: 'B4', label: 'Band 4 (Red)', description: 'Red - For NDVI' },
];

export interface BandFiles {
    B10: File | null;
    B5: File | null;
    B4: File | null;
}

interface UploadPanelProps {
    onFileSelect: (file: File) => void;
    onBandFilesSelect?: (bands: BandFiles) => void;
    selectedFile: File | null;
    className?: string;
}

export const UploadPanel: React.FC<UploadPanelProps> = ({
    onFileSelect,
    onBandFilesSelect,
    selectedFile,
    className
}) => {
    const [isDragOver, setIsDragOver] = useState(false);
    const [useIndividualBands, setUseIndividualBands] = useState(false);
    const [bandFiles, setBandFiles] = useState<BandFiles>({ B10: null, B5: null, B4: null });

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);

        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            if (file.name.endsWith('.tif') || file.name.endsWith('.tiff')) {
                onFileSelect(file);
            } else {
                alert("Please upload a .tif or .tiff file");
            }
        }
    }, [onFileSelect]);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);
    }, []);

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            onFileSelect(e.target.files[0]);
        }
    };

    const handleBandFileInput = (bandId: keyof BandFiles, e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            const file = e.target.files[0];
            const newBandFiles = { ...bandFiles, [bandId]: file };
            setBandFiles(newBandFiles);
            onBandFilesSelect?.(newBandFiles);
        }
    };

    const clearBandFile = (bandId: keyof BandFiles) => {
        const newBandFiles = { ...bandFiles, [bandId]: null };
        setBandFiles(newBandFiles);
        onBandFilesSelect?.(newBandFiles);
    };

    const allBandsUploaded = bandFiles.B10 && bandFiles.B5 && bandFiles.B4;

    return (
        <div className={clsx("p-4 bg-white dark:bg-slate-900 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800", className)}>
            <h3 className="text-lg font-medium text-slate-800 dark:text-slate-100 mb-4">Data Upload</h3>

            {/* Toggle for individual bands */}
            <label className="flex items-center gap-2 mb-4 cursor-pointer">
                <input
                    type="checkbox"
                    checked={useIndividualBands}
                    onChange={(e) => setUseIndividualBands(e.target.checked)}
                    className="w-4 h-4 text-primary-600 rounded border-slate-300 dark:border-slate-600 focus:ring-primary-500"
                />
                <span className="text-sm text-slate-700 dark:text-slate-300">Use individual bands</span>
            </label>

            {!useIndividualBands ? (
                /* Single composite upload */
                !selectedFile ? (
                    <div
                        className={clsx(
                            "border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-colors",
                            isDragOver
                                ? "border-primary-500 bg-primary-50 dark:bg-primary-900/10"
                                : "border-slate-300 dark:border-slate-700 hover:border-primary-400"
                        )}
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onClick={() => document.getElementById('file-upload')?.click()}
                    >
                        <Upload className="w-10 h-10 text-slate-400 mb-3" />
                        <p className="text-sm text-slate-600 dark:text-slate-300 font-medium">
                            Click to upload or drag & drop
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                            Landsat 8/9 standard GeoTIFF (.tif)
                        </p>
                        <input
                            id="file-upload"
                            type="file"
                            className="hidden"
                            accept=".tif,.tiff"
                            onChange={handleFileInput}
                        />
                    </div>
                ) : (
                    <div className="bg-slate-50 dark:bg-slate-800 rounded-lg p-3 flex items-center justify-between border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center overflow-hidden">
                            <FileIcon className="w-8 h-8 text-primary-500 mr-3 flex-shrink-0" />
                            <div className="min-w-0">
                                <p className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">
                                    {selectedFile.name}
                                </p>
                                <p className="text-xs text-slate-500">
                                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={() => document.getElementById('file-upload')?.click()}
                            className="text-primary-600 hover:text-primary-700 text-sm font-medium ml-2"
                        >
                            Change
                        </button>
                    </div>
                )
            ) : (
                /* Individual band uploads */
                <div className="space-y-3">
                    {BAND_CONFIG.map((band) => (
                        <div key={band.id} className="flex items-center gap-3">
                            <div className="flex-1 min-w-0 overflow-hidden">
                                {!bandFiles[band.id as keyof BandFiles] ? (
                                    <label
                                        className="flex items-center gap-3 p-3 border border-dashed border-slate-300 dark:border-slate-700 rounded-lg cursor-pointer hover:border-primary-400 transition-colors"
                                    >
                                        <Upload className="w-5 h-5 text-slate-400 flex-shrink-0" />
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-slate-700 dark:text-slate-200">
                                                {band.label}
                                            </p>
                                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                                {band.description}
                                            </p>
                                        </div>
                                        <input
                                            type="file"
                                            className="hidden"
                                            accept=".tif,.tiff"
                                            onChange={(e) => handleBandFileInput(band.id as keyof BandFiles, e)}
                                        />
                                    </label>
                                ) : (
                                    <div className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg overflow-hidden">
                                        <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                                        <div className="flex-1 min-w-0 overflow-hidden">
                                            <p className="text-xs font-semibold text-green-600 dark:text-green-400 mb-0.5">
                                                {band.label}
                                            </p>
                                            <p className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate" title={bandFiles[band.id as keyof BandFiles]?.name}>
                                                {bandFiles[band.id as keyof BandFiles]?.name}
                                            </p>
                                            <p className="text-xs text-slate-500">
                                                {((bandFiles[band.id as keyof BandFiles]?.size || 0) / 1024 / 1024).toFixed(2)} MB
                                            </p>
                                        </div>
                                        <button
                                            onClick={() => clearBandFile(band.id as keyof BandFiles)}
                                            className="p-1 hover:bg-red-100 dark:hover:bg-red-900/30 rounded flex-shrink-0"
                                        >
                                            <X className="w-4 h-4 text-red-500" />
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Ready indicator */}
            {(selectedFile || allBandsUploaded) && (
                <div className="mt-4 flex items-center text-sm text-green-600 dark:text-green-400">
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Ready for analysis
                </div>
            )}

            {/* Hidden file input for composite */}
            <input
                id="file-upload"
                type="file"
                className="hidden"
                accept=".tif,.tiff"
                onChange={handleFileInput}
            />
        </div>
    );
};
