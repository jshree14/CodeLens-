// Keep backend alive by pinging it every 10 minutes
const BACKEND_URL = import.meta.env.VITE_API_URL || 'https://codelens-backend-lyab.onrender.com';

export function startKeepAlive() {
  // Ping immediately on load
  pingBackend();
  
  // Then ping every 10 minutes
  setInterval(pingBackend, 10 * 60 * 1000);
}

async function pingBackend() {
  try {
    await fetch(`${BACKEND_URL}/api/health`);
    console.log('Backend pinged successfully');
  } catch (error) {
    console.log('Backend ping failed:', error);
  }
}
