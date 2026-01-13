# 🖥️ UHI-LST Frontend

The interactive user interface for the Urban Heat Island and Land Surface Temperature analysis platform.

## 🚀 Built With

- **Framework**: [React 18](https://reactjs.org/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Mapping**: [Leaflet](https://leafletjs.com/) + [React Leaflet](https://react-leaflet.js.org/)
- **Raster Processing**: [GeoTIFF.js](https://geotiffjs.github.io/) + [Plotty](https://github.com/santilland/plotty)
- **State Management**: [Zustand](https://github.com/pmndrs/zustand)
- **Icons**: [Lucide React](https://lucide.dev/)

---

## 🏗️ Project Structure

- `src/components/map/`: Custom mapping layers and Leaflet integrations.
  - `TiffLayer.tsx`: Grayscale thermal band rendering.
  - `CompositeTiffLayer.tsx`: Multi-band (RGB) true color composite rendering.
  - `HeatmapLayer.tsx`: Dynamic visualization of analysis results.
- `src/pages/`: Main application views.
  - `Analysis.tsx`: Data ingestion and processing workspace.
  - `Dashboard.tsx`: Comprehensive results visualization and AI insights.
- `src/stores/`: Global state management for analysis results.
- `src/services/api.ts`: FastAPI backend integration layer.

---

## 🛠️ Development

### Setup
Ensure you have [Node.js](https://nodejs.org/) installed.

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Production Build
```bash
# Build for production
npm run build

# Preview build locally
npm run preview
```

---

## 📐 Design Principles

- **Performance First**: Large raster files are downsampled and processed in-memory for zero-latency map interactions.
- **Glassmorphic UI**: Uses modern translucent layers and subtle gradients for a premium feel.
- **Responsive Layout**: Designed to work on various screen sizes from iPad Pro to Desktop.
- **Real-time Feedback**: Detailed progress bars and live timers for backend processing tasks.

---

## 📝 Type Safety

The project uses a strict TypeScript configuration to ensure data integrity between the FastAPI backend and the React frontend. See `src/types/api.ts` for the shared data models.
