import React, { useState } from 'react';
import { Upload, CheckCircle, X } from 'lucide-react';
import { clsx } from 'clsx';

// Band configuration for Landsat 8/9
const BAND_CONFIG = [
    { id: 'B10', label: 'Band 10 (Thermal)', description: 'TIRS1 - Required for LST' },
    { id: 'B7', label: 'Band 7 (SWIR 2)', description: 'Shortwave Infrared 2' },
    { id: 'B6', label: 'Band 6 (SWIR 1)', description: 'Shortwave Infrared 1 - For NDBI' },
    { id: 'B5', label: 'Band 5 (NIR)', description: 'Near Infrared - For NDVI' },
    { id: 'B4', label: 'Band 4 (Red)', description: 'Red - For NDVI/True Color' },
    { id: 'B3', label: 'Band 3 (Green)', description: 'Green - For True Color/MNDWI' },
    { id: 'B2', label: 'Band 2 (Blue)', description: 'Blue - For True Color' },
];

export interface BandFiles {
    B10: File | null;
    B7: File | null;
    B6: File | null;
    B5: File | null;
    B4: File | null;
    B3: File | null;
    B2: File | null;
}

interface UploadPanelProps {
    onFileSelect: (file: File) => void;
    onBandFilesSelect?: (bands: BandFiles) => void;
    selectedFile: File | null;
    className?: string;
}

export const UploadPanel: React.FC<UploadPanelProps> = ({
    onBandFilesSelect,
    className
}) => {
    const [bandFiles, setBandFiles] = useState<BandFiles>({
        B10: null, B7: null, B6: null, B5: null, B4: null, B3: null, B2: null
    });

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

    // Count uploaded bands
    const uploadedCount = Object.values(bandFiles).filter(f => f !== null).length;
    const totalBands = BAND_CONFIG.length;
    const allBandsUploaded = uploadedCount === totalBands;

    return (
        <div className={clsx("p-3 sm:p-4 bg-white dark:bg-slate-900 rounded-lg shadow-sm border border-slate-200 dark:border-slate-800", className)}>
            <div className="flex items-center justify-between mb-3 sm:mb-4">
                <h3 className="text-base sm:text-lg font-medium text-slate-800 dark:text-slate-100">Data Upload</h3>
                <span className="text-xs text-slate-500 dark:text-slate-400">
                    {uploadedCount}/{totalBands} bands
                </span>
            </div>

            {/* Individual band uploads */}
            <div className="space-y-2">
                {BAND_CONFIG.map((band) => (
                    <div key={band.id}>
                        {!bandFiles[band.id as keyof BandFiles] ? (
                            <label
                                className="flex items-center gap-3 p-2.5 border border-dashed border-slate-300 dark:border-slate-700 rounded-lg cursor-pointer hover:border-primary-400 transition-colors"
                            >
                                <Upload className="w-4 h-4 text-slate-400 flex-shrink-0" />
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
                            <div className="flex items-center gap-3 p-2.5 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                                <div className="flex-1 min-w-0 overflow-hidden">
                                    <p className="text-xs font-semibold text-green-600 dark:text-green-400">
                                        {band.label}
                                    </p>
                                    <p className="text-sm text-slate-700 dark:text-slate-200 truncate" title={bandFiles[band.id as keyof BandFiles]?.name}>
                                        {bandFiles[band.id as keyof BandFiles]?.name}
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
                ))}
            </div>

            {/* Ready indicator */}
            {allBandsUploaded && (
                <div className="mt-4 flex items-center text-sm text-green-600 dark:text-green-400">
                    <CheckCircle className="w-4 h-4 mr-2" />
                    All bands uploaded - Ready for analysis
                </div>
            )}
        </div>
    );
};
