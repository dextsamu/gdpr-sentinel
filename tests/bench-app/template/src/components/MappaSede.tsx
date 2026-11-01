export function MappaSede({ lat, lng }: { lat: number; lng: number }) {
  return <img alt="Mappa della sede" src={`/api/mappa-statica?lat=${lat}&lng=${lng}`} />
}
