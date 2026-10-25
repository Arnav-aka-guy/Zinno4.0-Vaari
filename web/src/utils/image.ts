/**
 * Image helper for driver camera uploads.
 * Downscales images to max 1600px on the long side as JPEG for fast transmission
 * over weak in-field cellular connections.
 */
export async function downscaleImage(file: File, maxDimension = 1600): Promise<File> {
  // If not an image, return as is
  if (!file.type.startsWith('image/')) {
    return file;
  }

  return new Promise((resolve) => {
    const img = new Image();
    const objectUrl = URL.createObjectURL(file);

    img.onload = () => {
      URL.revokeObjectURL(objectUrl);
      let { width, height } = img;

      // Check if downscale is needed
      if (width <= maxDimension && height <= maxDimension && file.type === 'image/jpeg') {
        resolve(file);
        return;
      }

      if (width > height) {
        if (width > maxDimension) {
          height = Math.round((height * maxDimension) / width);
          width = maxDimension;
        }
      } else {
        if (height > maxDimension) {
          width = Math.round((width * maxDimension) / height);
          height = maxDimension;
        }
      }

      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        resolve(file);
        return;
      }

      ctx.drawImage(img, 0, 0, width, height);

      canvas.toBlob(
        (blob) => {
          if (!blob) {
            resolve(file);
            return;
          }
          const newName = file.name.replace(/\.[^.]+$/, '') + '.jpg';
          const resizedFile = new File([blob], newName, {
            type: 'image/jpeg',
            lastModified: Date.now(),
          });
          resolve(resizedFile);
        },
        'image/jpeg',
        0.85,
      );
    };

    img.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      resolve(file);
    };

    img.src = objectUrl;
  });
}

/**
 * Capture current GPS position with high accuracy.
 * Never throws or blocks: returns empty object on error, refusal, or HTTP.
 */
export interface GeoCoords {
  lat?: number;
  lon?: number;
  accuracy_m?: number;
}

export function getCurrentPosition(): Promise<GeoCoords> {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve({});
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        resolve({
          lat: Number(pos.coords.latitude.toFixed(6)),
          lon: Number(pos.coords.longitude.toFixed(6)),
          accuracy_m: Math.round(pos.coords.accuracy),
        });
      },
      (_err) => {
        // Location blocked / unavailable / insecure context -> send without position
        resolve({});
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      },
    );
  });
}

/**
 * Format UTC server timestamp to Indian Standard Time (IST).
 */
export function formatIST(isoString?: string | null): string {
  if (!isoString) return '—';
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return (
      new Intl.DateTimeFormat('en-IN', {
        timeZone: 'Asia/Kolkata',
        day: '2-digit',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
      }).format(d) + ' IST'
    );
  } catch {
    return isoString;
  }
}
