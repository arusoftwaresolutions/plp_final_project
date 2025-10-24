import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export default function PovertyMap() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-semibold mb-4">Poverty Map</h1>
      <MapContainer center={[9.03, 38.74]} zoom={12} style={{ height: 400 }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <Marker position={[9.03, 38.74]}>
          <Popup>Example region</Popup>
        </Marker>
      </MapContainer>
    </div>
  );
}
