import React from 'react';
import { MapContainer, TileLayer, ZoomControl } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icon in Leaflet with React
// (Though we might not use markers immediately, good to have)
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

interface MapViewerProps {
    className?: string;
    center?: [number, number];
    zoom?: number;
    children?: React.ReactNode;
}

export const MapViewer: React.FC<MapViewerProps> = ({
    className = "h-full w-full",
    center = [9.0820, 8.6753], // Default to Nigeria center
    zoom = 6,
    children
}) => {
    return (
        <div className={`relative ${className} z-0`}>
            <MapContainer
                center={center}
                zoom={zoom}
                scrollWheelZoom={true}
                className="h-full w-full rounded-lg"
                zoomControl={false}
                attributionControl={false}
            >
                <TileLayer
                    url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                />
                <TileLayer
                    url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
                />
                <ZoomControl position="bottomright" />
                {children}
            </MapContainer>
        </div>
    );
};
