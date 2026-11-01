'use client'
export function CheckinButton() {
  function checkin() {
    navigator.geolocation.getCurrentPosition(async (pos) => {
      await fetch('/api/checkin', { method: 'POST', body: JSON.stringify({ lat: pos.coords.latitude, lng: pos.coords.longitude, accuracy: pos.coords.accuracy }) })
    }, undefined, { enableHighAccuracy: true })
  }
  return <button onClick={checkin}>Inizio turno</button>
}
