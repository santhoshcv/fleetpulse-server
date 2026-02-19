'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { GoogleMap, useJsApiLoader, InfoWindow } from '@react-google-maps/api';

export interface DeviceMarker {
  device_id: string;
  lat: number;
  lon: number;
  speed: number;
  heading: number;        // 0–360, 0 = north
  status: 'online' | 'idle' | 'offline';
  last_seen: string | null;
}

interface FleetMapProps {
  devices: DeviceMarker[];
  height?: number;
  focusedDeviceId?: string | null;
  onFocusCleared?: () => void;
}

const STATUS_COLOR: Record<string, string> = {
  online: '#00AEEF',
  idle: '#F5C400',
  offline: '#B3B3B3',
};

const LIBRARIES: ('marker')[] = ['marker'];
const DEFAULT_CENTER = { lat: 25.2, lng: 51.5 };

export default function FleetMap({ devices, height = 500, focusedDeviceId, onFocusCleared }: FleetMapProps) {
  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_KEY!,
    libraries: LIBRARIES,
  });

  const [map, setMap] = useState<google.maps.Map | null>(null);
  const [selectedDevice, setSelectedDevice] = useState<DeviceMarker | null>(null);
  const advancedMarkersRef = useRef<Map<string, google.maps.marker.AdvancedMarkerElement>>(new Map());

  const onLoad = useCallback((mapInstance: google.maps.Map) => {
    setMap(mapInstance);
    if (devices.length > 0) {
      const bounds = new google.maps.LatLngBounds();
      devices.forEach(d => bounds.extend({ lat: d.lat, lng: d.lon }));
      mapInstance.fitBounds(bounds, 60);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const onUnmount = useCallback(() => {
    // Clean up advanced markers
    advancedMarkersRef.current.forEach(m => (m.map = null));
    advancedMarkersRef.current.clear();
    setMap(null);
  }, []);

  // Pan to focused device and open its InfoWindow
  useEffect(() => {
    if (!map || !focusedDeviceId) return;
    const device = devices.find(d => d.device_id === focusedDeviceId);
    if (!device) return;
    map.panTo({ lat: device.lat, lng: device.lon });
    map.setZoom(15);
    setSelectedDevice(device);
  }, [focusedDeviceId]); // eslint-disable-line react-hooks/exhaustive-deps

  // Manage AdvancedMarkerElements whenever map or devices change
  useEffect(() => {
    if (!map || !isLoaded) return;
    if (!google.maps.marker?.AdvancedMarkerElement) return;

    const currentIds = new Set(devices.map(d => d.device_id));
    const existingIds = new Set(advancedMarkersRef.current.keys());

    // Remove markers for devices no longer present
    existingIds.forEach(id => {
      if (!currentIds.has(id)) {
        const m = advancedMarkersRef.current.get(id)!;
        m.map = null;
        advancedMarkersRef.current.delete(id);
      }
    });

    devices.forEach(device => {
      const color = STATUS_COLOR[device.status] ?? '#B3B3B3';
      const isMoving = device.speed > 2;
      const heading = device.heading ?? 0;

      // Navigation triangle arrow — rotates to show heading direction
      // SVG points north (up) at 0°, rotated by heading
      const size = isMoving ? 40 : 32;
      const pin = document.createElement('div');
      pin.style.cssText = `
        cursor: pointer;
        width: ${size}px;
        height: ${size}px;
        transform: rotate(${heading}deg);
        filter: drop-shadow(0 2px 5px rgba(0,0,0,0.45));
        transition: transform 0.4s ease;
      `;
      pin.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg"
          width="${size}" height="${size}"
          viewBox="0 0 40 40">
          <!-- Outer triangle arrow (pointing up = north) -->
          <polygon
            points="20,3 37,37 20,29 3,37"
            fill="${color}"
            stroke="white"
            stroke-width="2.5"
            stroke-linejoin="round"
          />
          ${isMoving
            ? `<!-- Speed dot when moving -->
               <circle cx="20" cy="20" r="3.5" fill="white" opacity="0.9"/>`
            : `<!-- Stationary: hollow centre -->
               <circle cx="20" cy="21" r="4" fill="none" stroke="white" stroke-width="2" opacity="0.7"/>`
          }
        </svg>
      `;

      if (advancedMarkersRef.current.has(device.device_id)) {
        // Update existing marker — position, heading rotation, icon state
        const existing = advancedMarkersRef.current.get(device.device_id)!;
        existing.position = { lat: device.lat, lng: device.lon };
        if (existing.content instanceof HTMLElement) {
          existing.content.style.transform = `rotate(${heading}deg)`;
          existing.content.innerHTML = pin.innerHTML;
        }
      } else {
        // Create new marker
        const marker = new google.maps.marker.AdvancedMarkerElement({
          map,
          position: { lat: device.lat, lng: device.lon },
          content: pin,
          title: device.device_id,
        });

        marker.addListener('gmp-click', () => {
          setSelectedDevice(device);
        });

        advancedMarkersRef.current.set(device.device_id, marker);
      }
    });
  }, [map, devices, isLoaded]);

  const headingLabel = (deg: number) => {
    const dirs = ['N','NE','E','SE','S','SW','W','NW'];
    return dirs[Math.round(deg / 45) % 8];
  };

  const formatTime = (ts: string | null) => {
    if (!ts) return 'Unknown';
    const diff = Math.round((Date.now() - new Date(ts).getTime()) / 1000);
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    return `${Math.floor(diff / 3600)}h ago`;
  };

  if (loadError) {
    return (
      <div style={{ height }} className="flex items-center justify-center rounded-lg bg-muted">
        <p className="text-sm text-destructive">Failed to load Google Maps — check API key</p>
      </div>
    );
  }

  if (!isLoaded) {
    return (
      <div style={{ height }} className="flex items-center justify-center rounded-lg bg-muted">
        <p className="text-sm text-muted-foreground animate-pulse">Loading map...</p>
      </div>
    );
  }

  return (
    <GoogleMap
      mapContainerStyle={{ width: '100%', height: `${height}px`, borderRadius: '8px' }}
      center={DEFAULT_CENTER}
      zoom={11}
      onLoad={onLoad}
      onUnmount={onUnmount}
      options={{
        mapId: 'e54ddf318386cffbaf32cf78',
        mapTypeControl: true,
        streetViewControl: false,
        fullscreenControl: true,
        zoomControl: true,
      }}
    >
      {selectedDevice && (
        <InfoWindow
          position={{ lat: selectedDevice.lat, lng: selectedDevice.lon }}
          onCloseClick={() => { setSelectedDevice(null); onFocusCleared?.(); }}
        >
          <div style={{ fontFamily: 'monospace', minWidth: 160, padding: '4px 2px' }}>
            <div style={{ fontWeight: 'bold', color: '#00AEEF', marginBottom: 6, fontSize: 13 }}>
              {selectedDevice.device_id}
            </div>
            <div style={{ fontSize: 12, color: '#444', lineHeight: '1.7' }}>
              <div>
                Status:{' '}
                <strong style={{ color: STATUS_COLOR[selectedDevice.status] }}>
                  {selectedDevice.status.toUpperCase()}
                </strong>
              </div>
              <div>Speed: {Math.round(selectedDevice.speed)} km/h</div>
              <div>Heading: {selectedDevice.heading ?? 0}° {headingLabel(selectedDevice.heading ?? 0)}</div>
              <div>Lat: {selectedDevice.lat.toFixed(5)}</div>
              <div>Lon: {selectedDevice.lon.toFixed(5)}</div>
              <div>Last seen: {formatTime(selectedDevice.last_seen)}</div>
            </div>
          </div>
        </InfoWindow>
      )}
    </GoogleMap>
  );
}
